#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""calibrate_scale_factors.py — COCOMO II Scale-Factor (SF) driver calibration on the same
full n=46 corpus as calibrate_drivers.py.

COCOMO II has two distinct driver mechanisms and this project has so far only fit one of them:
  - Effort Multipliers (EM, calibrate_drivers.py): a driver shifts the LEVEL of effort at any
    size -- ln(PM) += beta_i * X_i, a main effect independent of ln(KSLOC).
  - Scale Factors (SF, this script): a driver shifts how effort SCALES with size --
    ln(PM) += w_j * (X_j * ln(KSLOC)), an interaction with size, which is exactly how COCOMO II
    defines it: E = B + 0.01*sum(SF_j), so ln(PM) = ln(A) + E*ln(KSLOC) = ln(A) + B*ln(KSLOC) +
    0.01*sum(SF_j)*ln(KSLOC). A driver that raises E makes the project suffer DISECONOMIES of
    scale (cost grows faster than linear in size); a driver that lowers E gives ECONOMIES of
    scale. This is a structurally different claim from an EM and requires a different design
    matrix (interaction terms, not main-effect terms) -- conflating the two would silently fit
    an EM while claiming to fit an SF.

ln(KSLOC) is mean-centered before building interaction terms (lnS_c = lnS - mean(lnS)): this
makes the fitted lnS_c coefficient B interpretable as "the exponent at the corpus's mean
size" and decorrelates main/interaction terms that would otherwise be severely collinear
(standard practice for interaction models) -- centering was decided before any fit was run,
not selected after inspecting which centering flattered the result.

Methodology (ridge with nested nested-LOOCV alpha selection, the 3 pre-declared driver-set
taxonomies, no point ever dropped or reweighted based on fit outcome) is copied verbatim from
calibrate_drivers.py's EM script -- same corpus, same regularization discipline, same taxonomy
-- so this is a like-for-like comparison of the two mechanisms, not a differently-tuned model
built to look better. See that script's docstring and 6. Logs/CALIBRATION_FIT_n45_2026-07-20.md
for the full pre-registration rationale.
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


def fit_ridge(Xfull, y, alphas=ALPHA_GRID):
    mu = Xfull.mean(axis=0); sd = Xfull.std(axis=0); sd[sd == 0] = 1.0
    Xs = (Xfull - mu) / sd
    model = RidgeCV(alphas=alphas, cv=None)
    model.fit(Xs, y)
    return model, mu, sd


def nested_loocv(Xfull, y, alphas=ALPHA_GRID):
    n = len(y); preds = np.zeros(n); chosen = np.zeros(n)
    for i in range(n):
        idx = [j for j in range(n) if j != i]
        model, mu, sd = fit_ridge(Xfull[idx], y[idx], alphas)
        chosen[i] = model.alpha_
        xte = (Xfull[i] - mu) / sd
        pred_log = float(model.predict(xte.reshape(1, -1))[0])
        res = y[idx] - model.predict((Xfull[idx] - mu) / sd)
        preds[i] = math.exp(pred_log) * math.exp(np.var(res) / 2)
    return preds, chosen


def run_sf_model(label, pm, lnS_c, X, driver_names):
    y = np.log(pm)
    interactions = X * lnS_c[:, None]  # X_j * lnS_c -- the SF design, NOT X_j alone
    Xfull = np.column_stack([lnS_c, interactions])
    names = ["ln(KSLOC)_centered [B]"] + [f"{d} x lnS  [SF]" for d in driver_names]

    model, mu, sd = fit_ridge(Xfull, y)
    coefs_std = model.coef_
    coefs_native = coefs_std / sd
    B = coefs_native[0]
    sf_weights = coefs_native[1:]

    preds, alphas_chosen = nested_loocv(Xfull, y)
    m = metrics(pm, preds)

    print(f"\n{'='*78}\n{label}  (n={len(pm)}, {len(driver_names)} scale factors)\n{'='*78}")
    print(f"selected ridge alpha (full-sample GCV): {model.alpha_:.4g}  "
          f"(nested-LOOCV per-fold alphas: median {np.median(alphas_chosen):.4g}, "
          f"range {alphas_chosen.min():.4g}-{alphas_chosen.max():.4g})")
    print(f"B (exponent at mean size, driver-absent baseline): {B:.4f}")
    print(f"{'driver (as SF)':22} {'w_j (ln)':>10} {'E at X_j=1':>12}   direction")
    for name, w in zip(driver_names, sf_weights):
        e_at_1 = B + w
        direction = "diseconomy (E up)" if w > 0 else "economy (E down)" if w < 0 else "no effect"
        print(f"{name:22} {w:10.4f} {e_at_1:12.4f}   {direction}")
    print("LOOCV (nested, nothing leaked): SA %+6.3f  PRED25 %3.0f%%  PRED30 %3.0f%%  "
          "MMRE %4.0f%%  MdMRE %4.0f%%" % (
              m["SA"], 100 * m["PRED25"], 100 * m["PRED30"], 100 * m["MMRE"], 100 * m["MdMRE"]))

    return {
        "n": len(pm), "drivers": driver_names, "alpha_full_sample": round(float(model.alpha_), 4),
        "B_exponent_at_mean_size": round(float(B), 4),
        "sf_weights_ln": {d: round(float(w), 4) for d, w in zip(driver_names, sf_weights)},
        "implied_E_if_driver_present": {d: round(float(B + w), 4) for d, w in zip(driver_names, sf_weights)},
        "loocv": m,
    }


def main():
    spec = load_spec()
    points = build_points(spec)
    ids_order = list(points.keys())
    pm = np.array([points[p][0] for p in ids_order])
    ksloc = np.array([points[p][1] for p in ids_order])
    lnS = np.log(ksloc)
    lnS_c = lnS - lnS.mean()

    print(f"Scale-Factor calibration on the full corpus: n={len(ids_order)} points "
          f"(identical point set to calibrate_drivers.py and calibrate_n45's FULL CORPUS FIT).")
    print(f"Baseline (no scale factors, size only, from calibrate_n45.py): free-E OLS E~0.515, "
          f"LOOCV SA+0.354 MMRE 226% MdMRE 72% PRED30 20%.")
    print(f"EM-only reference (calibrate_drivers.py, full driver set): LOOCV SA+0.418 "
          f"MMRE 130% MdMRE 66% PRED30 33%.")

    ids, Xall = driver_matrix(spec, points, ALL_DRIVERS)
    assert ids == ids_order

    results = {}
    for setname, dnames in DRIVER_SETS.items():
        cols = [ALL_DRIVERS.index(d) for d in dnames]
        X = Xall[:, cols]
        prevalence = {d: int(X[:, j].sum()) for j, d in enumerate(dnames)}
        print(f"\ndriver prevalence in this n={len(ids)} corpus (of {len(ids)}): {prevalence}")
        results[setname] = run_sf_model(f"RIDGE SCALE-FACTOR MODEL: {setname}", pm, lnS_c, X, dnames)

    outpath = REPORTS / "calibrate_scale_factors_result.json"
    json.dump({"corpus_n": len(ids_order), "point_ids": ids_order, "models": results},
               open(outpath, "w"), indent=2)
    print(f"\nwrote {outpath}")


if __name__ == "__main__":
    main()
