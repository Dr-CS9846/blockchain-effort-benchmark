#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""calibrate_n45.py — PM = A*KSLOC^E on the full corpus (71 spec rows), with dependent
windows collapsed into single independent points per the project's own documented rule
("N dependent windows collapse to one aggregate point, no pseudo-replication" — established
2026-07-03 for the SDK and ae_mdw panels; applied here CONSISTENTLY to every structurally
identical group: ae_node, reactivedot, zgo, aeknow).

Reads size from reports/dissect_<project_id>.json (equivalent_ksloc field, reuse-adjusted)
and reported_pm from data/calibration/pilots_cocomo.csv. Fitting methodology (fit_full,
loocv, metrics incl. Duan smearing) is reused VERBATIM from calibrate_actual.py for direct
comparability with the established n=17 headline.

Also reports the NAIVE (uncollapsed, all-71-rows-as-independent) fit as an explicit contrast,
to make the pseudo-replication correction's impact visible rather than silently applied.
"""
import csv, json, math, sys
import numpy as np
from scipy.stats import theilslopes
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "data/calibration/pilots_cocomo.csv"
REPORTS = ROOT / "reports"

# ---- point-collapsing groups (see audit reasoning in session log) ----
WINDOW_COLLAPSE_GROUPS = {
    "ae_node_AGG":       lambda pid: pid.startswith("ae_node_"),
    "aeternity_sdk_AGG": lambda pid: pid.startswith("aeternity_sdk_") and pid != "aeternity_sdk_q1_2025",
    "ae_mdw_AGG":        lambda pid: pid.startswith("ae_mdw_"),
    "reactivedot_AGG":   lambda pid: pid.startswith("reactivedot_"),
}
# same-scope-multi-repo groups: PM is a SINGLE figure duplicated across rows (not per-row),
# so PM must NOT be summed for these -- only KSLOC sums.
SUM_SCOPE_GROUPS = {
    "zgo_AGG":    (["zcg_zgo_ng_2025", "zcg_zenith_2025", "zcg_zgo_frontend_2025"], "no_pm_sum"),
    # aeknow_chain is intentionally listed in EXCLUDED below (scope re-verification pending)
    # and must be omitted here so aeknow_AGG is sized by .org only -- matching the documented
    # approach in DATASHEET.md §3.1 and PROJECT_STATUS_FOR_REVIEWER.md §3.2:
    # "AEKnow (.org authored) ... .chain vendored-inflated, disclosed". The chain's KSLOC
    # has since been remediated (165.518 -> 13.292 after removing bundled third-party libs),
    # but PM=1.00's coverage of chain's work needs source re-verification before chain's KSLOC
    # can be included in the aggregate point.
    "aeknow_AGG": (["aeknow_org"], "no_pm_sum"),
    # ink_analyzer's second point (referendum 779, added 2026-07-20 gov2-sweep follow-up):
    # same solo dev (David Semakula), same-scope-multi-repo grant spanning the main
    # ink-analyzer repo + the companion ink-vscode extension repo, one PM figure. Window
    # 2024-04-01 -> 2024-05-16 deliberately starts where the EXISTING ink_analyzer row's
    # window ends (2024-04-01) to avoid double-counting against referendum 619 -- the 779
    # proposal text states this work was explicitly excluded from both the initial v5
    # release and the 619 proposal. Commit-level check: 21/9 commits in the two repos in
    # this window are v5-migration-labelled, matching the itemised task table.
    "ink_analyzer_779_AGG": (["ink_analyzer_779_main", "ink_analyzer_779_vscode"], "no_pm_sum"),
    # FOUND 2026-08-08 during a graded-signal probing pass (see CALIBRATION_FIT_n45's Thirteenth
    # addendum): polkascan_explorer/polkadapt/ui are the SAME funded scope (PM=11.63, identical
    # non-round figure, confirmed by their own notes -- "component 2/3"/"component 3/3 -- sum
    # into polkascan total") split across 3 repos, but were never registered here, so they were
    # silently fit as 3 independent points sharing one PM against 3 different KSLOC values. Same
    # class of fix as zgo_AGG/aeknow_AGG/ink_analyzer_779_AGG above, applied here for consistency.
    "polkascan_AGG": (["polkascan_explorer", "polkascan_polkadapt", "polkascan_ui"], "no_pm_sum"),
}
EXCLUDED = {
    "aeternity_sdk_q1_2025",  # explicitly marked PROVISIONAL in its own notes
    "aeknow_chain",           # PM scope re-verification pending (see SUM_SCOPE_GROUPS comment)
}

# ---------------------------------------------------------------------------------------
# REVERTED 2026-07-20 (user instruction): every point-removal decision below was made by
# looking at which points were hurting the fit's residuals and then finding a reason to cut
# them -- regardless of whether the individual reason was factually true, that process is
# outlier-chasing, not corpus curation, and it is NOT what this script does anymore. All four
# categories are kept here ONLY as a dated evidentiary record (each finding may still be true
# and worth a properly separate, non-fit-driven admissibility review someday) but NONE of them
# are applied to the fit below. The fit uses every collapsed point in the corpus. See
# 6. Logs/CALIBRATION_FIT_n45_2026-07-20.md, "REVERTED" addendum, for the full record of why.
# ---------------------------------------------------------------------------------------
FLAGGED_OUTLIERS = {"dot_login", "sandox_ide", "dodao", "polkascan_AGG"}  # renamed 2026-08-08: the
# point id is now polkascan_AGG (3-repo scope collapse, see SUM_SCOPE_GROUPS) -- same underlying
# whole-repo-at-HEAD upper-bound-sizing concern the flag was originally about, just relabeled.
FLAGGED_REJECTED = {"kitdot", "remarker"}
FLAGGED_SCOPE = {"ink_analyzer"}
FLAGGED_GATE_VIOLATION = {"megaclite", "elara", "fennel", "ask_v01", "bagpipes",
                           "paraspell_maint_2025_26"}


def load_spec():
    return {r["project_id"]: r for r in csv.DictReader(open(SPEC, encoding="utf-8"), delimiter=";")}


def load_size(pid):
    """Reuse-adjusted equivalent KSLOC from the canonical dissect output. Hard-fails (no
    silent fallback) if a measurement is missing -- every point in a calibration fit must
    trace to a real, reproducible measurement."""
    f = REPORTS / f"dissect_{pid}.json"
    if not f.exists():
        raise FileNotFoundError(f"no dissect output for {pid} -- run dissect_pilot.py first")
    d = json.loads(f.read_text(encoding="utf-8"))
    if "error" in d:
        raise ValueError(f"{pid}: dissect error -- {d['error']}")
    return float(d["equivalent_ksloc"])


def build_points(spec):
    """Returns dict pid -> (pm, ksloc, member_ids) for every FINAL calibration point,
    after collapsing dependent-window groups and excluding provisional rows."""
    grouped_ids = set(EXCLUDED)
    points = {}

    for gname, pred in WINDOW_COLLAPSE_GROUPS.items():
        members = sorted(pid for pid in spec if pred(pid))
        grouped_ids |= set(members)
        pm = sum(float(spec[m]["reported_pm"]) for m in members)
        ksloc = sum(load_size(m) for m in members)
        points[gname] = (pm, ksloc, members)

    for gname, (members, mode) in SUM_SCOPE_GROUPS.items():
        grouped_ids |= set(members)
        pms = [float(spec[m]["reported_pm"]) for m in members]
        assert len(set(pms)) == 1, f"{gname}: expected identical PM duplicated per row, got {pms}"
        pm = pms[0]  # NOT summed -- one funded scope, multi-repo
        ksloc = sum(load_size(m) for m in members)
        points[gname] = (pm, ksloc, members)

    for pid, row in spec.items():
        if pid in grouped_ids:
            continue
        points[pid] = (float(row["reported_pm"]), load_size(pid), [pid])

    return points


# ---- fit methodology, reused verbatim from calibrate_actual.py for comparability ----
def metrics(actual, preds):
    actual = np.asarray(actual, float); preds = np.asarray(preds, float)
    mre = np.abs(actual - preds) / actual
    marp0 = np.mean(np.abs(actual[:, None] - actual[None, :]))
    return dict(SA=round(float(1 - np.mean(np.abs(actual - preds)) / marp0), 3),
                MMRE=round(float(np.mean(mre)), 3), MdMRE=round(float(np.median(mre)), 3),
                PRED25=round(float(np.mean(mre <= .25)), 3), PRED30=round(float(np.mean(mre <= .30)), 3))


def loocv(y, lnS, fixedE=None):
    n = len(y); preds = np.zeros(n)
    for i in range(n):
        idx = [j for j in range(n) if j != i]
        if fixedE is None:
            X = np.column_stack([np.ones(n - 1), lnS[idx]])
            b, *_ = np.linalg.lstsq(X, y[idx], rcond=None); lnA, E = b[0], b[1]; res = y[idx] - X @ b
        else:
            E = fixedE; resid = y[idx] - E * lnS[idx]; lnA = float(np.mean(resid)); res = resid - lnA
        preds[i] = math.exp(lnA + E * lnS[i]) * math.exp(np.var(res) / 2)  # Duan smearing
    return preds


def fit_full(y, lnS, fixedE=None):
    if fixedE is None:
        X = np.column_stack([np.ones(len(y)), lnS]); b, *_ = np.linalg.lstsq(X, y, rcond=None)
        return math.exp(b[0]), float(b[1])
    lnA = float(np.mean(y - fixedE * lnS)); return math.exp(lnA), fixedE


def robust_fit(y, lnS):
    """Theil-Sen: E = median of all pairwise ln-ln slopes. Downweights extreme points
    statistically (median, not mean, over pairwise slopes) instead of a human excluding them
    by hand -- the 'baby step' methodological alternative to manual outlier removal."""
    E, lnA, lo, hi = theilslopes(y, lnS)
    return math.exp(lnA), float(E), (float(lo), float(hi))


def robust_loocv(y, lnS):
    n = len(y); preds = np.zeros(n)
    for i in range(n):
        idx = [j for j in range(n) if j != i]
        E, lnA, *_ = theilslopes(y[idx], lnS[idx])
        res = y[idx] - (lnA + E * lnS[idx])
        preds[i] = math.exp(lnA + E * lnS[i]) * math.exp(np.var(res) / 2)  # Duan smearing
    return preds


def run_fit(label, pairs):
    """pairs: list of (id, pm, ksloc). Prints A/E/LOOCV metrics for free-E OLS, fixed-E=0.91,
    and Theil-Sen robust regression (same n, no points removed for any of the three)."""
    ids = [p[0] for p in pairs]
    pm = np.array([p[1] for p in pairs]); ks = np.array([p[2] for p in pairs])
    y = np.log(pm); lnS = np.log(ks)
    print(f"\n{'='*78}\n{label}  (n={len(pairs)})\n{'='*78}")
    out = {"n": len(pairs), "ids": ids}
    for tag, fE in [("free", None), ("fixedE0.91", 0.91)]:
        A, E = fit_full(y, lnS, fE)
        preds = loocv(y, lnS, fE)
        m = metrics(pm, preds)
        r = float(np.corrcoef(lnS, y)[0, 1])
        out[tag] = {"A": round(A, 3), "E": round(E, 3), "r_lnln": round(r, 3), "loocv": m}
        print("%-12s A=%7.4f E=%6.3f r=%5.3f | LOOCV: SA %+6.3f  PRED25 %3.0f%%  PRED30 %3.0f%%  "
              "MMRE %4.0f%%  MdMRE %4.0f%%" % (
                  tag, A, E, r, m["SA"], 100 * m["PRED25"], 100 * m["PRED30"], 100 * m["MMRE"], 100 * m["MdMRE"]))

    A, E, E_ci = robust_fit(y, lnS)
    preds = robust_loocv(y, lnS)
    m = metrics(pm, preds)
    r = float(np.corrcoef(lnS, y)[0, 1])
    out["robust_theilsen"] = {"A": round(A, 3), "E": round(E, 3), "E_95ci": [round(v, 3) for v in E_ci],
                               "r_lnln": round(r, 3), "loocv": m}
    print("%-12s A=%7.4f E=%6.3f r=%5.3f | LOOCV: SA %+6.3f  PRED25 %3.0f%%  PRED30 %3.0f%%  "
          "MMRE %4.0f%%  MdMRE %4.0f%%   (E 95%% CI %.3f-%.3f)" % (
              "robust(TS)", A, E, r, m["SA"], 100 * m["PRED25"], 100 * m["PRED30"], 100 * m["MMRE"],
              100 * m["MdMRE"], E_ci[0], E_ci[1]))
    return out


def main():
    spec = load_spec()
    points = build_points(spec)

    print(f"Collapsed to {len(points)} independent calibration points (from {len(spec)} spec rows).")
    print("\nGroup membership (dependent-window / shared-scope collapses):")
    for gname in list(WINDOW_COLLAPSE_GROUPS) + list(SUM_SCOPE_GROUPS):
        pm, ksloc, members = points[gname]
        print(f"  {gname:18} PM={pm:7.2f}  KSLOC={ksloc:8.3f}  from {len(members)} rows: {members}")
    print(f"  (excluded as provisional -- measurement incomplete/flaky, not a fit-driven "
          f"decision: {sorted(EXCLUDED)})")

    # FULL-CORPUS FIT (2026-07-20, user instruction after reverting the outlier-chasing pass):
    # every collapsed point in the corpus, zero points dropped for any judgment-call reason.
    # The four FLAGGED_* sets above are carried as a dated evidentiary record only -- printed
    # below for visibility, never subtracted from the fit.
    all_pairs = [(pid, pm, ksloc) for pid, (pm, ksloc, _) in points.items()]
    flagged = FLAGGED_OUTLIERS | FLAGGED_REJECTED | FLAGGED_SCOPE | FLAGGED_GATE_VIOLATION
    print(f"\nFlagged in source review, NOT excluded from this fit ({len(flagged)} of "
          f"{len(points)}): {sorted(flagged)}")
    result_full = run_fit("FULL CORPUS FIT (every collapsed point, nothing dropped)", all_pairs)

    # explicit contrast: the naive fit if every raw row (minus the 2 provisional exclusions,
    # which are measurement-completeness gates, not judgment calls) were wrongly treated as an
    # independent point -- shows the pseudo-replication correction's effect, not an exclusion.
    naive_pairs = [(pid, float(row["reported_pm"]), load_size(pid))
                   for pid, row in spec.items() if pid not in EXCLUDED]
    # ksloc=0 raw rows (disclosed pipeline gap: Erlang not in dissect_pilot.py's SRC_EXTS, so a
    # window whose only changes are .erl files legitimately measures zero) are undefined under
    # this fit's log-transform and are excluded from the NAIVE CONTRAST ONLY -- they remain fully
    # present in the real, collapsed-point FULL CORPUS FIT above via their point-level sum.
    zero_naive = [pid for pid, pm, ks in naive_pairs if ks <= 0]
    if zero_naive:
        print(f"\n[disclosed] excluding {zero_naive} from the naive contrast fit only (ksloc=0)")
    naive_pairs = [(pid, pm, ks) for pid, pm, ks in naive_pairs if ks > 0]
    result_naive = run_fit("NAIVE FIT (raw rows as independent points -- FOR CONTRAST ONLY, not the headline)",
                           naive_pairs)

    outdir = REPORTS
    json.dump({"full_corpus_fit": result_full, "naive_contrast": result_naive,
               "flagged_not_excluded": {
                   "outliers": sorted(FLAGGED_OUTLIERS), "rejected": sorted(FLAGGED_REJECTED),
                   "scope_mismatch": sorted(FLAGGED_SCOPE), "gate_violation": sorted(FLAGGED_GATE_VIOLATION)},
               "points": {k: {"pm": v[0], "ksloc": v[1], "members": v[2]} for k, v in points.items()}},
              open(outdir / "calibrate_n45_result.json", "w"), indent=2)
    print(f"\nwrote {outdir / 'calibrate_n45_result.json'}")


if __name__ == "__main__":
    main()
