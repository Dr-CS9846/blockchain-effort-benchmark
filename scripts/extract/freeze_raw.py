#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
freeze_raw.py  —  snapshot the RAW sources so the chain is frozen at the source.
For each project in the manifest, fetch verbatim copies of:
  * the W3F application markdown          -> data/raw/applications/<project_id>.md
  * each milestone-delivery record        -> data/raw/deliveries/<file>.md
and record source_url, captured_at (UTC), sha256, bytes in data/raw/RAW_MANIFEST.csv.

The sha256 lets anyone confirm that the extracted fields derive from exactly these
bytes. Runs where network is reliable (CI or locally); deterministic given the
upstream files. urllib only; no third-party deps.

USAGE
  python scripts/extract/freeze_raw.py --manifest data/calibration/projects_manifest.csv
"""
import argparse, csv, hashlib, os, sys, urllib.request
from datetime import datetime, timezone

UA = {"User-Agent": "freeze-raw/1.0"}
DELIV_BASE = "https://raw.githubusercontent.com/w3f/Grant-Milestone-Delivery/master/deliveries/"
RAW = "data/raw"

def raw_url(app_url):
    u = (app_url or "").strip()
    if not u: return ""
    if not u.startswith("http"): u = "https://" + u
    return u.replace("https://github.com/", "https://raw.githubusercontent.com/").replace("/blob/", "/")

def fetch_bytes(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def sha256(b): return hashlib.sha256(b).hexdigest()

def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f: f.write(data)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="data/calibration/projects_manifest.csv")
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.manifest)))
    records = []
    now = datetime.now(timezone.utc).isoformat()
    for r in rows:
        pid = r["project_id"]
        # application
        ru = raw_url(r.get("application_url", ""))
        if ru:
            try:
                b = fetch_bytes(ru)
                p = f"{RAW}/applications/{pid}.md"; save(p, b)
                records.append([p, ru, now, sha256(b), len(b)])
                print(f"  app   {pid:22} {len(b):>7}B  {sha256(b)[:12]}")
            except Exception as e:
                print(f"  [WARN] app {pid}: {str(e)[:60]}")
        # deliveries (milestones 1..5)
        for k in range(1, 6):
            url = f"{DELIV_BASE}{pid}-milestone_{k}.md"
            try:
                b = fetch_bytes(url)
            except Exception:
                continue
            p = f"{RAW}/deliveries/{pid}-milestone_{k}.md"; save(p, b)
            records.append([p, url, now, sha256(b), len(b)])
            print(f"  deliv {pid:22} m{k} {len(b):>6}B  {sha256(b)[:12]}")
    os.makedirs(RAW, exist_ok=True)
    with open(f"{RAW}/RAW_MANIFEST.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["path", "source_url", "captured_at", "sha256", "bytes"])
        w.writerows(records)
    print(f"Froze {len(records)} raw files -> {RAW}/RAW_MANIFEST.csv")

if __name__ == "__main__":
    main()
