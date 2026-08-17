#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""calibrate_mixed_effects.py — random-intercept linear mixed-effects model over the corpus's
panel structure, instead of collapsing dependent windows to a single summed point.

Every prior script in this project (calibrate_n45.py onward) uses one design decision to avoid
pseudo-replication: 4 projects with multiple independently-reported time windows (ae_node: 9
windows, aeternity_sdk: 7, ae_mdw: 4, reactivedot: 6 -- 26 raw rows total) are COLLAPSED into a
single point per project (PM summed, KSLOC summed) before any fit. That is correct for avoiding
pseudo-replication under ordinary OLS (which assumes independent errors), but it also throws
away real information: how much a single project's own effort/size relationship varies across
its own windows, versus how much it varies from OTHER projects. A mixed-effects (hierarchical)
model uses that information instead of discarding it, while still not pseudo-replicating --
each window is modeled as `y_ig = (lnA + u_g) + E*lnS_ig + eps_ig`, u_g ~ N(0, sigma_u^2) a
per-project random intercept, eps_ig ~ N(0, sigma_eps^2) residual noise. The random intercept
absorbs each project's own unobserved baseline (team, domain, coding style), so the model does
not treat correlated windows as independent evidence about the corpus-wide slope E -- exactly
what pseudo-replication concerns require, achieved through the model's error structure instead
of through discarding data.

SUM_SCOPE_GROUPS (zgo_AGG, aeknow_AGG, ink_analyzer_779_AGG) are NOT ungrouped here: those are
one reported PM figure spanning several repos with no per-repo split in the source data, so
there is nothing to ungroup -- they remain single collapsed rows, each its own singleton group,
exactly as in every prior script. This is a structural fact already documented in
calibrate_n45.build_points(), not a new judgment call made for this script.

Fitting: statsmodels MixedLM, REML. Cross-validation: leave-one-GROUP-out (46 folds, matching
the point-level n=46 granularity every other script in this project reports at), refitting the
model from scratch each fold, predicting the held-out group by its FIXED effects only (a new
group's random intercept is by definition unobserved -- population-average / marginal
prediction is the standard, correct way to evaluate out-of-sample generalization for a mixed
model), with a Duan-style smearing correction using the TOTAL marginal variance
(sigma_u^2 + sigma_eps^2, not residual variance alone, since a new group's own intercept
deviation is exactly the part of the total variance we cannot observe for it). A held-out
panel group's several rows are summed to a single predicted total PM before scoring, mirroring
the same summing rule build_points() already uses for the actual data -- so every fold still
scores exactly one point, keeping this comparable to every previous script's n=46 metrics.
"""
import sys, json
import numpy as np
import pandas as pd
from pathlib import Path
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from calibrate_n45 import load_spec, build_points, load_size, WINDOW_COLLAPSE_GROUPS, metrics

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"


def build_panel_rows(spec, points):
    panel_names = set(WINDOW_COLLAPSE_GROUPS)
    rows = []; zero_ks_dropped = []
    for gname, pred in WINDOW_COLLAPSE_GROUPS.items():
        for m in sorted(pid for pid in spec if pred(pid)):
            ks = load_size(m)
            # A raw window can legitimately measure ksloc=0 under this pipeline's known,
            # disclosed gap (Erlang/.erl is not in dissect_pilot.py's SRC_EXTS, so a window whose
            # only changes are .erl files reads as zero size). ln(0) is undefined and breaks any
            # raw-window-level fit (mixed-effects, within/between decomposition); such windows
            # are mathematically unusable there and are excluded from THIS raw-panel dataframe
            # only. They are NOT excluded from the point-level corpus -- their (non-zero, since
            # summed with sibling windows) collapsed-point KSLOC still feeds every other model.
            if ks <= 0:
                zero_ks_dropped.append(m); continue
            rows.append({"group": gname, "member": m,
                         "pm": float(spec[m]["reported_pm"]), "ksloc": ks})
    for pid, (pm, ksloc, _members) in points.items():
        if pid in panel_names:
            continue
        rows.append({"group": pid, "member": pid, "pm": pm, "ksloc": ksloc})
    if zero_ks_dropped:
        print(f"  [disclosed] {len(zero_ks_dropped)} raw window(s) excluded from panel-level "
              f"analysis only (ksloc=0, undefined under log-transform): {zero_ks_dropped}")
    df = pd.DataFrame(rows)
    df["y"] = np.log(df["pm"]); df["lnS"] = np.log(df["ksloc"])
    return df


def fit_mixedlm(df):
    model = smf.mixedlm("y ~ lnS", df, groups=df["group"])
    return model.fit(reml=True)


def loocv_group(df):
    groups = df["group"].unique()
    ids, actual_totals, pred_totals = [], [], []
    for g in groups:
        train, test = df[df["group"] != g], df[df["group"] == g]
        r = fit_mixedlm(train)
        b0, b1 = r.fe_params["Intercept"], r.fe_params["lnS"]
        sigma_u2 = float(r.cov_re.iloc[0, 0]); sigma_eps2 = float(r.scale)
        total_var = sigma_u2 + sigma_eps2
        pred_pm = np.exp(b0 + b1 * test["lnS"]) * np.exp(total_var / 2)  # Duan-style smearing
        ids.append(g)
        actual_totals.append(float(test["pm"].sum()))
        pred_totals.append(float(pred_pm.sum()))
    return ids, np.array(actual_totals), np.array(pred_totals)


def main():
    spec = load_spec()
    points = build_points(spec)
    df = build_panel_rows(spec, points)

    n_groups = df["group"].nunique()
    print(f"Panel dataset: {len(df)} raw observations in {n_groups} groups "
          f"(4 multi-window projects ungrouped to {sum(len(df[df.group==g]) for g in WINDOW_COLLAPSE_GROUPS)} rows, "
          f"{n_groups - len(WINDOW_COLLAPSE_GROUPS)} singleton groups unchanged from the collapsed corpus).")
    print("Reference (already on record, same n=44 points, plain OLS, no panel structure used):")
    print("  baseline free-E OLS: E~0.523  LOOCV SA+0.371 MMRE 220% MdMRE 75% PRED30 23%")

    result = fit_mixedlm(df)
    b0, b1 = result.fe_params["Intercept"], result.fe_params["lnS"]
    se0, se1 = result.bse_fe["Intercept"], result.bse_fe["lnS"]
    sigma_u2 = float(result.cov_re.iloc[0, 0]); sigma_eps2 = float(result.scale)
    icc = sigma_u2 / (sigma_u2 + sigma_eps2)

    print(f"\n{'='*78}\nFULL-SAMPLE MIXED MODEL (REML, random intercept by project)\n{'='*78}")
    print(f"fixed effect  ln(A) = {b0:.4f} (se {se0:.4f})   A = {np.exp(b0):.4f}")
    print(f"fixed effect  E     = {b1:.4f} (se {se1:.4f})   [95%% CI {b1-1.96*se1:.4f}, {b1+1.96*se1:.4f}]")
    print(f"variance components: between-project sigma_u^2={sigma_u2:.4f}  "
          f"within-project sigma_eps^2={sigma_eps2:.4f}")
    print(f"ICC (fraction of total variance that is between-project): {icc:.3f}")
    print(f"  -> {icc:.0%} of the corpus's unexplained variance is systematic per-project "
          f"differences; {1-icc:.0%} is window-to-window noise within the same project.")

    ids, actual, pred = loocv_group(df)
    m = metrics(actual, pred)
    print(f"\nLeave-one-GROUP-out CV ({n_groups} folds, refit each time, marginal/fixed-effects-only "
          f"prediction for the held-out group, summed to one point per fold):")
    print("  SA %+6.3f  PRED25 %3.0f%%  PRED30 %3.0f%%  MMRE %4.0f%%  MdMRE %4.0f%%" % (
        m["SA"], 100*m["PRED25"], 100*m["PRED30"], 100*m["MMRE"], 100*m["MdMRE"]))

    outpath = REPORTS / "calibrate_mixed_effects_result.json"
    json.dump({
        "n_observations": len(df), "n_groups": int(n_groups),
        "fixed_effects": {"lnA": round(float(b0), 4), "E": round(float(b1), 4),
                           "E_se": round(float(se1), 4),
                           "E_95ci": [round(float(b1 - 1.96*se1), 4), round(float(b1 + 1.96*se1), 4)]},
        "variance_components": {"sigma_u2_between_project": round(sigma_u2, 4),
                                 "sigma_eps2_within_project": round(sigma_eps2, 4),
                                 "ICC": round(float(icc), 4)},
        "loocv_group_level": m,
        "loocv_group_predictions": {g: {"actual_pm": a, "pred_pm": p}
                                     for g, a, p in zip(ids, actual.tolist(), pred.tolist())},
    }, open(outpath, "w"), indent=2)
    print(f"\nwrote {outpath}")


if __name__ == "__main__":
    main()
