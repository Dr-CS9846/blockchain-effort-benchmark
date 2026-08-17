#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""calibrate_drivers.py — COCOMO II Effort-Multiplier (EM) driver calibration on the full
n=46 corpus produced by calibrate_n45.py.

Extends PM = A*KSLOC^E with a multiplicative driver term:
    ln(PM) = ln(A) + E*ln(KSLOC) + sum_i beta_i * X_i
i.e. each binary driver X_i contributes a COCOMO-style effort multiplier exp(beta_i) (>1 =
raises effort, <1 = lowers it), estimated jointly with size rather than assumed from expert
judgment (COCOMO II's original EM values were Delphi-elicited, not fit -- this is the
data-driven analogue, which is itself the methodological contribution here).

STANDING RULE (see 6. Logs/CALIBRATION_FIT_n45_2026-07-20.md): no calibration point is ever
dropped, reweighted, or driver-set changed based on how doing so affects the resulting fit
metrics. To make that binding rather than just declared, every choice below was fixed BEFORE
looking at any fit output:
  1. The full n=46 point set from calibrate_n45.build_points() is used unmodified.
  2. The three driver-set specifications (process/tooling, blockchain-domain, full) are a
     pre-declared taxonomy split (COCOMO EM-analogue vs genuinely novel blockchain-specific
     drivers), not a search over subsets for the one that fits best. All three are always
     reported together, whatever the numbers say.
  3. Regularisation strength (ridge alpha) is chosen by leave-one-out cross-validation, not by
     hand -- and chosen independently inside EVERY outer LOOCV fold (nested CV), so the
     reported predictive metrics cannot leak information from a left-out point into its own
     prediction.
  4. Two dropped columns (has_docs, has_audit) are dropped because they are constant across
     the entire corpus (73/73 rows), not because of any fit result -- a constant column carries
     no information and is mathematically inestimable, independent of what it would do to SA.
  5. ov_CPLX / ov_PVOL are entirely unfilled in the spec (73/73 blank) and are skipped for the
     same reason.

Multi-member points (zgo_AGG's 3 repos, ae_node_AGG's 9 windows) occasionally disagree on a
binary flag across members (4 disagreements out of 460 point x driver cells checked). Resolved
by logical OR ("driver present if ANY member repo/window has it") -- a single rule fixed before
inspecting whether OR or AND would help the fit.
"""
import csv, json, math, sys
import numpy as np
from pathlib import Path
from sklearn.linear_model import RidgeCV

sys.path.insert(0, str(Path(__file__).resolve().parent))
from calibrate_n45 import load_spec, build_points

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"

# Pre-declared taxonomy (fixed before any fit was run) -----------------------------------
DRIVER_SETS = {
    "process_tooling": ["has_ci", "has_tests", "has_docker", "has_lintfmt"],
    "blockchain_domain": ["onchain_runtime", "has_contracts", "dep_consensus",
                           "dep_crosschain", "dep_zkcrypto", "dep_contract"],
}
DRIVER_SETS["full"] = DRIVER_SETS["process_tooling"] + DRIVER_SETS["blockchain_domain"]
ALL_DRIVERS = DRIVER_SETS["full"]

ALPHA_GRID = np.logspace(-2, 3, 60)  # fixed grid, not tuned post hoc


def driver_matrix(spec, points, driver_names):
    """OR-aggregate each binary driver across a point's member rows."""
    ids, rows = [], []
    for pid, (pm, ksloc, members) in points.items():
        vals = []
        for d in driver_names:
            v = max(int(spec[m][d].strip()) for m in members)
            vals.append(v)
        ids.append(pid)
        rows.append(vals)
    return ids, np.array(rows, dtype=float)


def metrics(actual, preds):
    actual = np.asarray(actual, float); preds = np.asarray(preds, float)
    mre = np.abs(actual - preds) / actual
    marp0 = np.mean(np.abs(actual[:, None] - actual[None, :]))
    return dict(SA=round(float(1 - np.mean(np.abs(actual - preds)) / marp0), 3),
                MMRE=round(float(np.mean(mre)), 3), MdMRE=round(float(np.median(mre)), 3),
                PRED25=round(float(np.mean(mre <= .25)), 3), PRED30=round(float(np.mean(mre <= .30)), 3))


def fit_ridge(Xfull, y, alphas=ALPHA_GRID):
    """Standardize on the given sample, fit RidgeCV (cv=None -> efficient leave-one-out
    generalized CV internally), return fitted model + standardization stats."""
    mu = Xfull.mean(axis=0); sd = Xfull.std(axis=0); sd[sd == 0] = 1.0
    Xs = (Xfull - mu) / sd
    model = RidgeCV(alphas=alphas, cv=None)  # cv=None => efficient LOOCV via GCV
    model.fit(Xs, y)
    return model, mu, sd


def nested_loocv(Xfull, y, alphas=ALPHA_GRID):
    """Outer LOOCV over points; alpha re-selected by (inner, efficient) LOOCV on the n-1
    training points at every outer fold, so the left-out point never influences its own
    alpha choice or its own standardization stats."""
    n = len(y); preds = np.zeros(n); chosen = np.zeros(n)
    for i in range(n):
        idx = [j for j in range(n) if j != i]
        model, mu, sd = fit_ridge(Xfull[idx], y[idx], alphas)
        chosen[i] = model.alpha_
        xte = (Xfull[i] - mu) / sd
        pred_log = float(model.predict(xte.reshape(1, -1))[0])
        res = y[idx] - model.predict((Xfull[idx] - mu) / sd)
        preds[i] = math.exp(pred_log) * math.exp(np.var(res) / 2)  # Duan smearing
    return preds, chosen


def run_driver_model(label, ids, pm, lnS, X, driver_names):
    y = np.log(pm)
    Xfull = np.column_stack([lnS, X])  # size + drivers, jointly regularized
    names = ["ln(KSLOC)"] + driver_names

    model, mu, sd = fit_ridge(Xfull, y)
    coefs_std = model.coef_
    # de-standardize to get coefficients in native (ln-effort per unit driver) units
    coefs_native = coefs_std / sd
    intercept_native = model.intercept_ - float(np.sum(coefs_std * mu / sd))

    preds, alphas_chosen = nested_loocv(Xfull, y)
    m = metrics(pm, preds)

    print(f"\n{'='*78}\n{label}  (n={len(pm)}, {len(driver_names)} drivers + size)\n{'='*78}")
    print(f"selected ridge alpha (full-sample GCV): {model.alpha_:.4g}  "
          f"(nested-LOOCV per-fold alphas: median {np.median(alphas_chosen):.4g}, "
          f"range {alphas_chosen.min():.4g}-{alphas_chosen.max():.4g})")
    print(f"{'driver':18} {'coef(ln)':>10} {'EM=exp(coef)':>14}   direction")
    for name, c in zip(names, coefs_native):
        em = math.exp(c)
        direction = "raises effort" if c > 0 else "lowers effort" if c < 0 else "no effect"
        print(f"{name:18} {c:10.4f} {em:14.3f}   {direction}")
    print("LOOCV (nested, nothing leaked): SA %+6.3f  PRED25 %3.0f%%  PRED30 %3.0f%%  "
          "MMRE %4.0f%%  MdMRE %4.0f%%" % (
              m["SA"], 100 * m["PRED25"], 100 * m["PRED30"], 100 * m["MMRE"], 100 * m["MdMRE"]))

    return {
        "n": len(pm), "drivers": driver_names, "alpha_full_sample": round(float(model.alpha_), 4),
        "coefficients_ln": {n: round(float(c), 4) for n, c in zip(names, coefs_native)},
        "effort_multipliers": {n: round(float(math.exp(c)), 4) for n, c in zip(names, coefs_native)},
        "intercept_ln": round(float(intercept_native), 4),
        "loocv": m,
    }


def main():
    spec = load_spec()
    points = build_points(spec)
    ids_order = list(points.keys())
    pm = np.array([points[p][0] for p in ids_order])
    ksloc = np.array([points[p][1] for p in ids_order])
    lnS = np.log(ksloc)

    print(f"Driver calibration on the full corpus: n={len(ids_order)} points "
          f"(same set as calibrate_n45's FULL CORPUS FIT).")
    print(f"Baseline (no drivers, from calibrate_n45.py): free-E OLS E~0.515, "
          f"LOOCV SA+0.354 PRED30 20% MdMRE 72% -- reproduced here as reference, not refit.")

    ids, Xall = driver_matrix(spec, points, ALL_DRIVERS)
    assert ids == ids_order

    results = {}
    for setname, dnames in DRIVER_SETS.items():
        cols = [ALL_DRIVERS.index(d) for d in dnames]
        X = Xall[:, cols]
        # report per-driver prevalence so a zero/near-zero coefficient can be distinguished
        # from "no variation to estimate from" -- computed for transparency, not selection
        prevalence = {d: int(X[:, j].sum()) for j, d in enumerate(dnames)}
        print(f"\ndriver prevalence in this n={len(ids)} corpus (of {len(ids)}): {prevalence}")
        results[setname] = run_driver_model(
            f"RIDGE DRIVER MODEL: {setname}", ids, pm, lnS, X, dnames)

    outpath = REPORTS / "calibrate_drivers_result.json"
    json.dump({"corpus_n": len(ids_order), "point_ids": ids_order, "models": results},
               open(outpath, "w"), indent=2)
    print(f"\nwrote {outpath}")


if __name__ == "__main__":
    main()
