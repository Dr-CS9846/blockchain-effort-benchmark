#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_graded_signals.py — commit-aligned, leak-free graded (not binary) driver signals for the
n=46 corpus.

PRE-DECLARED DESIGN (fixed before any fit is run, per the standing rule against fit-driven choices):

Problem this fixes: `repo_attributes.csv` (the earlier census's driver/complexity signals, incl.
functional-size counts like n_pallets/n_extrinsics/n_contracts_def) was probed at each repo's single
CENSUS "resolved_commit" -- a fixed, usually-most-recent snapshot, not the commit(s) that actually
bound each of THIS corpus's 46 calibration points' funded windows. Reusing it here would silently
leak future repo state into a past-window's prediction. This script instead re-probes every raw spec
row (73 rows in pilots_cocomo.csv) at EXACTLY the same commit(s) `dissect_pilot.py` already resolved
for that row's SIZE measurement, so size and complexity signal are always read from the identical
repo state.

Per-row commit alignment, mirroring dissect_pilot.py's own three sizing_mode branches exactly:
  - "whole": one checkout at the resolved `ref` (date or commit) -- probe the tree AS-IS, a single
    snapshot. This matches how size_whole() measures KSLOC (whole tree at that ref).
  - "window": TWO checkouts (window start, window end), probed separately; the signal is the
    START->END DELTA (end minus start) of each functional-size count, mirroring EXACTLY how
    size_window() measures KSLOC as a net boundary-diff, not a cumulative snapshot. Using a
    cumulative end-snapshot instead would conflate "how big/complex the whole repo has become by
    now" with "how complex was the specific funded window's work" -- a cumulative count would be
    dominated by everything the project ever built before this window, biasing later windows upward
    for reasons unrelated to that window's own effort. If window start is the empty tree (repo began
    inside the window), the delta is just the end snapshot (start is definitionally zero).
  - "diff": two checkouts at ref_a/ref_b, same delta logic as "window".

Signals probed (functional-size counts, reused verbatim from cocomo_probe.py's probe() regex/counter
logic -- not reinvented, so this is directly comparable to that already-verified extraction code):
  on-chain: n_pallets, n_extrinsics, n_storage, n_events, n_ink_msgs, n_sol_funcs, n_contracts_def, n_rpc
  off-chain: n_exports, n_funcs, n_classes, n_routes
These are graded (count-valued) analogues of the existing binary onchain_runtime/has_contracts flags
-- NOT a replacement for the full 22-driver Boehm taxonomy (most of that taxonomy has no repo-derived
signal at all, graded or binary; see the Track 2 log's driver-depth audit for the full disclosure of
what is and is not covered).

Aggregation to point level: summed across a collapsed point's member rows, exactly matching how PM
and KSLOC are already summed in calibrate_n45.build_points() -- no new aggregation rule invented here.

Reuses dissect_pilot.py's own clone/checkout/commit-resolution code (not reimplemented) so the
checkout commit is guaranteed identical to the one already used for each row's SIZE measurement.
"""
import csv, json, os, re, sys, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dissect_pilot as dp
sys.path.insert(0, str(HERE.parent / "extract"))

ROOT = HERE.parents[1]
SPEC = ROOT / "data/calibration/pilots_cocomo.csv"
REPORTS = ROOT / "reports"

FS_FIELDS = ["n_pallets", "n_extrinsics", "n_storage", "n_events", "n_ink_msgs", "n_sol_funcs",
             "n_contracts_def", "n_rpc", "n_exports", "n_funcs", "n_classes", "n_routes"]
OFF_EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go", ".py", ".java", ".kt")
MAX_BYTES = 600_000
EXCLUDE_DIRS = {"node_modules", "vendor", ".git", "dist", "build", "target",
                "__pycache__", ".venv", "venv", "third_party", "thirdparty"}


def _walk_files(root):
    root = str(root)
    for dpath, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in EXCLUDE_DIRS]
        for fn in fns:
            full = os.path.join(dpath, fn)
            yield os.path.relpath(full, root).replace("\\", "/").lower(), full


def probe_fs_counts(dest):
    """Functional-size counts at the CURRENT checkout state of `dest` -- reused verbatim from
    cocomo_probe.py's probe(), trimmed to just the fs-counting logic (dissect_pilot.py already
    owns cloning/checkout; this only re-scans the tree it left behind)."""
    fs = {k: 0 for k in FS_FIELDS}
    for rel, full in _walk_files(dest):
        low = rel.lower()
        if not (low.endswith(".rs") or low.endswith(".sol") or low.endswith(OFF_EXT)):
            continue
        try:
            if os.path.getsize(full) > MAX_BYTES:
                continue
            txt = open(full, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        if low.endswith(".rs"):
            fs["n_pallets"] += txt.count("#[frame_support::pallet]") + txt.count("#[pallet::pallet]")
            fs["n_extrinsics"] += txt.count("#[pallet::call_index")
            fs["n_storage"] += txt.count("#[pallet::storage]")
            fs["n_events"] += txt.count("#[pallet::event]")
            fs["n_ink_msgs"] += txt.count("#[ink(message")
            fs["n_contracts_def"] += txt.count("#[ink::contract]") + txt.count("#[contract]")
            fs["n_rpc"] += txt.count("#[rpc(") + txt.count("#[method(")
        elif low.endswith(".sol"):
            fs["n_sol_funcs"] += len(re.findall(r"\bfunction\s+\w+", txt))
            fs["n_contracts_def"] += len(re.findall(r"\bcontract\s+\w+", txt))
        else:
            fs["n_exports"] += len(re.findall(
                r"\bexport\s+(?:default\s+)?(?:async\s+)?(?:function|const|let|var|class|interface|type|enum)\b", txt))
            fs["n_exports"] += len(re.findall(r"\bexport\s*\{", txt)) + txt.count("module.exports")
            fs["n_funcs"] += len(re.findall(r"\bfunction\s+\w+\s*\(", txt))
            fs["n_funcs"] += len(re.findall(r"^\s*def\s+\w+\s*\(", txt, re.M))
            fs["n_funcs"] += len(re.findall(r"^\s*func\s+(?:\([^)]*\)\s*)?\w+\s*\(", txt, re.M))
            fs["n_funcs"] += len(re.findall(r"\b\w+\s*[:=]\s*(?:async\s*)?\([^)]*\)\s*=>", txt))
            fs["n_classes"] += len(re.findall(r"\b(?:class|interface)\s+\w+", txt))
            fs["n_routes"] += len(re.findall(
                r"\b(?:app|router|server|fastify|api|route[r]?)\.(?:get|post|put|delete|patch|use)\s*\(", txt, re.I))
            fs["n_routes"] += len(re.findall(r"@(?:Get|Post|Put|Delete|Patch|Route|RequestMapping|app\.route)\b", txt))
    return fs


def checkout(d, sha):
    dp.sh(["git", "checkout", "--quiet", "-f", sha], cwd=d)


def probe_row(row):
    pid = row["project_id"]
    mode = row.get("sizing_mode", "whole").strip()
    d = dp.clone(row["repo_url"], pid)
    result = {"project_id": pid, "mode": mode}
    try:
        if mode == "whole":
            ref = row.get("ref", "").strip()
            c = dp._resolve_before(d, ref) if re.match(r"^\d{4}-\d{2}-\d{2}$", ref) else ref
            if c:
                checkout(d, c)
            fs = probe_fs_counts(d)
            result.update(fs); result["basis"] = "whole-tree snapshot"
        elif mode == "window":
            since, until = row.get("since", "").strip(), row.get("until", "").strip()
            start = dp._resolve_before(d, since)
            end = dp._resolve_before(d, until) or "HEAD"
            if start:
                checkout(d, start)
                fs_start = probe_fs_counts(d)
            else:
                fs_start = {k: 0 for k in FS_FIELDS}   # empty tree -> zero baseline
            checkout(d, end)
            fs_end = probe_fs_counts(d)
            delta = {k: max(0, fs_end[k] - fs_start[k]) for k in FS_FIELDS}
            result.update(delta); result["basis"] = f"window delta ({start[:8] if start else 'EMPTY'}->{end[:8]})"
        elif mode == "diff":
            ref_a, ref_b = row.get("ref_a", "").strip(), row.get("ref_b", "").strip()
            checkout(d, ref_a); fs_a = probe_fs_counts(d)
            checkout(d, ref_b); fs_b = probe_fs_counts(d)
            delta = {k: max(0, fs_b[k] - fs_a[k]) for k in FS_FIELDS}
            result.update(delta); result["basis"] = f"diff delta ({ref_a[:8]}->{ref_b[:8]})"
        else:
            result["error"] = f"unknown sizing_mode {mode!r}"
    except Exception as e:
        result["error"] = str(e)[:200]
    return result


def main():
    spec = {r["project_id"]: r for r in csv.DictReader(open(SPEC, encoding="utf-8"), delimiter=";")}
    out = {}
    n = len(spec)
    for i, (pid, row) in enumerate(spec.items(), 1):
        print(f"[{i}/{n}] probing {pid} ({row.get('sizing_mode','whole')}) ...", flush=True)
        r = probe_row(row)
        out[pid] = r
        tag = "ERROR: " + r["error"] if "error" in r else r.get("basis", "")
        counts = " ".join(f"{k}={r.get(k,0)}" for k in ("n_pallets", "n_extrinsics", "n_contracts_def", "n_exports"))
        print(f"    {tag}  {counts}")

    outpath = REPORTS / "probe_graded_signals_result.json"
    json.dump(out, open(outpath, "w"), indent=2)
    print(f"\nwrote {outpath}")


if __name__ == "__main__":
    main()
