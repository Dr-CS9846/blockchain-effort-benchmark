#!/usr/bin/env python3
"""
measure_equiv_sloc.py — reuse-adjusted EQUIVALENT SLOC for the verified pilot set (grant-authored code only).
=============================================================================================================
WHY: raw whole-repo cloc at HEAD overcounts effort-relevant size for (a) brownfield/maintenance grants that
touched only a slice, (b) forks of the Substrate node-template, and (c) repos that kept growing for years after
the grant. The first full-set fit was R^2=0.08 largely for this reason (e.g. dotreasury: 72 KSLOC at HEAD for a
~20 dev-day feature).

WHAT: for each repo we isolate the GRANT DEVELOPMENT BURST from git history and count the code the grant
authored there — operationalising the COCOMO II reuse model (new code = full weight; inherited/template code =
excluded) without hand DM/CM/IM judgements:

  1. Full clone; `git log --numstat` over all history (no merges).
  2. Per commit: sum line ADDITIONS in *code* files only (whitelisted source extensions; docs/json/lock/assets
     excluded). Commits adding > IMPORT_CAP lines in one shot are flagged as bulk template/vendored imports and
     excluded from the grant total (reported separately so the choice is transparent).
  3. Slide a window of width = the grant's stated duration (months) over the commit timeline (two-pointer) and
     pick the window with the most added code — that burst = the grant's active development period.
  4. equiv_sloc = code additions inside that burst (import-capped). For greenfield the burst ≈ initial build
     (≈ full size); for brownfield the burst ≈ just the funded slice (≪ full size). Self-correcting.

Output: data/calibration/pilot_equiv_sloc.csv (id, repo, dur_months, full_code, burst_added, burst_added_capped,
n_import_commits, window_start, window_end, equiv_sloc, equiv_ksloc, status). stdlib + git. CI.
"""
import csv, re, subprocess, os
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parents[2]
PILOTS = ROOT / "data/calibration/VERIFIED_PILOTS.md"
SIZES  = ROOT / "data/calibration/pilot_sizes.csv"
OUT    = ROOT / "data/calibration/pilot_equiv_sloc.csv"
WORK   = Path("/tmp/equiv"); WORK.mkdir(parents=True, exist_ok=True)

IMPORT_CAP = 12000          # single-commit code additions above this = likely bulk import/vendored template
CODE_EXT = {".rs",".ts",".tsx",".js",".jsx",".mjs",".cjs",".py",".go",".java",".kt",".sol",".hs",".lua",
            ".c",".cc",".cpp",".h",".hpp",".vue",".svelte",".rb",".php",".move",".cairo",".scala",".swift",
            ".ml",".ex",".exs",".erl",".dart",".sh",".pl",".r",".jl",".clj",".fs",".cs",".elm",".nim",".zig"}

def sh(cmd, timeout=120, **kw):
    try: return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, **kw)
    except subprocess.TimeoutExpired:
        class T: returncode=124; stdout=""; stderr="timeout"
        return T()

def months_from(cell, pm):
    m=re.search(r"×\s*([\d.]+)\s*mo", cell)
    if m: return float(m.group(1))
    m=re.search(r"([\d.]+)\s*dev[\s-]?weeks", cell, re.I)
    if m: return round(float(m.group(1))/4.345, 2)
    m=re.search(r"([\d.]+)\s*(?:person|dev)[\s-]?days", cell, re.I)
    if m: return round(float(m.group(1))/19.0, 2)
    return max(pm, 1.0) if pm else 3.0     # fallback: ~PM months (≈1 FTE), min 1

def parse_pilots():
    out={}
    for ln in open(PILOTS, encoding="utf-8"):
        if not re.match(r"^\|\s*\d+\s*\|", ln): continue
        c=[x.strip() for x in ln.split("|")]
        if len(c)<9 or "REMOVED" in ln: continue
        idn=c[1]; eff=c[6]
        m=re.search(r"([0-9]+\.?[0-9]*)", c[7].replace("*",""))
        pm=float(m.group(1)) if m else 0.0
        out[idn]=months_from(eff, pm)
    return out

def commit_adds(repo_dir):
    """list of (datetime, code_added) per commit, oldest→newest."""
    r=sh(["git","-C",str(repo_dir),"log","--no-merges","--numstat","--date=iso-strict",
          "--pretty=format:#C#%cI"], timeout=180)
    if r.returncode!=0: return None
    commits=[]; cur_date=None; cur_add=0
    for line in r.stdout.splitlines():
        if line.startswith("#C#"):
            if cur_date is not None: commits.append((cur_date, cur_add))
            cur_date=line[3:].strip()[:19]; cur_add=0
        elif line.strip():
            p=line.split("\t")
            if len(p)>=3 and p[0].isdigit():
                ext=os.path.splitext(p[2])[1].lower()
                if ext in CODE_EXT: cur_add+=int(p[0])
    if cur_date is not None: commits.append((cur_date, cur_add))
    parsed=[]
    for d,a in commits:
        try: parsed.append((datetime.fromisoformat(d), a))
        except ValueError: pass
    parsed.sort(key=lambda t:t[0])
    return parsed

def burst(commits, dur_months):
    """densest window of width dur_months by capped code-additions (two-pointer)."""
    if not commits: return 0,0,0,"",""
    width=timedelta(days=dur_months*30.44)
    capped=[(d, (0 if a>IMPORT_CAP else a), a) for d,a in commits]
    n=len(capped); best=-1; bi=bj=0; j=0; run=0
    # prefix not used; sliding two-pointer
    import collections
    dq=collections.deque()  # holds capped adds
    s=0; lo=0
    best=0; bw=("","")
    for hi in range(n):
        s+=capped[hi][1]
        while capped[hi][0]-capped[lo][0] > width:
            s-=capped[lo][1]; lo+=1
        if s>best:
            best=s; bw=(capped[lo][0].date().isoformat(), capped[hi][0].date().isoformat())
    # raw (uncapped) sum in same window width for reference; n import commits overall
    n_import=sum(1 for _,_,a in capped if a>IMPORT_CAP)
    # raw best window (uncapped)
    s=0; lo=0; bestraw=0
    for hi in range(n):
        s+=capped[hi][2]
        while capped[hi][0]-capped[lo][0] > width:
            s-=capped[lo][2]; lo+=1
        bestraw=max(bestraw,s)
    return best, bestraw, n_import, bw[0], bw[1]

def main():
    dur=parse_pilots()
    sizes={r["id"]: r for r in csv.DictReader(open(SIZES, encoding="utf-8"))}
    out=[]
    for idn, srow in sizes.items():
        repo=srow["listed_repo"]; full=srow.get("code_lines","")
        dm=dur.get(idn, 3.0)
        dest=WORK / repo.replace("/","__")
        status="ok"
        if not dest.exists():
            cl=sh(["git","clone","--no-tags","--single-branch",f"https://github.com/{repo}.git",str(dest)], timeout=180)
            if cl.returncode!=0: status="clone_failed"
        commits = commit_adds(dest) if status=="ok" else None
        if commits is None:
            out.append(dict(id=idn, repo=repo, dur_months=dm, full_code=full, burst_added="",
                            burst_added_capped="", n_import_commits="", window_start="", window_end="",
                            equiv_sloc="", equiv_ksloc="", status=status if status!="ok" else "log_failed"))
            continue
        cap, raw, nimp, ws, we = burst(commits, dm)
        out.append(dict(id=idn, repo=repo, dur_months=dm, full_code=full, burst_added=raw,
                        burst_added_capped=cap, n_import_commits=nimp, window_start=ws, window_end=we,
                        equiv_sloc=cap, equiv_ksloc=round(cap/1000.0,3) if cap else 0, status="ok"))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols=["id","repo","dur_months","full_code","burst_added","burst_added_capped","n_import_commits",
          "window_start","window_end","equiv_sloc","equiv_ksloc","status"]
    with open(OUT,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(out)

    ok=[x for x in out if x["status"]=="ok" and x["equiv_ksloc"]]
    print(f"=== equivalent-SLOC (grant-burst) measured {len(ok)}/{len(out)} ===")
    if ok:
        import statistics as st
        eq=[float(x["equiv_ksloc"]) for x in ok]
        fc=[int(x["full_code"])/1000 for x in ok if x["full_code"]]
        print(f"  equiv KSLOC: min {min(eq):.2f}  median {st.median(eq):.2f}  max {max(eq):.2f}")
        ratios=[float(x['equiv_ksloc'])/(int(x['full_code'])/1000) for x in ok if x['full_code'] and int(x['full_code'])>0]
        if ratios: print(f"  equiv/full ratio: median {st.median(ratios):.2f} (1.0=greenfield, <1=reuse/brownfield discount)")
    fails=[x for x in out if x["status"]!="ok"]
    if fails: print("  failed:", ", ".join(f"#{x['id']}({x['status']})" for x in fails[:30]))
    print(f"\nwrote {OUT}")

if __name__=="__main__":
    main()
