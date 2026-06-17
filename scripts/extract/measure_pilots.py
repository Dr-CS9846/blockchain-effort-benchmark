#!/usr/bin/env python3
"""
measure_pilots.py  —  delivery-repo resolver + size (KSLOC) extractor for the verified pilot set.
=================================================================================================
Two jobs in one pass, over every row of data/calibration/VERIFIED_PILOTS.md:

  1. DELIVERY-REPO CROSS-CHECK — for each pilot, scan the relevant milestone-delivery repo
     (w3f / crust / POSG) for the project's delivery doc and extract the *actual* deliverable repo it
     names ("Repository: github.com/...", or the first non-upstream code repo link). This catches the
     "matched repo is prior-art/dependency" trap (e.g. Jot's real repo methodfive/jot is only in the
     delivery doc). The listed repo (hand-verified) is what we measure; delivery_repo is recorded and a
     `repo_mismatch` flag is raised when they differ so a human can adjudicate. NO silent overrides.

  2. SIZE — shallow-clone the listed repo, pin the exact commit SHA + date, and run `cloc` (excluding
     vendored dirs) to get code lines → KSLOC. This is the size half of the matched triple, needed to
     calibrate Effort = A * Size^E on all 100.

Output: data/calibration/pilot_sizes.csv  (id, project, source, listed_repo, delivery_repo, repo_mismatch,
        commit_sha, commit_date, n_files, code_lines, ksloc, status). stdlib + git + cloc. CI.
"""
import csv, json, os, re, subprocess, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PILOTS = ROOT / "data/calibration/VERIFIED_PILOTS.md"
OUT = ROOT / "data/calibration/pilot_sizes.csv"
WORK = Path("/tmp/measure"); WORK.mkdir(parents=True, exist_ok=True)
REPOS = WORK / "repos"; REPOS.mkdir(exist_ok=True)

DELIVERY_SRC = {
    "W3F":   "https://github.com/w3f/Grant-Milestone-Delivery.git",
    "Crust": "https://github.com/crustio/Crust-Grant-Milestone-Delivery.git",
    "POSG":  "https://github.com/PolkadotOpenSourceGrants/delivery.git",
}
EXCLUDE_DIRS = "node_modules,target,dist,build,vendor,.git,Pods,bin,obj,out,.next,coverage,deps,_build,artifacts"
UPSTREAM = {"paritytech","w3f","polkadot","substrate","ipfs","ethereum","Off-Narrative-Labs","crustio",
            "PolkadotOpenSourceGrants","zeropoolnetwork","kodadot"}  # likely-dependency orgs (flag, don't trust)

def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def clone(url, dest, branch=None):
    if dest.exists(): return True
    cmd = ["git","clone","--depth","1"] + (["-b",branch] if branch else []) + [url, str(dest)]
    return sh(cmd).returncode == 0

def norm(s): return re.sub(r"[^a-z0-9]","",(s or "").lower())
SUFFIX = re.compile(r"(_|-)(milestone|m)(_|-)?\d+.*$|(_|-)\d+([_-][a-z0-9]+)?$", re.I)
def stem_of(fn): return norm(SUFFIX.sub("", re.sub(r"\.md$","",fn,flags=re.I)))
GH = re.compile(r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")

def source_of(chain):
    if "Crust" in chain: return "Crust"
    if "POSG" in chain:  return "POSG"
    return "W3F"

def parse_pilots():
    rows=[]
    for ln in open(PILOTS, encoding="utf-8"):
        if not re.match(r"^\|\s*\d+\s*\|", ln): continue
        c=[x.strip() for x in ln.split("|")]
        if len(c) < 9: continue
        idn=c[1]; proj=c[2]; chain=c[3]; repo_cell=c[8]
        if "ParaSpell" in proj: continue           # dropped pilot
        m=GH.search(repo_cell) or re.search(r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", repo_cell)
        if not m: continue
        owner_repo = "/".join(m.groups()) if m.lastindex==2 else m.group(1)
        rows.append(dict(id=idn, project=re.sub(r"\*","",proj).strip(), source=source_of(chain),
                         listed_repo=owner_repo.replace(".git","")))
    return rows

def build_delivery_index():
    idx={}  # source -> {stem: deliverable_repo}
    for src,url in DELIVERY_SRC.items():
        d = WORK / f"delivery_{src}"
        if not clone(url, d):
            idx[src] = {}; continue
        m={}
        for p in glob.glob(str(d / "**" / "*.md"), recursive=True):
            name=os.path.basename(p)
            if name.lower() in ("readme.md","milestone-delivery-template.md","evaluation-template.md"): continue
            txt=open(p, encoding="utf-8", errors="ignore").read()
            # prefer an explicit "Repository:" line; else first code repo link that isn't upstream/self
            repo=None
            mr=re.search(r"(?im)repositor(?:y|ies)\s*[:\-]?\s*(?:https?://)?github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", txt)
            if mr: repo=mr.group(1)
            else:
                for o,r in GH.findall(txt):
                    if o in UPSTREAM or o.lower()=="polkadotopensourcegrants": continue
                    repo=f"{o}/{r}"; break
            if repo:
                st=stem_of(name)
                if len(st)>=4: m.setdefault(st, repo.replace(".git",""))
        idx[src]=m
    return idx

def cloc_dir(d):
    r=sh(["cloc","--json","--quiet",f"--exclude-dir={EXCLUDE_DIRS}", str(d)])
    if r.returncode!=0 or not r.stdout.strip(): return None
    try: j=json.loads(r.stdout)
    except json.JSONDecodeError: return None
    s=j.get("SUM",{})
    return dict(files=s.get("nFiles",0), code=s.get("code",0))

def main():
    rows=parse_pilots()
    print(f"pilots parsed: {len(rows)}")
    didx=build_delivery_index()
    print("delivery-doc repos indexed:", {k:len(v) for k,v in didx.items()})

    out=[]
    for r in rows:
        src=r["source"]; listed=r["listed_repo"]
        # delivery-doc cross-check
        drepo=""
        for st,rp in didx.get(src,{}).items():
            pn=norm(r["project"]); lr=norm(listed.split("/")[-1])
            if st==lr or (len(lr)>=5 and lr in st) or (len(st)>=5 and st in pn):
                drepo=rp; break
        mism = "Y" if (drepo and norm(drepo)!=norm(listed)) else ""
        # size
        dest=REPOS / listed.replace("/","__")
        ok=clone(f"https://github.com/{listed}.git", dest)
        sha=date=""; files=code=0; status="ok"
        if ok:
            sha=sh(["git","-C",str(dest),"rev-parse","HEAD"]).stdout.strip()[:12]
            date=sh(["git","-C",str(dest),"log","-1","--format=%cI"]).stdout.strip()[:10]
            c=cloc_dir(dest)
            if c: files,code=c["files"],c["code"]
            else: status="cloc_failed"
        else:
            status="clone_failed"
        out.append(dict(id=r["id"], project=r["project"][:40], source=src, listed_repo=listed,
                        delivery_repo=drepo, repo_mismatch=mism, commit_sha=sha, commit_date=date,
                        n_files=files, code_lines=code, ksloc=round(code/1000.0,3) if code else "",
                        status=status))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols=["id","project","source","listed_repo","delivery_repo","repo_mismatch","commit_sha",
          "commit_date","n_files","code_lines","ksloc","status"]
    with open(OUT,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(out)

    okrows=[x for x in out if x["status"]=="ok" and x["ksloc"]!=""]
    fails=[x for x in out if x["status"]!="ok"]
    mismatches=[x for x in out if x["repo_mismatch"]=="Y"]
    print(f"\n=== measured {len(okrows)}/{len(out)} | clone/cloc fails {len(fails)} | repo mismatches {len(mismatches)} ===")
    if okrows:
        ks=sorted(float(x["ksloc"]) for x in okrows)
        print(f"KSLOC: min {ks[0]}  median {ks[len(ks)//2]}  max {ks[-1]}")
    if mismatches:
        print("-- delivery-doc repo MISMATCHES (review) --")
        for x in mismatches[:40]:
            print(f"  #{x['id']:>3} {x['project'][:26]:28} listed={x['listed_repo']:38} delivery={x['delivery_repo']}")
    if fails:
        print("-- could not measure (resolve manually / use delivery_repo) --")
        for x in fails[:40]:
            print(f"  #{x['id']:>3} {x['project'][:26]:28} {x['listed_repo']:40} {x['status']}  (delivery={x['delivery_repo']})")
    print(f"\nwrote {OUT}")

if __name__ == "__main__":
    main()
