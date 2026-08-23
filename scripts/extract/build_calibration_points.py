#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_calibration_points.py — deterministically collapses the 73 hand-verified,
source-cited spec rows in data/calibration/pilots_cocomo.csv into the dataset's
44 independent calibration points, per the project's own documented no-pseudo-
replication rule (dependent windows of the same project collapse to one aggregate
point; same-funded-scope multi-repo rows share one PM figure, KSLOC summed).

This is the final assembly step of dataset construction — separate from, and a
prerequisite to, any COCOMO model fitting/calibration (those live in
scripts/validate/calibrate_*.py and are downstream analysis, not part of how the
dataset itself was built).

Group definitions are reproduced verbatim from scripts/validate/calibrate_n45.py
(the two must stay in sync; that script's fit uses these exact same points).

Reads:  data/calibration/pilots_cocomo.csv (73 rows) + reports/dissect_<id>.json
        (per-row equivalent_ksloc, produced by scripts/validate/dissect_pilot.py)
Writes: data/calibration/calibration_points_n44.csv (44 rows)
"""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "data/calibration/pilots_cocomo.csv"
REPORTS = ROOT / "reports"
OUT = ROOT / "data/calibration/calibration_points_n44.csv"

# ---- point-collapsing groups (verbatim from calibrate_n45.py — keep in sync) ----
WINDOW_COLLAPSE_GROUPS = {
    "ae_node_AGG":       lambda pid: pid.startswith("ae_node_"),
    "aeternity_sdk_AGG": lambda pid: pid.startswith("aeternity_sdk_") and pid != "aeternity_sdk_q1_2025",
    "ae_mdw_AGG":        lambda pid: pid.startswith("ae_mdw_"),
    "reactivedot_AGG":   lambda pid: pid.startswith("reactivedot_"),
}
SUM_SCOPE_GROUPS = {
    "zgo_AGG":    (["zcg_zgo_ng_2025", "zcg_zenith_2025", "zcg_zgo_frontend_2025"], "no_pm_sum"),
    "aeknow_AGG": (["aeknow_org"], "no_pm_sum"),
    "ink_analyzer_779_AGG": (["ink_analyzer_779_main", "ink_analyzer_779_vscode"], "no_pm_sum"),
    "polkascan_AGG": (["polkascan_explorer", "polkascan_polkadapt", "polkascan_ui"], "no_pm_sum"),
}
EXCLUDED = {
    "aeternity_sdk_q1_2025",  # explicitly marked PROVISIONAL in its own notes
    "aeknow_chain",           # PM scope re-verification pending (see SUM_SCOPE_GROUPS comment)
}


def load_spec():
    return {r["project_id"]: r for r in csv.DictReader(open(SPEC, encoding="utf-8"), delimiter=";")}


def load_size(pid):
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
        pm = pms[0]
        ksloc = sum(load_size(m) for m in members)
        points[gname] = (pm, ksloc, members)

    for pid, row in spec.items():
        if pid in grouped_ids:
            continue
        points[pid] = (float(row["reported_pm"]), load_size(pid), [pid])

    return points


def main():
    spec = load_spec()
    points = build_points(spec)
    print(f"Collapsed {len(spec)} spec rows -> {len(points)} independent calibration points.")
    print(f"  excluded as provisional (measurement incomplete, not a fit-driven decision): {sorted(EXCLUDED)}")

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["point_id", "reported_pm", "equivalent_ksloc", "n_member_rows", "member_project_ids"])
        for pid in sorted(points):
            pm, ksloc, members = points[pid]
            w.writerow([pid, round(pm, 3), round(ksloc, 3), len(members), "|".join(members)])
    print(f"wrote {len(points)} rows to {OUT}")


if __name__ == "__main__":
    main()
