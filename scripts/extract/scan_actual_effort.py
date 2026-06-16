#!/usr/bin/env python3
"""
scan_actual_effort.py  —  mine ACTUAL logged effort from W3F milestone-DELIVERY documents.
=========================================================================================
W3F grant rules require each milestone delivery to report the *time spent on each task*. Where a grantee
actually wrote it down, the delivery doc carries a PUBLIC, ON-RECORD, ACTUAL effort figure for a COMPLETED
project whose repo we already have — i.e. exactly the hard-to-locate gold the planned applications lack.

This scans every deliveries/*.md (and evaluations/*.md) in w3f/Grant-Milestone-Delivery for real time/effort
signals, extracts the figure, and ranks docs that genuinely report actual hours/person-months/man-days.
Output: data/calibration/delivery_actuals.csv  (triage → promote matching pilots Extended→GOLD).
stdlib only. Runs in CI (needs git clone).
"""
import csv, os, re, subprocess, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/calibration/delivery_actuals.csv"
WORK = Path("/tmp/w3f_actuals"); WORK.mkdir(parents=True, exist_ok=True)
GMD = WORK / "Grant-Milestone-Delivery"

def clone(url, dest):
    if not dest.exists():
        subprocess.run(["git", "clone", "--depth", "1", url, str(dest)], check=True)

# ACTUAL-effort signals in a delivery report
HOURS_A = re.compile(r"([\d][\d,\.]{0,6})\s*(?:work[\s-]?hours?|dev(?:eloper|elopment)?[\s-]?hours?|man[\s-]?hours?|person[\s-]?hours?|\bhours?\b|\bhrs?\b)", re.I)
HOURS_B = re.compile(r"(?:time spent|hours?(?:\s*spent)?|effort)\s*[:|]?\s*([\d][\d,\.]{0,6})", re.I)
PM_RE   = re.compile(r"([\d][\d,\.]{0,4})\s*(?:person[\s-]?months?|man[\s-]?months?|dev(?:eloper)?[\s-]?months?)", re.I)
DAYS_RE = re.compile(r"([\d][\d,\.]{0,5})\s*(?:person[\s-]?days?|man[\s-]?days?|dev(?:eloper)?[\s-]?days?|working[\s-]?days?)", re.I)
TIMECOL = re.compile(r"(?im)\|[^\n|]*\b(time spent|hours?|effort|man[\s-]?days?|person[\s-]?months?)\b[^\n|]*\|")  # a table column header
ACTUALW = re.compile(r"(?i)\b(time spent|actually spent|actual (?:effort|hours|time)|hours spent|logged)\b")

def num(m):
    try: return float(m.group(1).replace(",", ""))
    except (ValueError, AttributeError): return None

def stem(fn):
    base = re.sub(r"\.md$", "", fn, flags=re.I)
    base = re.sub(r"(_|-)(milestone|m)(_|-)?\d+.*$|(_|-)\d+([_-][a-z0-9]+)?$", "", base, flags=re.I)
    return base

def scan(txt):
    h = num(HOURS_A.search(txt)) or num(HOURS_B.search(txt))
    pm = num(PM_RE.search(txt))
    dd = num(DAYS_RE.search(txt))
    has_col = bool(TIMECOL.search(txt))
    has_word = bool(ACTUALW.search(txt))
    # best PM estimate: hours/152, or person-months, or days/19 (Boehm 152h/PM = 19 8h-days)
    pm_est = ""
    if h and 30 <= h <= 100000:   pm_est = round(h/152.0, 2)
    elif pm and 0.1 <= pm <= 400:  pm_est = round(pm, 2)
    elif dd and 1 <= dd <= 8000:   pm_est = round(dd/19.0, 2)
    return dict(hours=(int(h) if h else ""), person_months=(pm or ""), person_days=(dd or ""),
                pm_est=pm_est, has_time_col=("Y" if has_col else ""), has_actual_word=("Y" if has_word else ""))

def main():
    clone("https://github.com/w3f/Grant-Milestone-Delivery.git", GMD)
    rows = []
    for folder in ("deliveries", "evaluations"):
        for p in glob.glob(str(GMD / folder / "*.md")):
            name = os.path.basename(p)
            if name.lower() in ("readme.md", "milestone-delivery-template.md", "evaluation-template.md"): continue
            txt = open(p, encoding="utf-8", errors="ignore").read()
            s = scan(txt)
            # keep only docs that plausibly report ACTUAL effort
            score = (2 if s["pm_est"] != "" else 0) + (1 if s["has_time_col"] else 0) + (1 if s["has_actual_word"] else 0)
            if score >= 2:
                rows.append(dict(folder=folder, file=name, project=stem(name), score=score, **s))
    # dedupe by project, keep highest score
    best = {}
    for r in rows:
        k = r["project"].lower()
        if k not in best or r["score"] > best[k]["score"]: best[k] = r
    out = sorted(best.values(), key=lambda r: (-r["score"], -(float(r["pm_est"]) if r["pm_est"] != "" else 0)))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols = ["project", "file", "folder", "score", "pm_est", "hours", "person_months", "person_days", "has_time_col", "has_actual_word"]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in out: w.writerow({c: r.get(c, "") for c in cols})

    strong = [r for r in out if r["pm_est"] != "" and (r["has_time_col"] or r["has_actual_word"])]
    print(f"=== delivery-doc ACTUAL-effort scan: {len(out)} candidate docs (score>=2) | strong: {len(strong)} ===")
    print(f"{'project':34}{'pm_est':>7}{'hours':>8}  flags")
    for r in strong[:50]:
        print(f"  {r['project'][:32]:34}{str(r['pm_est']):>7}{str(r['hours']):>8}  col={r['has_time_col']} word={r['has_actual_word']} {r['file']}")
    print(f"\nwrote {OUT}")

if __name__ == "__main__":
    main()
