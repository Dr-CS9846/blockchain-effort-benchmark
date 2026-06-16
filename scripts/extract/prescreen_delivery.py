#!/usr/bin/env python3
"""
Delivery-verified pre-screen over the W3F census candidates  —  v2 (actionable shortlist).

v1: tagged each census project DELIVERED / no_delivery_found / REJECT_terminated by cross-referencing the
W3F Grant-Milestone-Delivery repo (deliveries/ + evaluations/) and the application `Status` header.

v2 ADDS, per grant, the fields that let admits land WITHOUT a per-candidate full-app fetch:
  - matched_app_file        : the actual applications/<name>.md filename (kills the "wrong filename" 404 churn)
  - app_fte, app_months     : PRIMARY effort from the application Development-Roadmap overview
  - app_pm                  : app_fte * app_months  (primary-source person-months)
  - n_app_repos             : distinct external github repos referenced (multi-repo / scope-sprawl signal)
  - ks_per_pm               : equivalent_sloc / app_pm  (SCOPE-SANITY ratio; clean pilots ~0.5-2.0)
  - scope_flag              : 'frag?' if ks_per_pm < 0.4 (measured repo is only a fragment -> likely multi-repo,
                              e.g. hyperfridge 1.68/9 = 0.19) ; 'bloat?' if > 8 ; else ''

Runs in CI (needs git clone). Emits data/calibration/census_prescreen.csv ranked so the cleanest
single-artifact DELIVERED grants with a plausible scope ratio float to the top.
"""
import csv, os, re, subprocess, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CENSUS = ROOT / "data/calibration/measurements_census.csv"
OUT = ROOT / "data/calibration/census_prescreen.csv"
WORK = Path("/tmp/w3f_prescreen"); WORK.mkdir(parents=True, exist_ok=True)
GMD = WORK / "Grant-Milestone-Delivery"; GP = WORK / "Grants-Program"

def clone(url, dest):
    if not dest.exists():
        subprocess.run(["git", "clone", "--depth", "1", url, str(dest)], check=True)

def norm(s): return re.sub(r"[^a-z0-9]", "", (s or "").lower())
SUFFIX = re.compile(r"(_|-)(milestone|m)(_|-)?\d+.*$|(_|-)\d+([_-][a-z0-9]+)?$", re.I)
def stem_of(fname): return norm(SUFFIX.sub("", re.sub(r"\.md$", "", fname, flags=re.I)))

# --- application effort + scope extraction -------------------------------------------------
FTE_RE  = re.compile(r"(?im)full[\s-]?time\s*equivalent[^\d\n]{0,12}\(?fte\)?[^\d\n]{0,12}([\d.]+)")
FTE_RE2 = re.compile(r"(?im)\bFTE\b[^\d\n]{0,12}([\d.]+)")
DUR_RE  = re.compile(r"(?im)total\s*estimated\s*duration[^\d\n]{0,12}([\d.]+)\s*(month|week)")
COST_RE = re.compile(r"(?im)total\s*costs?[^\d\n]{0,14}[$]?\s*([\d.,']+)")
GH_RE   = re.compile(r"github\.com/([A-Za-z0-9._-]+)/([A-Za-z0-9._-]+)")
DENY = {"w3f","paritytech","polkadot-sdk","substrate","polkadot","webpack","risc0","risc0-lean4",
        "ethereum","w3c","ibm","CurveSwap","libeufin","cosmos","libra","facebook","apache"}

def app_effort(txt):
    f = FTE_RE.search(txt) or FTE_RE2.search(txt)
    fte = float(f.group(1)) if f else None
    m = DUR_RE.search(txt)
    months = None
    if m:
        v = float(m.group(1)); months = round(v/4.345, 2) if m.group(2).lower().startswith("week") else v
    pm = round(fte*months, 2) if (fte and months) else None
    return fte, months, pm

def app_repos(txt):
    seen = set()
    for o, r in GH_RE.findall(txt or ""):
        r = r.rstrip(".,)").replace(".git","")
        if o.lower() in (d.lower() for d in DENY): continue
        seen.add(f"{o.lower()}/{r.lower()}")
    return seen

def main():
    clone("https://github.com/w3f/Grant-Milestone-Delivery.git", GMD)
    clone("https://github.com/w3f/Grants-Program.git", GP)

    delivered, evaluated = {}, {}
    for folder, bucket in [("deliveries", delivered), ("evaluations", evaluated)]:
        for p in glob.glob(str(GMD / folder / "*.md")):
            name = os.path.basename(p)
            if name.lower() in ("readme.md","milestone-delivery-template.md","evaluation-template.md"): continue
            st = stem_of(name)
            if len(st) >= 4: bucket[st] = bucket.get(st, 0) + 1

    # per application: stem -> (filename, status, fte, months, pm, n_repos)
    apps = {}
    for p in glob.glob(str(GP / "applications" / "*.md")):
        name = os.path.basename(p)
        if name.lower() in ("index.md","application-template.md"): continue
        st = norm(re.sub(r"\.md$","",name,flags=re.I))
        txt = open(p, encoding="utf-8", errors="ignore").read()
        ms = re.search(r"(?im)^\s*[-*]?\s*\*{0,2}status\*{0,2}\s*:?\*{0,2}\s*\[?([A-Za-z ]+)", txt[:4000])
        fte, months, pm = app_effort(txt)
        apps[st] = dict(file=name, status=(ms.group(1).strip() if ms else ""),
                        fte=fte, months=months, pm=pm, n_repos=len(app_repos(txt)))

    def find(pid_norm, bucket):
        best = 0
        for st, n in bucket.items():
            if st == pid_norm or (len(pid_norm) >= 5 and pid_norm in st) or (len(st) >= 5 and st in pid_norm):
                best = max(best, n)
        return best
    def find_app(pid_norm):
        # prefer exact, else longest containment match
        cand = None
        for st, a in apps.items():
            if st == pid_norm: return a
            if (len(pid_norm) >= 5 and pid_norm in st) or (len(st) >= 5 and st in pid_norm):
                if cand is None or len(st) > len(cand[0]): cand = (st, a)
        return cand[1] if cand else None

    rows, seen = [], set()
    for r in csv.DictReader(open(CENSUS, encoding="utf-8")):
        pid = (r.get("project_id") or "").strip()
        if not pid or pid in seen: continue
        seen.add(pid); pn = norm(pid)
        nd, ne = find(pn, delivered), find(pn, evaluated)
        a = find_app(pn) or {}
        status = a.get("status",""); terminated = bool(re.search(r"(?i)terminat|deprecat|withdraw|cancel", status))
        try: eqks = float(r.get("equivalent_sloc") or "")
        except ValueError: eqks = None
        app_pm = a.get("pm")
        kspp = round(eqks/app_pm, 2) if (eqks and app_pm) else ""
        # ks/pm is a WARNING to manually verify scope/reuse, NOT an auto-reject: reuse-corrected and
        # proposed-effort pilots legitimately run low (pontem 0.14, skyekiwi 0.21). Only extremes flag.
        scope = "verify-frag?" if (kspp != "" and kspp < 0.15) else ("verify-bloat?" if (kspp != "" and kspp > 12) else "")
        if terminated:   verdict = "REJECT_terminated"
        elif nd >= 1:    verdict = "DELIVERED"
        elif ne >= 1:    verdict = "evaluated_no_delivery_file"
        else:            verdict = "no_delivery_found"
        rows.append(dict(project_id=pid, verdict=verdict, n_delivery_files=nd, n_evaluations=ne,
            matched_app_file=a.get("file",""), app_status=status, terminated=("Y" if terminated else ""),
            app_fte=a.get("fte",""), app_months=a.get("months",""), app_pm=(app_pm or ""),
            n_app_repos=a.get("n_repos",""), ks_per_pm=kspp, scope_flag=scope,
            repo_url=(r.get("repo_url") or "").strip(),
            planned_pm_census=(r.get("planned_pm") or "").strip(),
            commit_source=(r.get("commit_source") or "").strip(),
            equivalent_sloc=(r.get("equivalent_sloc") or "").strip()))

    # rank: DELIVERED first; then single-artifact (n_app_repos<=1) & sane scope & has app_pm
    vorder = {"DELIVERED":0,"evaluated_no_delivery_file":1,"no_delivery_found":2,"REJECT_terminated":3}
    def key(x):
        # actionable = has primary app_pm AND a low repo-spread (single-artifact likely). scope_flag is
        # informational only and does NOT de-rank (reuse-heavy clean pilots keep their place).
        actionable = (x["app_pm"]!="" and (x["n_app_repos"]=="" or x["n_app_repos"]<=2))
        return (vorder.get(x["verdict"],9), 0 if actionable else 1, -(x["n_delivery_files"] or 0))
    rows.sort(key=key)

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    deliv = [x for x in rows if x["verdict"]=="DELIVERED"]
    clean = [x for x in deliv if x["app_pm"]!="" and (x["n_app_repos"]=="" or x["n_app_repos"]<=2)]
    print(f"=== prescreen v2: {len(rows)} projects | DELIVERED {len(deliv)} | "
          f"REJECT_terminated {sum(1 for x in rows if x['verdict']=='REJECT_terminated')} ===")
    print(f"admit-ready DELIVERED (app_pm present + <=2 repos; scope_flag=verify-only): {len(clean)}")
    print("--- top 30 admit-ready ---")
    print(f"{'project':30}{'app_pm':>7}{'ksPM':>6}{'repos':>6}  app_file")
    for x in clean[:30]:
        print(f"  {x['project_id'][:28]:28}{str(x['app_pm']):>7}{str(x['ks_per_pm']):>6}{str(x['n_app_repos']):>6}  {x['matched_app_file']}")
    print(f"\nwrote {OUT}")

if __name__ == "__main__":
    main()
