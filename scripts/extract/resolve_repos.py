#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resolve_repos.py  —  Step 1 helper (optional but recommended)
=============================================================
Suggests candidate delivered-repository URLs for each project by scanning the
local W3F application markdown files and (if present) the milestone-delivery
markdown. It does NOT guess: it extracts real GitHub URLs found in those files so
you can confirm the correct one and paste it into projects_manifest.csv.

It writes `repo_candidates.csv` (project_id -> list of github URLs found) and,
where exactly one strong candidate exists, fills `repo_url` in a copy of the
manifest (`projects_manifest.suggested.csv`) for you to review.

Usage:
    python resolve_repos.py \
        --apps   ../01_raw_applications/Grants-Program/applications \
        --deliv  ../02_raw_deliveries/Grant-Milestone-Delivery/deliveries \
        --manifest projects_manifest.csv
"""
import argparse, csv, os, re, glob, json

GH = re.compile(r"https?://github\.com/[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+", re.I)
SKIP = ("w3f/grants-program", "w3f/grant-milestone-delivery")  # not delivery repos

def urls_in_text(t):
    out=[]
    for m in GH.findall(t or ""):
        u=m.rstrip("/.").replace(".git","")
        if not any(s in u.lower() for s in SKIP):
            out.append(u)
    # dedupe, preserve order
    seen=set(); uniq=[u for u in out if not (u in seen or seen.add(u))]
    return uniq

def slug(s): return re.sub(r"[^a-z0-9]","",s.lower())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--apps", default="../01_raw_applications/Grants-Program/applications")
    ap.add_argument("--deliv", default="../02_raw_deliveries/Grant-Milestone-Delivery/deliveries")
    ap.add_argument("--manifest", default="projects_manifest.csv")
    a=ap.parse_args()

    # index application/delivery files by filename slug
    files=[]
    for d in (a.apps, a.deliv):
        if os.path.isdir(d):
            files += glob.glob(os.path.join(d, "*.md"))
    text_by_slug={}
    for fp in files:
        try: txt=open(fp, encoding="utf-8", errors="ignore").read()
        except Exception: continue
        text_by_slug.setdefault(slug(os.path.splitext(os.path.basename(fp))[0]), []).append(txt)

    rows=list(csv.DictReader(open(a.manifest)))
    cand_rows=[]
    for r in rows:
        keys={slug(r["project_id"]), slug(r["project_name"])}
        found=[]
        for k,texts in text_by_slug.items():
            if any(key and (key in k or k in key) for key in keys):
                for t in texts: found += urls_in_text(t)
        seen=set(); found=[u for u in found if not (u in seen or seen.add(u))]
        cand_rows.append((r["project_id"], found))
        if len(found)==1 and not r["repo_url"]:
            r["repo_url"]=found[0]; r["notes"]=(r["notes"]+" repo auto-suggested").strip()

    with open("repo_candidates.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["project_id","candidate_github_urls"])
        for pid,urls in cand_rows: w.writerow([pid, " | ".join(urls) if urls else "NONE_FOUND"])
    with open("projects_manifest.suggested.csv","w",newline="") as f:
        w=csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

    n_one=sum(1 for _,u in cand_rows if len(u)==1)
    print(f"Scanned {len(files)} md files. {n_one}/{len(rows)} projects have exactly one candidate.")
    print("Review repo_candidates.csv, then confirm repo_url in projects_manifest.csv.")

if __name__=="__main__": main()
