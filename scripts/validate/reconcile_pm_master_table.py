#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""reconcile_pm_master_table.py — the "PM=PM" ground-truth table.

Every model built this session (baseline size-only, EM ridge, SF ridge, Bayesian-EM,
Bayesian-SF, mixed-effects) has so far been judged on its OWN aggregate metrics report,
computed by its own script, in its own JSON. That is enough to say "this model's LOOCV MMRE
was X%" but it is NOT enough to defend a claim like "model A's E is more trustworthy than
model B's" -- such a claim requires comparing what each model actually PREDICTED, point by
point, against the SAME actual reported PM figures, on the SAME 46 points, under the SAME
honest (nothing-leaked) cross-validation discipline. Until that single side-by-side table
exists, any narrative about which model or which E/EM/SF is "closer to true" has no common
ground to stand on -- actual PM has to be pinned against predicted PM for every model at once,
or the comparison is apples-to-oranges dressed up as a finding.

This script changes NOTHING about any prior fit. It re-runs each already-existing model's own
fitting/CV code (imported, not reimplemented) on the identical n=46 corpus, collects each
model's per-point LOOCV/leave-one-group-out prediction (only the mixed-effects model's own
script previously saved these; the ridge-based scripts only saved aggregate metrics), and
lines them all up against the same actual_pm column. Aggregate metrics are also recomputed
here from the same per-point predictions, as a consistency check against each script's own
previously-reported numbers -- if they don't match exactly, that is itself flagged, not
smoothed over.

No point is dropped, reweighted, or given a different CV fold across models. No model's
regularization/shrinkage/prior is re-tuned here -- every model uses exactly the alpha/prior/
formula selection its own script already used.
"""
import sys, json
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from calibrate_n45 import load_spec, build_points, loocv as n45_loocv
from calibrate_drivers import (DRIVER_SETS, ALL_DRIVERS, driver_matrix, metrics,
                                fit_ridge as em_fit_ridge, nested_loocv as em_nested_loocv)
from calibrate_scale_factors import (fit_ridge as sf_fit_ridge, nested_loocv as sf_nested_loocv)
from calibrate_bayesian_cocomo import (EM_PRIOR, SF_PRIOR, COCOMO_B,
                                        fit_ridge_informative, nested_loocv_informative)
from calibrate_mixed_effects import build_panel_rows, loocv_group

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"

MODEL_ORDER = ["baseline_size_only", "em_full", "sf_full", "bayes_em_full", "bayes_sf_full",
               "mixed_effects"]
MODEL_LABEL = {
    "baseline_size_only": "Baseline (size only, free-E OLS)",
    "em_full":             "EM ridge, full driver set",
    "sf_full":             "SF ridge, full driver set",
    "bayes_em_full":       "Bayesian EM (COCOMO-2000 prior), full set",
    "bayes_sf_full":       "Bayesian SF (COCOMO-2000 prior), full set",
    "mixed_effects":       "Mixed-effects (random intercept, panel-aware)",
}


def main():
    spec = load_spec()
    points = build_points(spec)
    ids_order = list(points.keys())
    pm = np.array([points[p][0] for p in ids_order])
    ksloc = np.array([points[p][1] for p in ids_order])
    lnS = np.log(ksloc)
    y = np.log(pm)
    n = len(ids_order)
    print(f"PM=PM master table: n={n} points (identical corpus, identical id order, every model below).")

    preds = {}

    # 1. baseline -----------------------------------------------------------------------
    preds["baseline_size_only"] = n45_loocv(y, lnS, fixedE=None)

    # 2. EM full-set ----------------------------------------------------------------------
    ids_chk, Xall = driver_matrix(spec, points, ALL_DRIVERS)
    assert ids_chk == ids_order, "point order mismatch: EM driver_matrix vs build_points"
    Xfull_em = np.column_stack([lnS, Xall])
    preds["em_full"], _ = em_nested_loocv(Xfull_em, y)

    # 3. SF full-set ------------------------------------------------------------------------
    lnS_c = lnS - lnS.mean()
    interactions = Xall * lnS_c[:, None]
    Xfull_sf = np.column_stack([lnS_c, interactions])
    preds["sf_full"], _ = sf_nested_loocv(Xfull_sf, y)

    # 4. Bayesian EM full-set (same Xfull_em design, informative prior instead of zero) ------
    prior_mean_em = np.array([COCOMO_B] + [EM_PRIOR[d] for d in ALL_DRIVERS])
    preds["bayes_em_full"], _ = nested_loocv_informative(Xfull_em, y, prior_mean_em)

    # 5. Bayesian SF full-set (same Xfull_sf design, informative prior instead of zero) ------
    prior_mean_sf = np.array([COCOMO_B] + [SF_PRIOR[d] for d in ALL_DRIVERS])
    preds["bayes_sf_full"], _ = nested_loocv_informative(Xfull_sf, y, prior_mean_sf)

    # 6. Mixed-effects (leave-one-group-out; group ids ARE the collapsed point ids) ----------
    df = build_panel_rows(spec, points)
    ids_mixed, actual_mixed, pred_mixed = loocv_group(df)
    mixed_by_id = dict(zip(ids_mixed, pred_mixed))
    assert set(mixed_by_id) == set(ids_order), "mixed-effects group ids don't match point ids"
    preds["mixed_effects"] = np.array([mixed_by_id[pid] for pid in ids_order])

    # ---- recomputed aggregate metrics, as a consistency check against each script's own ----
    print(f"\n{'='*90}\nRecomputed aggregate metrics (should match each script's own reported numbers)\n{'='*90}")
    agg = {}
    for mname in MODEL_ORDER:
        m = metrics(pm, preds[mname])
        agg[mname] = m
        print(f"{MODEL_LABEL[mname]:48} SA %+6.3f  MMRE %4.0f%%  MdMRE %4.0f%%  PRED25 %3.0f%%  PRED30 %3.0f%%" % (
            m["SA"], 100*m["MMRE"], 100*m["MdMRE"], 100*m["PRED25"], 100*m["PRED30"]))

    # ---- per-point table: actual PM vs every model's predicted PM, MRE, and the winner ----
    mre = {mname: np.abs(pm - preds[mname]) / pm for mname in MODEL_ORDER}
    winner_idx = np.argmin(np.column_stack([mre[m] for m in MODEL_ORDER]), axis=1)
    winner = [MODEL_ORDER[i] for i in winner_idx]
    win_counts = {mname: int(np.sum(np.array(winner) == mname)) for mname in MODEL_ORDER}

    print(f"\n{'='*90}\nPer-point closest-model win counts (of {n} points)\n{'='*90}")
    for mname in MODEL_ORDER:
        print(f"  {MODEL_LABEL[mname]:48} {win_counts[mname]:3d} points")

    rows = []
    for i, pid in enumerate(ids_order):
        row = {"id": pid, "actual_pm": round(float(pm[i]), 3),
               "winner": winner[i]}
        for mname in MODEL_ORDER:
            row[f"pred_{mname}"] = round(float(preds[mname][i]), 3)
            row[f"mre_{mname}"] = round(float(mre[mname][i]), 4)
        rows.append(row)

    out = {"n": n, "point_ids": ids_order, "models": MODEL_LABEL,
           "aggregate_metrics_recomputed": agg, "win_counts": win_counts,
           "per_point": rows}
    outpath = REPORTS / "reconcile_pm_master_table_result.json"
    json.dump(out, open(outpath, "w"), indent=2)
    print(f"\nwrote {outpath}")

    # ---- worst-disagreement points: where models diverge most from each other -------------
    pred_matrix = np.column_stack([preds[m] for m in MODEL_ORDER])
    spread = pred_matrix.max(axis=1) / np.maximum(pred_matrix.min(axis=1), 1e-9)
    order = np.argsort(-spread)[:8]
    print(f"\n{'='*90}\n8 points where models disagree most (max predicted PM / min predicted PM)\n{'='*90}")
    print(f"{'id':28} {'actual_pm':>10} {'spread(x)':>10}   per-model predicted PM")
    for i in order:
        pid = ids_order[i]
        preds_str = "  ".join(f"{MODEL_LABEL[m].split(',')[0][:14]:14}={preds[m][i]:8.2f}" for m in MODEL_ORDER)
        print(f"{pid:28} {pm[i]:10.2f} {spread[i]:9.2f}x   {preds_str}")


if __name__ == "__main__":
    main()
