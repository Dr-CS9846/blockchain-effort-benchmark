#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dissect_pilot.py  —  per-project COCOMO II dissection of a verified pilot (PM=PM, one at a time)
================================================================================================
For ONE hand-verified matched triple (reported PM + the ONE repo that produced it + on-chain proof),
measure the matched-slice SIZE, assign the 22 COCOMO II drivers (5 SF + 17 EM) from objective repo
signals + evidence-based overrides, and compute:

    E       = 0.91 + 0.01 * sum(SF)
    PM_pred = A * Size^E * prod(EM)          (A = published 2.94, and optional blockchain-calibrated A)
    A_local = reported_PM / (Size^E * prod(EM))     <- the exact A that makes PM(COCOMO) = PM(reported)

PM=PM holds per project by A_local; the science is whether A_local clusters near 2.94 across the clean
curated set. Every non-Nominal driver must cite evidence (recorded in the spec / notes).

Reads one or more rows from data/calibration/pilots_cocomo.csv (semicolon-delimited). Each row carries
repo + sizing mode + reported PM + objective driver flags + optional rating overrides (ov_<DRIVER>).
Clones the repo, measures size per mode, writes reports/dissect_<project_id>.json and prints a readable
breakdown. Resumable / one-at-a-time via --only.

Sizing modes:
  whole   : checkout <ref> (tag/commit/HEAD), cloc SOURCE languages -> KSLOC (greenfield delivery).
  window  : git log --since <since> --until <until> --numstat -> added SOURCE lines (brownfield slice).
  diff    : git diff <ref_a>..<ref_b> --numstat -> added+modified SOURCE lines (exact developer range).
"""
import argparse, csv, json, math, os, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cocomo2_tables as T
import cocomo_fit as F   # reuse synth_ratings (objective signal -> rating)

HERE = Path(__file__).parent.resolve()
CACHE = HERE / "dissect_cache"
SRC_EXTS = {".rs",".ts",".tsx",".js",".jsx",".vue",".sol",".ink",".py",".go",".java",".kt",
            ".c",".cc",".cpp",".h",".hpp",".cs",".rb",".php",".scala",".move",".cairo",".swift",
            ".nix",".lean",".circom"}
VENDOR = ("node_modules/","vendor/","dist/","build/","target/","third_party/","thirdparty/",
          ".git/","bower_components/","__pycache__/")

def sh(args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)

def clone(repo_url, pid):
    CACHE.mkdir(exist_ok=True)
    d = CACHE / pid
    if not d.exists():
        r = sh(["git","clone","--quiet",repo_url,str(d)])
        if r.returncode != 0:
            raise RuntimeError(f"clone failed: {r.stderr.strip()[:300]}")
    return d

def _is_src(path):
    p = path.lower()
    if any(v in p for v in VENDOR): return False
    return os.path.splitext(p)[1] in SRC_EXTS

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
def _resolve_before(d, when):
    """Last commit on HEAD at/just before a YYYY-MM-DD date (repo state at that date)."""
    r = sh(["git","rev-list","-1",f"--before={when} 23:59:59","HEAD"], cwd=d)
    return r.stdout.strip()

def size_whole(d, ref):
    # ref may be a commit/tag OR a YYYY-MM-DD cutoff (checkout repo state at that date)
    if ref and re.match(r"^\d{4}-\d{2}-\d{2}$", ref.strip()):
        c = _resolve_before(d, ref.strip())
        if not c:
            raise RuntimeError(f"cutoff {ref} predates first commit (no checkout) - pick a later date/commit")
        sh(["git","checkout","--quiet",c], cwd=d)
    elif ref: sh(["git","checkout","--quiet",ref], cwd=d)
    # prefer cloc; fallback to line count over source files
    r = sh(["cloc","--quiet","--json","--exclude-dir="+",".join(v.strip("/") for v in VENDOR)] + [str(d)])
    if r.returncode == 0 and r.stdout.strip():
        try:
            j = json.loads(r.stdout)
            code = sum(v["code"] for k,v in j.items()
                       if k in F.__dict__.get("SOURCE_LANGS", set()) or k in SOURCE_LANGS_FALLBACK)
            if code > 0: return code/1000.0, "cloc"
        except Exception: pass
    # fallback: count non-blank source lines
    total = 0
    for root,_,files in os.walk(d):
        for f in files:
            fp = os.path.join(root,f)
            rel = os.path.relpath(fp,d)
            if not _is_src(rel): continue
            try:
                with open(fp,encoding="utf-8",errors="ignore") as fh:
                    total += sum(1 for ln in fh if ln.strip())
            except Exception: pass
    return total/1000.0, "linecount"

def _numstat(d, gitargs):
    r = sh(["git"]+gitargs, cwd=d)
    add = mod_del = 0
    for ln in r.stdout.splitlines():
        parts = ln.split("\t")
        if len(parts) != 3: continue
        a,dl,path = parts
        if a in ("-","") or not _is_src(path): continue
        try: add += int(a); mod_del += int(dl)
        except ValueError: pass
    return add, mod_del

def size_window(d, since, until):
    # NET delta between the repo state at window-start and window-end (NOT cumulative log churn,
    # which double-counts refactors/moves/snapshots). Two-snapshot diff = real delivered code.
    start = _resolve_before(d, since)
    end = _resolve_before(d, until) or "HEAD"
    a_ref = start if start else EMPTY_TREE     # empty tree if repo began inside the window
    add, dele = _numstat(d, ["diff","--numstat",f"{a_ref}..{end}"])
    return add/1000.0, {"added": add, "deleted": dele, "start": (start[:8] or "EMPTY"),
                        "end": end[:8], "metric": "net-delta(boundary-diff)"}

def size_diff(d, ref_a, ref_b):
    sh(["git","fetch","--quiet","--tags"], cwd=d)
    add, dele = _numstat(d, ["diff","--numstat",f"{ref_a}..{ref_b}"])
    # exact range: added + modified(=deleted overlap) ~ added captures new+modified-new lines
    return add/1000.0, {"added": add, "deleted": dele}

SOURCE_LANGS_FALLBACK = {"Rust","Go","TypeScript","JavaScript","JSX","TSX","Python","Solidity","C",
    "C++","C/C++ Header","Java","Kotlin","Swift","C#","Ruby","Scala","Vyper","Move","Cairo","PHP",
    "Dart","Vuejs Component","Nix","Lean","Circom"}

def _flag(row,k): return "1" if str(row.get(k,"0")).strip() in ("1","true","True") else "0"

def dissect(row, A_bc=None):
    pid = row["project_id"]; reported_pm = float(row["reported_pm"])
    d = clone(row["repo_url"], pid)
    mode = row.get("sizing_mode","whole").strip()
    if mode == "whole":
        ks, how = size_whole(d, row.get("ref","").strip()); churn = {}
    elif mode == "window":
        ks, churn = size_window(d, row["since"], row["until"]); how = "git-window"
    elif mode == "diff":
        ks, churn = size_diff(d, row["ref_a"], row["ref_b"]); how = "git-diff"
    else:
        raise ValueError(f"bad sizing_mode {mode}")
    # equivalent SLOC: whole greenfield ~ all new; slice ~ authored lines are the work
    equiv_ks = ks  # honest first pass; reuse-adjustment hook can refine per project
    if equiv_ks <= 0:
        raise RuntimeError(f"{pid}: measured 0 KSLOC (mode={mode}); check refs/window")

    # build attribute + measurement rows for synth_ratings
    a = {k:_flag(row,k) for k in ("has_ci","has_tests","has_docker","has_docs","has_audit",
         "has_lintfmt","onchain_runtime","has_contracts","dep_consensus","dep_crosschain",
         "dep_zkcrypto","dep_contract")}
    a["status"]="OK"
    SF, EM, BC = F.synth_ratings({}, a)
    # evidence-based overrides (ov_<DRIVER>=rating), each must be justified in spec notes
    overrides = {}
    for k,v in row.items():
        if isinstance(k,str) and k.startswith("ov_") and v and str(v).strip():
            name = k[3:]; rating = str(v).strip()
            if name in SF: SF[name]=rating; overrides[name]=rating
            elif name in EM: EM[name]=rating; overrides[name]=rating

    E = T.exponent_E(SF)
    prodEM = 1.0
    em_detail = {}
    for v in EM:
        mv = T.em_value(v, EM[v]); prodEM *= mv; em_detail[v] = {"rating":EM[v], "mult":round(mv,3)}
    sf_detail = {v:{"rating":SF[v],"value":round(T.sf_value(v,SF[v]),3)} for v in SF}
    base = (equiv_ks**E) * prodEM           # Size^E * prod(EM)
    pm_pub = T.A * base
    A_local = reported_pm / base
    out = dict(project_id=pid, reported_pm=round(reported_pm,3), sizing_mode=mode, size_how=how,
               churn=churn, ksloc=round(ks,3), equivalent_ksloc=round(equiv_ks,3),
               E=round(E,4), sumSF=round((E-T.B)/0.01,2), prodEM=round(prodEM,4),
               sf=sf_detail, em=em_detail, overrides=overrides,
               PM_pred_A2_94=round(pm_pub,3), pct_err_A2_94=round((pm_pub-reported_pm)/reported_pm*100,1),
               A_local_for_PMeqPM=round(A_local,3))
    if A_bc:
        out["PM_pred_Abc"]=round(A_bc*base,3); out["A_bc_used"]=A_bc
        out["pct_err_Abc"]=round((A_bc*base-reported_pm)/reported_pm*100,1)
    return out

def main():
    ap = argparse.ArgumentParser()
    root = os.path.dirname(os.path.dirname(HERE))
    ap.add_argument("--spec", default=os.path.join(root,"data/calibration/pilots_cocomo.csv"))
    ap.add_argument("--only", default="")
    ap.add_argument("--abc", type=float, default=0.0, help="blockchain-calibrated A (optional)")
    ap.add_argument("--outdir", default=os.path.join(root,"reports"))
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.spec,encoding="utf-8"), delimiter=";"))
    if a.only:
        keep=set(a.only.split(",")); rows=[r for r in rows if r["project_id"] in keep]
    os.makedirs(a.outdir, exist_ok=True)
    allout=[]
    for row in rows:
        try:
            o = dissect(row, A_bc=(a.abc or None))
        except Exception as e:
            o = dict(project_id=row["project_id"], error=str(e)[:400])
        allout.append(o)
        json.dump(o, open(os.path.join(a.outdir,f"dissect_{row['project_id']}.json"),"w"), indent=2)
        print("="*72)
        if "error" in o: print(f"{o['project_id']}: ERROR {o['error']}"); continue
        print(f"PILOT {o['project_id']}  (reported {o['reported_pm']} PM)")
        print(f"  size: {o['ksloc']} KSLOC (equiv {o['equivalent_ksloc']}) via {o['size_how']} "
              f"[{o['sizing_mode']}]  churn={o['churn']}")
        print(f"  E={o['E']} (ΣSF={o['sumSF']})   ∏EM={o['prodEM']}   overrides={o['overrides']}")
        print(f"  PM_pred @A=2.94 : {o['PM_pred_A2_94']}   ({o['pct_err_A2_94']:+}% vs reported)")
        if 'PM_pred_Abc' in o:
            print(f"  PM_pred @A={o['A_bc_used']} : {o['PM_pred_Abc']}   ({o['pct_err_Abc']:+}%)")
        print(f"  >> A_local for PM=PM : {o['A_local_for_PMeqPM']}  (published A=2.94)")
    json.dump(allout, open(os.path.join(a.outdir,"dissect_all.json"),"w"), indent=2)
    print(f"\nwrote {len(allout)} dissection(s) to {a.outdir}")

if __name__ == "__main__":
    main()
