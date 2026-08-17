#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""calibrate_bayesian_cocomo.py — Bayesian shrinkage toward COCOMO II.2000's OWN published
EM/SF table values, instead of the plain-ridge shrink-toward-zero used in calibrate_drivers.py
and calibrate_scale_factors.py.

Ridge regression is MAP estimation under a Gaussian prior N(0, tau^2) on each coefficient.
This script generalizes that to a non-zero-mean Gaussian prior N(mu_j, tau^2), where mu_j is
NOT a free parameter chosen to fit this corpus -- it is COCOMO II.2000's own literature value
for the nearest cost-driver category, published in 2000 from a completely different (non-
blockchain) dataset (Boehm et al., "COCOMO II Model Definition Manual" v2.1). Mathematically
this is a simple shift-of-origin: fit plain (zero-mean-prior) ridge on (y - X@mu), then add mu
back. Implementation and regularization discipline (RidgeCV alpha, nested LOOCV) are otherwise
identical to the two prior scripts -- only the shrinkage TARGET changes.

Why this is a legitimate methodological step, not a repeat of the earlier mistake: mu is fixed
BEFORE any fit is run, from an external published source, using a category mapping declared in
this docstring, not searched over. The corpus's own points, driver taxonomy (process_tooling /
blockchain_domain / full) and metrics are unchanged from the prior two scripts.

--- COCOMO II.2000 published values used (Boehm et al. 2000; cross-verified 2026-07-20 against
    two independent secondary sources: github.com/ai-se/cocomo/blob/master/doc/cocomo.md, and
    an independent web search hit reproducing the CPLX row) ---
  TOOL (use of software tools) EM: VL 1.17 / L 1.09 / N 1.00 / H 0.90 / VH 0.78
  CPLX (product complexity)   EM: VL 0.73 / L 0.87 / N 1.00 / H 1.17 / VH 1.34 / XH 1.74
  PMAT (process maturity)     SF: VL 7.80 / L 6.24 / N 4.68 / H 3.12 / VH 1.56
  PREC (precedentedness)      SF: VL 6.20 / L 4.96 / N 3.72 / H 2.48 / VH 1.24
  B   (nominal scale-factor baseline exponent, COCOMO II.2000): 0.91

--- pre-declared driver -> COCOMO category mapping (fixed before any Bayesian fit was run) ---
  process_tooling (has_ci, has_tests, has_docker, has_lintfmt): 4 instances of ONE construct --
  automated build/QA tooling investment -- mapped to COCOMO's own TOOL definition ("integrated
  into the process via data and control coupling"). Given a shared prior: TOOL "High" (0.90) for
  the EM version; PMAT "High" (3.12) vs Nominal (4.68) delta for the SF version (good tooling
  read as a process-maturity signal).
  blockchain_domain (onchain_runtime, has_contracts, dep_consensus, dep_crosschain,
  dep_zkcrypto, dep_contract): 6 instances of elevated technical complexity (consensus
  algorithms, cross-chain interop, ZK cryptography, on-chain execution constraints, contract
  state management) -- mapped to COCOMO's CPLX definition (control / compute / device-dependent
  / data-management operations). Given a shared prior: CPLX "High" (1.17) for the EM version;
  PREC "Low" (4.96) vs Nominal (3.72) delta for the SF version (novel technical domains read as
  less precedented than an average project).
These are honest, coarse, best-effort analogies across a genuine taxonomy mismatch (COCOMO's
17 EM + 5 SF categories were never designed for blockchain-specific technical dependencies) --
not a precise expert re-rating of this corpus. That imprecision is the point being tested: how
much does the data pull away from a 26-year-old, non-blockchain-elicited prior?
"""
import json, math, sys
import numpy as np
from pathlib import Path
from sklearn.linear_model import RidgeCV

sys.path.insert(0, str(Path(__file__).resolve().parent))
from calibrate_n45 import load_spec, build_points
from calibrate_drivers import DRIVER_SETS, ALL_DRIVERS, driver_matrix, metrics, ALPHA_GRID

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"

COCOMO_B = 0.91
_TOOL_HIGH, _CPLX_HIGH = math.log(0.90), math.log(1.17)
_PMAT_DELTA, _PREC_DELTA = 0.01 * (3.12 - 4.68), 0.01 * (4.96 - 3.72)

EM_PRIOR = {d: _TOOL_HIGH for d in DRIVER_SETS["process_tooling"]}
EM_PRIOR.update({d: _CPLX_HIGH for d in DRIVER_SETS["blockchain_domain"]})
SF_PRIOR = {d: _PMAT_DELTA for d in DRIVER_SETS["process_tooling"]}
SF_PRIOR.update({d: _PREC_DELTA for d in DRIVER_SETS["blockchain_domain"]})


def fit_ridge_informative(Xfull, y, prior_mean, alphas=ALPHA_GRID):
    y_adj = y - Xfull @ prior_mean
    mu = Xfull.mean(axis=0); sd = Xfull.std(axis=0); sd[sd == 0] = 1.0
    Xs = (Xfull - mu) / sd
    model = RidgeCV(alphas=alphas, cv=None)
    model.fit(Xs, y_adj)
    coefs_native = prior_mean + model.coef_ / sd
    return model, mu, sd


def nested_loocv_informative(Xfull, y, prior_mean, alphas=ALPHA_GRID):
    n = len(y); preds = np.zeros(n); chosen = np.zeros(n)
    for i in range(n):
        idx = [j for j in range(n) if j != i]
        model, mu, sd = fit_ridge_informative(Xfull[idx], y[idx], prior_mean, alphas)
        chosen[i] = model.alpha_
        y_adj_train = y[idx] - Xfull[idx] @ prior_mean
        xte = (Xfull[i] - mu) / sd
        pred_dev = float(model.predict(xte.reshape(1, -1))[0])
        pred_log = pred_dev + float(Xfull[i] @ prior_mean)
        res = y_adj_train - model.predict((Xfull[idx] - mu) / sd)
        preds[i] = math.exp(pred_log) * math.exp(np.var(res) / 2)
    return preds, chosen


def run_em_bayesian(pm, lnS, X, driver_names):
    y = np.log(pm)
    Xfull = np.column_stack([lnS, X])
    names = ["ln(KSLOC)"] + driver_names
    prior_mean = np.array([COCOMO_B] + [EM_PRIOR[d] for d in driver_names])

    model, mu, sd = fit_ridge_informative(Xfull, y, prior_mean)
    coefs_native = prior_mean + model.coef_ / sd
    preds, alphas_chosen = nested_loocv_informative(Xfull, y, prior_mean)
    m = metrics(pm, preds)

    print(f"\n{'-'*78}\nEM, Bayesian shrinkage toward COCOMO II.2000 (n={len(pm)}, "
          f"{len(driver_names)} drivers)\n{'-'*78}")
    print(f"alpha (full-sample GCV): {model.alpha_:.4g}  "
          f"(nested per-fold median {np.median(alphas_chosen):.4g})")
    print(f"{'driver':18} {'prior mu':>10} {'posterior':>10} {'moved by':>10}   EM=exp(post)")
    for name, mu_j, post in zip(names, prior_mean, coefs_native):
        print(f"{name:18} {mu_j:10.4f} {post:10.4f} {post-mu_j:10.4f}   {math.exp(post):.3f}")
    print("LOOCV: SA %+6.3f  PRED25 %3.0f%%  PRED30 %3.0f%%  MMRE %4.0f%%  MdMRE %4.0f%%" % (
        m["SA"], 100*m["PRED25"], 100*m["PRED30"], 100*m["MMRE"], 100*m["MdMRE"]))

    return {"n": len(pm), "drivers": driver_names, "alpha": round(float(model.alpha_), 4),
            "prior_mean": {n: round(float(v), 4) for n, v in zip(names, prior_mean)},
            "posterior_mean": {n: round(float(v), 4) for n, v in zip(names, coefs_native)},
            "loocv": m}


def run_sf_bayesian(pm, lnS_c, X, driver_names):
    y = np.log(pm)
    interactions = X * lnS_c[:, None]
    Xfull = np.column_stack([lnS_c, interactions])
    names = ["ln(KSLOC)_centered [B]"] + [f"{d} x lnS [SF]" for d in driver_names]
    prior_mean = np.array([COCOMO_B] + [SF_PRIOR[d] for d in driver_names])

    model, mu, sd = fit_ridge_informative(Xfull, y, prior_mean)
    coefs_native = prior_mean + model.coef_ / sd
    preds, alphas_chosen = nested_loocv_informative(Xfull, y, prior_mean)
    m = metrics(pm, preds)

    print(f"\n{'-'*78}\nSF, Bayesian shrinkage toward COCOMO II.2000 (n={len(pm)}, "
          f"{len(driver_names)} scale factors)\n{'-'*78}")
    print(f"alpha (full-sample GCV): {model.alpha_:.4g}  "
          f"(nested per-fold median {np.median(alphas_chosen):.4g})")
    print(f"{'driver':22} {'prior mu':>10} {'posterior':>10} {'moved by':>10}")
    for name, mu_j, post in zip(names, prior_mean, coefs_native):
        print(f"{name:22} {mu_j:10.4f} {post:10.4f} {post-mu_j:10.4f}")
    print("LOOCV: SA %+6.3f  PRED25 %3.0f%%  PRED30 %3.0f%%  MMRE %4.0f%%  MdMRE %4.0f%%" % (
        m["SA"], 100*m["PRED25"], 100*m["PRED30"], 100*m["MMRE"], 100*m["MdMRE"]))

    return {"n": len(pm), "drivers": driver_names, "alpha": round(float(model.alpha_), 4),
            "prior_mean": {n: round(float(v), 4) for n, v in zip(names, prior_mean)},
            "posterior_mean": {n: round(float(v), 4) for n, v in zip(names, coefs_native)},
            "loocv": m}


def main():
    spec = load_spec()
    points = build_points(spec)
    ids_order = list(points.keys())
    pm = np.array([points[p][0] for p in ids_order])
    ksloc = np.array([points[p][1] for p in ids_order])
    lnS = np.log(ksloc)
    lnS_c = lnS - lnS.mean()

    print(f"Bayesian (COCOMO-II.2000-informed prior) calibration, n={len(ids_order)}, "
          f"identical corpus to prior scripts.")
    print("References (zero-prior results already on record):")
    print("  baseline (size only):      SA+0.354 MMRE 226% MdMRE 72% PRED30 20%")
    print("  EM zero-shrink, full set:  SA+0.418 MMRE 130% MdMRE 66% PRED30 33%")
    print("  SF zero-shrink, full set:  SA+0.392 MMRE 248% MdMRE 71% PRED30 22%")

    ids, Xall = driver_matrix(spec, points, ALL_DRIVERS)
    assert ids == ids_order

    results = {"em": {}, "sf": {}}
    for setname, dnames in DRIVER_SETS.items():
        cols = [ALL_DRIVERS.index(d) for d in dnames]
        X = Xall[:, cols]
        print(f"\n=== driver set: {setname} ===")
        results["em"][setname] = run_em_bayesian(pm, lnS, X, dnames)
        results["sf"][setname] = run_sf_bayesian(pm, lnS_c, X, dnames)

    outpath = REPORTS / "calibrate_bayesian_cocomo_result.json"
    json.dump({"corpus_n": len(ids_order), "point_ids": ids_order,
               "cocomo_priors_used": {"TOOL_high": 0.90, "CPLX_high": 1.17, "PMAT_high": 3.12,
                                       "PMAT_nominal": 4.68, "PREC_low": 4.96,
                                       "PREC_nominal": 3.72, "B": COCOMO_B},
               "models": results},
              open(outpath, "w"), indent=2)
    print(f"\nwrote {outpath}")


if __name__ == "__main__":
    main()
