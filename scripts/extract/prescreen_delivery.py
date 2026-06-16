#!/usr/bin/env python3
"""
Delivery-verified pre-screen over the W3F census candidates.

Cross-references each census project against the W3F Grant-Milestone-Delivery repo
(deliveries/ + evaluations/) and the Grants-Program application `Status` header, so that
deep hand-verification only targets grants that were ACTUALLY accepted/delivered
(no more terminated/partial grants like Spacewalk slipping through the basic-clean filter).

Decisive signal: a delivered grant has >=1 file in deliveries/ (and usually an evaluation);
terminated/undelivered grants have none. Application `Status: Terminated` is a secondary flag.

Runs in CI (needs git clone + network). Emits data/calibration/census_prescreen.csv.
"""
import csv, os, re, subprocess, sys, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]            # 06_measurement/
CENSUS = ROOT / "data/calibration/measurements_census.csv"
OUT = ROOT / "data/calibration/census_prescreen.csv"
WORK = Path("/tmp/w3f_prescreen"); WORK.mkdir(parents=True, exist_ok=True)

GMD = WORK / "Grant-Milestone-Delivery"
GP  = WORK / "Grants-Program"

def clone(url, dest):
    if dest.exists(): return
    subprocess.run(["git", "clone", "--depth", "1", url, str(dest)], check=True)

def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())

# strip milestone/version suffixes from a delivery/evaluation filename stem
SUFFIX = re.compile(r"(_|-)(milestone|m)(_|-)?\d+.*$|(_|-)\d+([_-][a-z0-9]+)?$", re.I)
def stem_of(fname: str) -> str:
    base = re.sub(r"\.md$", "", fname, flags=re.I)
    base = SUFFIX.sub("", base)
    return norm(base)

def main():
    clone("https://github.com/w3f/Grant-Milestone-Delivery.git", GMD)
    clone("https://github.com/w3f/Grants-Program.git", GP)

    # delivered/evaluated stems -> count of milestone files
    delivered = {}   # stem -> n delivery files
    evaluated = {}   # stem -> n evaluation files
    for folder, bucket in [("deliveries", delivered), ("evaluations", evaluated)]:
        for p in glob.glob(str(GMD / folder / "*.md")):
            name = os.path.basename(p)
            if name.lower() in ("readme.md", "milestone-delivery-template.md", "evaluation-template.md"):
                continue
            st = stem_of(name)
            if len(st) >= 4:
                bucket[st] = bucket.get(st, 0) + 1

    # application Status headers: app_stem -> status string
    app_status = {}
    for p in glob.glob(str(GP / "applications" / "*.md")):
        name = os.path.basename(p)
        if name.lower() in ("index.md", "application-template.md"): continue
        st = norm(re.sub(r"\.md$", "", name, flags=re.I))
        try:
            txt = open(p, encoding="utf-8", errors="ignore").read(4000)
        except Exception:
            txt = ""
        m = re.search(r"(?im)^\s*[-*]?\s*\*{0,2}status\*{0,2}\s*:?\*{0,2}\s*\[?([A-Za-z ]+)", txt)
        app_status[st] = (m.group(1).strip() if m else "")

    def match_count(pid_norm, bucket):
        # exact, or containment either way (handles pontem<->pontemnetwork), guarded by length
        best = 0
        for st, n in bucket.items():
            if st == pid_norm or (len(pid_norm) >= 5 and pid_norm in st) or (len(st) >= 5 and st in pid_norm):
                best = max(best, n)
        return best

    def status_for(pid_norm):
        for st, s in app_status.items():
            if st == pid_norm or (len(pid_norm) >= 5 and pid_norm in st) or (len(st) >= 5 and st in pid_norm):
                if s: return s
        return ""

    rows = []
    seen = set()
    for r in csv.DictReader(open(CENSUS, encoding="utf-8")):
        pid = (r.get("project_id") or "").strip()
        if not pid or pid in seen: continue
        seen.add(pid)
        pn = norm(pid)
        nd = match_count(pn, delivered)
        ne = match_count(pn, evaluated)
        status = status_for(pn)
        terminated = bool(re.search(r"(?i)terminat|deprecat|withdraw|cancel", status))
        if terminated:                      verdict = "REJECT_terminated"
        elif nd >= 1:                        verdict = "DELIVERED"
        elif ne >= 1:                        verdict = "evaluated_no_delivery_file"
        else:                                verdict = "no_delivery_found"
        rows.append({
            "project_id": pid, "verdict": verdict, "n_delivery_files": nd,
            "n_evaluations": ne, "app_status": status, "terminated": "Y" if terminated else "",
            "repo_url": (r.get("repo_url") or "").strip(),
            "planned_pm_census": (r.get("planned_pm") or "").strip(),
            "commit_source": (r.get("commit_source") or "").strip(),
            "equivalent_sloc": (r.get("equivalent_sloc") or "").strip(),
        })

    order = {"DELIVERED": 0, "evaluated_no_delivery_file": 1, "no_delivery_found": 2, "REJECT_terminated": 3}
    rows.sort(key=lambda x: (order.get(x["verdict"], 9), -float(x["n_delivery_files"] or 0)))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    n = len(rows)
    delivered_n = sum(1 for x in rows if x["verdict"] == "DELIVERED")
    term_n = sum(1 for x in rows if x["verdict"] == "REJECT_terminated")
    nofile_n = sum(1 for x in rows if x["verdict"] == "no_delivery_found")
    print(f"=== prescreen: {n} census projects ===")
    print(f"DELIVERED={delivered_n}  evaluated_only={sum(1 for x in rows if x['verdict']=='evaluated_no_delivery_file')}"
          f"  no_delivery_found={nofile_n}  REJECT_terminated={term_n}")
    print(f"deliveries indexed: {sum(delivered.values())} files / {len(delivered)} stems")
    print("--- top 25 DELIVERED ---")
    for x in [r for r in rows if r['verdict']=='DELIVERED'][:25]:
        print(f"  {x['project_id']:30} deliv={x['n_delivery_files']} pm~{x['planned_pm_census']:>5} {x['repo_url']}")
    print(f"\nwrote {OUT}")

if __name__ == "__main__":
    main()
