#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
calibrate_bc_cocomo.py
======================
Reproducible calibration of the BC-COCOMO II effort model on the REAL,
delivery-verified Web3 Foundation grants dataset (n = 13).

This script is deliberately self-contained and deterministic. It depends only on
`numpy` and Python's standard library, reads the real benchmark CSV, fits the
model by closed-form maximum likelihood (no random restarts, no hidden state),
and writes its parameters and accuracy metrics to JSON so the result is auditable
and re-runnable in VS Code or anywhere else.

MODEL  (BC-COCOMO II, Equivalent Size Function form)
---------------------------------------------------
    PM_i = C * ( FTE_i^b1 * Cost_K_i^b2 * MS_i^b3 )^{E_i} * smear

where
    Cost_K_i = actual_cost_usd_i / 1000                (cost in $k)
    E_i      = 0.91 + 0.01 * SF_sum_i                  (COCOMO II scale exponent,
                                                        from each project's own 5
                                                        scale-factor values)
    C        = combined multiplier (absorbs COCOMO's A and the ESF coefficient
               alpha, which are NOT separately identifiable from data; see NOTE)
    b1,b2,b3 = ESF elasticities of effort w.r.t. FTE, Cost_K, milestones
    smear    = Duan (1983) non-parametric smearing factor that corrects the
               retransformation bias of exponentiating a log-space fit.

ESTIMATION
----------
Taking logs and folding the known per-project exponent E_i into the regressors
(z_j = E_i * ln x_j) turns the model into an ordinary linear regression in
(ln C, b1, b2, b3).  Under the lognormal error assumption stated in the proof,
ordinary least squares IS the maximum-likelihood estimator, and it has a unique
closed-form solution — so the calibration is exactly reproducible with no
optimiser, no seed, and no convergence ambiguity.

EVALUATION
----------
 * In-sample  : fit on all 13, predict all 13.
 * LOOCV      : leave-one-out cross-validation (refit on 12, predict the 1 held
                out, repeat 13x). This is the honest generalisation estimate for
                a dataset this small.
 * Criteria   : Conte et al. (1986) — MMRE < 0.25 AND PRED(25) >= 0.75.

NOTE ON A vs alpha
------------------
COCOMO writes the multiplier as A and the ESF as alpha*(...). Because the data
only ever sees their product (A * alpha^E), A and alpha cannot be identified
separately from this dataset; only the combined constant C is estimable. Any
document quoting a specific A AND a specific alpha is asserting a convention, not
a data-derived fact. This script reports the identifiable C and is explicit
about it.

Author: prepared for Dr (PhD candidate), 30 May 2026.
"""

import argparse, csv, json, math, os, sys
import numpy as np

# 5 standard COCOMO II scale factors stored in the benchmark CSV
SF_COLS = ["SF_PREC_value", "SF_FLEX_value", "SF_RESL_value",
           "SF_TEAM_value", "SF_PMAT_value"]
B_BASE  = 0.91   # COCOMO II fixed base scale exponent (Boehm et al., 2000)


def load_dataset(path):
    """Read the real benchmark CSV and return arrays of the model variables."""
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            try:
                fte  = float(r["actual_fte"])
                cost = float(r["actual_cost_usd"])
                pm   = float(r["actual_effort_pm"])
                ms   = float(r["milestone_count"])
            except (KeyError, ValueError):
                continue
            if min(fte, cost, pm, ms) <= 0:      # logs require strictly positive
                continue
            sf_sum = sum(float(r[c]) for c in SF_COLS)
            rows.append(dict(name=r.get("project_name", "?"),
                             fte=fte, cost_k=cost / 1000.0, pm=pm, ms=ms,
                             E=B_BASE + 0.01 * sf_sum))
    if not rows:
        sys.exit("No usable rows found in %s" % path)
    return rows


def design_matrix(rows):
    """Build X (with E_i folded into the regressors) and y = ln(PM)."""
    X, y = [], []
    for d in rows:
        E = d["E"]
        X.append([1.0,
                  E * math.log(d["fte"]),
                  E * math.log(d["cost_k"]),
                  E * math.log(d["ms"])])
        y.append(math.log(d["pm"]))
    return np.array(X), np.array(y)


def fit_ols(X, y):
    """Closed-form OLS = MLE under lognormal errors. Returns coefs and Duan smear."""
    coefs, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coefs
    smear = float(np.mean(np.exp(resid)))          # Duan smearing factor
    return coefs, smear, resid


def predict(X, coefs, smear):
    return np.exp(X @ coefs) * smear


def accuracy(actual, pred):
    mre = np.abs(actual - pred) / actual
    return dict(
        MMRE=float(np.mean(mre)),
        MdMRE=float(np.median(mre)),
        PRED25=float(np.mean(mre <= 0.25)),
        PRED30=float(np.mean(mre <= 0.30)),
        per_project_mre=[float(v) for v in mre],
    )


def loocv(rows):
    """Honest leave-one-out CV: refit on n-1, predict the held-out project."""
    X, y = design_matrix(rows)
    n = len(rows)
    actual = np.array([d["pm"] for d in rows])
    preds = np.zeros(n)
    for i in range(n):
        idx = [j for j in range(n) if j != i]
        coefs, smear, _ = fit_ols(X[idx], y[idx])
        preds[i] = math.exp(X[i] @ coefs) * smear
    return actual, preds


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    default_csv = os.path.join(here, "w3f_benchmark_dataset.csv")
    if not os.path.exists(default_csv):
        default_csv = os.path.join(here, "04_cocomo_dataset",
                                   "w3f_benchmark_dataset.csv")
    ap = argparse.ArgumentParser(description="Calibrate BC-COCOMO II on the real W3F dataset.")
    ap.add_argument("--csv", default=default_csv, help="path to w3f_benchmark_dataset.csv")
    ap.add_argument("--outdir", default=here, help="where to write params.json / results.json")
    args = ap.parse_args()

    rows = load_dataset(args.csv)
    n = len(rows)
    X, y = design_matrix(rows)

    # --- in-sample fit (all n) ---
    coefs, smear, resid = fit_ols(X, y)
    lnC, b1, b2, b3 = coefs
    dof = n - len(coefs)
    sigma = float(math.sqrt(float(resid @ resid) / dof))
    insample = accuracy(np.array([d["pm"] for d in rows]), predict(X, coefs, smear))

    # --- LOOCV (honest generalisation) ---
    a_cv, p_cv = loocv(rows)
    cv = accuracy(a_cv, p_cv)

    E_vals = [d["E"] for d in rows]
    params = {
        "model": "BC-COCOMO II (ESF, Cost_K in $k, per-project E from real SF values)",
        "n": n,
        "C_combined_multiplier": float(math.exp(lnC)),
        "ln_C": float(lnC),
        "b1_FTE_elasticity": float(b1),
        "b2_CostK_elasticity": float(b2),
        "b3_MS_elasticity": float(b3),
        "sigma_logspace": sigma,
        "duan_smearing": smear,
        "E_min": float(min(E_vals)), "E_max": float(max(E_vals)),
        "B_base": B_BASE,
        "identifiability_note": ("A and alpha are not separately identifiable; "
                                 "only the combined multiplier C = A*alpha^E is."),
        "estimator": "closed-form OLS in log space = MLE under lognormal errors (deterministic)",
    }
    results = {
        "conte_1986_criteria": {"MMRE_threshold": 0.25, "PRED25_threshold": 0.75},
        "in_sample": insample,
        "loocv": cv,
        "loocv_conte_pass": bool(cv["MMRE"] < 0.25 and cv["PRED25"] >= 0.75),
        "projects": [d["name"] for d in rows],
        "actual_pm": [d["pm"] for d in rows],
        "loocv_predicted_pm": [float(v) for v in p_cv],
    }

    os.makedirs(args.outdir, exist_ok=True)
    with open(os.path.join(args.outdir, "params.json"), "w") as f:
        json.dump(params, f, indent=2)
    with open(os.path.join(args.outdir, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    # --- human-readable report ---
    print("=" * 64)
    print("  BC-COCOMO II  —  REPRODUCIBLE CALIBRATION ON REAL W3F DATA")
    print("=" * 64)
    print(f"  Dataset            : {args.csv}")
    print(f"  Projects (n)       : {n}   (delivery-verified, real costs $10k-$50k)")
    print(f"  Scale exponent E   : {min(E_vals):.4f} .. {max(E_vals):.4f}  (per project, from real SF)")
    print("-" * 64)
    print("  FITTED PARAMETERS (identifiable form)")
    print(f"    C (multiplier)   : {math.exp(lnC):.4f}")
    print(f"    b1  FTE          : {b1:.4f}")
    print(f"    b2  Cost_K       : {b2:.4f}")
    print(f"    b3  Milestones   : {b3:.4f}")
    print(f"    sigma (log)      : {sigma:.4f}")
    print(f"    Duan smearing    : {smear:.4f}")
    print("-" * 64)
    print("  ACCURACY")
    print(f"    In-sample  MMRE  : {insample['MMRE']*100:5.1f}%   PRED(25): {insample['PRED25']*100:5.1f}%   MdMRE: {insample['MdMRE']*100:4.1f}%")
    print(f"    LOOCV      MMRE  : {cv['MMRE']*100:5.1f}%   PRED(25): {cv['PRED25']*100:5.1f}%   MdMRE: {cv['MdMRE']*100:4.1f}%")
    print(f"    LOOCV     PRED(30): {cv['PRED30']*100:5.1f}%")
    print("-" * 64)
    print("  CONTE et al. (1986):  MMRE < 25%  AND  PRED(25) >= 75%")
    verdict = "PASS" if results["loocv_conte_pass"] else "FAIL"
    print(f"    LOOCV verdict    : {verdict}")
    print("=" * 64)
    print("  Per-project LOOCV (actual -> predicted, MRE):")
    for d, pm_hat, mre in zip(rows, p_cv, cv["per_project_mre"]):
        print(f"    {d['name'][:30]:30} {d['pm']:6.2f} -> {pm_hat:6.2f}   {mre*100:5.1f}%")
    print("=" * 64)
    print("  Wrote params.json and results.json to", args.outdir)


if __name__ == "__main__":
    main()
