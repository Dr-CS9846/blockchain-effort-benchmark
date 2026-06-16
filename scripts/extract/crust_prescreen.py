#!/usr/bin/env python3
"""
crust_prescreen.py  —  matched-triple pre-screen over the Crust Grants Program (diversified, non-W3F source).
==============================================================================================================
Crust runs its OWN W3F-template grants program with its OWN milestone-delivery repo and distinct
(storage-domain) grantees, so it gives clean, believe-the-stated-FTE matched triples that do NOT overlap our
W3F set. This clones both Crust repos, reads each application's Development-Roadmap FTE+duration (primary
effort), the listed project repo(s), and the application Status, then cross-references the Crust delivery repo
to mark DELIVERED. Emits data/calibration/crust_prescreen.csv ranked so clean single-repo DELIVERED grants with
a stated FTE float to the top for hand-verification.

Mirrors scripts/extract/prescreen_delivery.py (W3F) but for crustio/* and without the SLOC scope ratio (no
Crust census measured yet — scope sanity is applied later, per-candidate, before admission). stdlib only; CI.
"""
import csv, os, re, subprocess, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/calibration/crust_prescreen.csv"
WORK = Path("/tmp/crust_prescreen"); WORK.mkdir(parents=True, exist_ok=True)
GP  = WORK / "Crust-Grants-Program"
GMD = WORK / "Crust-Grant-Milestone-Delivery"

def clone(url, dest, branch=None):
    if not dest.exists():
        cmd = ["git", "clone", "--depth", "1"]
        if branch: cmd += ["-b", branch]
        cmd += [url, str(dest)]
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            # fall back to default branch if the guessed one is wrong
            subprocess.run(["git", "clone", "--depth", "1", url, str(dest)], check=True)

def norm(s): return re.sub(r"[^a-z0-9]", "", (s or "").lower())
SUFFIX = re.compile(r"(_|-)(milestone|m)(_|-)?\d+.*$|(_|-)\d+([_-][a-z0-9]+)?$", re.I)
def stem_of(fname): return norm(SUFFIX.sub("", re.sub(r"\.md$", "", fname, flags=re.I)))

FTE_RE  = re.compile(r"(?im)full[\s-]?time\s*equivalent[^\d\n]{0,12}\(?fte\)?[^\d\n]{0,12}([\d.]+)")
FTE_RE2 = re.compile(r"(?im)\bFTE\b[^\d\n]{0,12}([\d.]+)")
DUR_RE  = re.compile(r"(?im)total\s*estimated\s*duration[^\d\n]{0,12}([\d.]+)\s*(month|week)")
COST_RE = re.compile(r"(?im)total\s*costs?[^\d\n]{0,14}[$]?\s*([\d.,']+)")
GH_RE   = re.compile(r"github\.com/([A-Za-z0-9._-]+)/([A-Za-z0-9._-]+)")
DENY = {"crustio","w3f","paritytech","polkadot-sdk","substrate","polkadot","ethereum","w3c","apache","cosmos"}

def app_effort(txt):
    f = FTE_RE.search(txt) or FTE_RE2.search(txt)
    fte = float(f.group(1).replace(",", ".")) if f else None
    m = DUR_RE.search(txt)
    months = None
    if m:
        v = float(m.group(1)); months = round(v/4.345, 2) if m.group(2).lower().startswith("week") else v
    pm = round(fte*months, 2) if (fte and months) else None
    return fte, months, pm

def app_repos(txt):
    seen = set()
    for o, r in GH_RE.findall(txt or ""):
        r = r.rstrip(".,)").replace(".git", "")
        if o.lower() in (d.lower() for d in DENY): continue
        seen.add(f"{o.lower()}/{r.lower()}")
    return seen

def first_repo(txt):
    for o, r in GH_RE.findall(txt or ""):
        if o.lower() in (d.lower() for d in DENY): continue
        return f"https://github.com/{o}/{r.rstrip('.,)').replace('.git','')}"
    return ""

def delivery_stems():
    """All delivered/evaluated stems from the Crust delivery repo (folder layout may vary -> scan recursively)."""
    delivered, evaluated = {}, {}
    for p in glob.glob(str(GMD / "**" / "*.md"), recursive=True):
        name = os.path.basename(p); low = name.lower()
        if low in ("readme.md", "milestone-delivery-template.md", "evaluation-template.md"): continue
        path_low = p.lower()
        bucket = evaluated if "eval" in path_low else delivered
        st = stem_of(name)
        if len(st) >= 4: bucket[st] = bucket.get(st, 0) + 1
    return delivered, evaluated

def main():
    clone("https://github.com/crustio/Crust-Grants-Program.git", GP, "main")
    clone("https://github.com/crustio/Crust-Grant-Milestone-Delivery.git", GMD, "main")

    delivered, evaluated = delivery_stems()

    def find(pid_norm, bucket):
        best = 0
        for st, n in bucket.items():
            if st == pid_norm or (len(pid_norm) >= 5 and pid_norm in st) or (len(st) >= 5 and st in pid_norm):
                best = max(best, n)
        return best

    rows = []
    app_glob = glob.glob(str(GP / "applications" / "*.md")) or glob.glob(str(GP / "**" / "*.md"), recursive=True)
    for p in app_glob:
        name = os.path.basename(p); low = name.lower()
        if low in ("readme.md", "application_template.md", "application-template.md", "index.md"): continue
        if "template" in low: continue
        txt = open(p, encoding="utf-8", errors="ignore").read()
        st = norm(re.sub(r"\.md$", "", name, flags=re.I))
        ms = re.search(r"(?im)^\s*[-*]?\s*\*{0,2}status\*{0,2}\s*:?\*{0,2}\s*\[?([A-Za-z ]+)", txt[:4000])
        status = ms.group(1).strip() if ms else ""
        terminated = bool(re.search(r"(?i)terminat|deprecat|withdraw|cancel", status))
        fte, months, pm = app_effort(txt)
        repos = app_repos(txt)
        nd, ne = find(st, delivered), find(st, evaluated)
        if terminated:  verdict = "REJECT_terminated"
        elif nd >= 1:   verdict = "DELIVERED"
        elif ne >= 1:   verdict = "evaluated_no_delivery_file"
        else:           verdict = "no_delivery_found"
        rows.append(dict(project=re.sub(r"\.md$", "", name, flags=re.I), verdict=verdict,
                         n_delivery_files=nd, n_evaluations=ne, status=status,
                         terminated=("Y" if terminated else ""), app_fte=(fte or ""),
                         app_months=(months or ""), app_pm=(pm or ""), n_app_repos=len(repos),
                         repo_url=first_repo(txt), all_repos="; ".join(sorted(repos))))

    vorder = {"DELIVERED": 0, "evaluated_no_delivery_file": 1, "no_delivery_found": 2, "REJECT_terminated": 3}
    def key(x):
        actionable = (x["app_pm"] != "" and x["n_app_repos"] <= 2)
        return (vorder.get(x["verdict"], 9), 0 if actionable else 1, -(x["n_delivery_files"] or 0))
    rows.sort(key=key)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols = ["project","verdict","n_delivery_files","n_evaluations","status","terminated",
            "app_fte","app_months","app_pm","n_app_repos","repo_url","all_repos"]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in rows: w.writerow(r)

    deliv = [x for x in rows if x["verdict"] == "DELIVERED"]
    clean = [x for x in deliv if x["app_pm"] != "" and x["n_app_repos"] <= 2]
    print(f"=== Crust prescreen: {len(rows)} applications | DELIVERED {len(deliv)} | "
          f"REJECT_terminated {sum(1 for x in rows if x['verdict']=='REJECT_terminated')} ===")
    print(f"admit-ready (DELIVERED + stated FTE pm + <=2 repos): {len(clean)}")
    print(f"{'project':34}{'pm':>7}{'fte':>6}{'mo':>6}{'repos':>6}")
    for x in clean[:40]:
        print(f"  {x['project'][:32]:34}{str(x['app_pm']):>7}{str(x['app_fte']):>6}{str(x['app_months']):>6}{x['n_app_repos']:>6}")
    print(f"\nwrote {OUT}")

if __name__ == "__main__":
    main()
