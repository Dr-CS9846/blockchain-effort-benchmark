#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resolve_repos_online.py  —  robust delivered-repo + commit resolver
===================================================================
The W3F milestone-delivery filenames are irregular (e.g. some are
"<Project>-milestone_1.md", others embed the full project title), so guessing
URLs fails. This resolver instead CLONES the delivery + grants repos (reliable in
GitHub Actions / locally; no API rate limits), lists deliveries/, fuzzy-matches
each manifest project to its delivery file(s), and extracts the delivered
repository URL and — where the delivery pins it — the commit (/tree|/commit/<sha>).
Falls back to the grant application's repo links when no delivery file is found.

Writes reports/resolved_repos.csv (committed, for human review). With --fill it
also writes projects_manifest.online.csv with repo_url/commit_sha pre-filled.

Human review is still expected before measurement; this produces the candidate
list at scale (13 -> 150) without rate limits.
"""
import argparse, csv, glob, os, re, subprocess, sys

GH = re.compile(r"https?://github\.com/([A-Za-z0-9_.\-]+)/([A-Za-z0-9_.\-]+)", re.I)
COMMIT = re.compile(r"github\.com/[^/\s)]+/[^/\s)]+/(?:tree|commit)/([0-9a-f]{7,40})", re.I)
EXCL_OWNERS = {"w3f"}
EXCL_REPONAMES = {"grants-program", "grant-milestone-delivery"}
DELIV_URL = "https://github.com/w3f/Grant-Milestone-Delivery.git"
GRANTS_URL = "https://github.com/w3f/Grants-Program.git"

def slug(s): return re.sub(r"[^a-z0-9]", "", (s or "").lower())

def clone(url, dest):
    if os.path.isdir(os.path.join(dest, ".git")): return True
    try:
        rc = subprocess.run(["git", "clone", "--depth", "1", url, dest],
                            capture_output=True, text=True, timeout=600).returncode
        return rc == 0
    except Exception:
        return False

def repos_in_text(t):
    out = []
    for m in GH.finditer(t):
        o, r = m.group(1), m.group(2)
        r = r.rstrip(").,").replace(".git", "")
        if o.lower() in EXCL_OWNERS or r.lower() in EXCL_REPONAMES: continue
        out.append(f"https://github.com/{o}/{r}")
    seen = set(); return [u for u in out if not (u in seen or seen.add(u))]

def commit_in_text(t):
    m = COMMIT.search(t); return m.group(1) if m else ""

def match_delivery_files(files, pid, pname):
    """Return delivery files whose name (before -milestone) matches the project."""
    keys = [k for k in {slug(pid), slug(pname)} if k]
    hits = []
    for f in files:
        stem = slug(os.path.basename(f).split("-milestone")[0].replace(".md", ""))
        if not stem: continue
        for k in keys:
            if stem == k or stem in k or k in stem or (len(stem) >= 5 and stem[:6] == k[:6]):
                hits.append(f); break
    return sorted(set(hits))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="data/calibration/projects_manifest.csv")
    ap.add_argument("--cache", default="resolve_cache")
    ap.add_argument("--fill", action="store_true")
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.manifest)))

    deliv = os.path.join(a.cache, "deliv"); grants = os.path.join(a.cache, "grants")
    os.makedirs(a.cache, exist_ok=True)
    have_d = clone(DELIV_URL, deliv); have_g = clone(GRANTS_URL, grants)
    if not have_d: print("[WARN] could not clone delivery repo; delivery resolution skipped.")
    deliv_files = glob.glob(os.path.join(deliv, "deliveries", "*.md")) if have_d else []

    out = []
    for r in rows:
        pid = r["project_id"]; pname = r.get("project_name", pid)
        repo = r.get("repo_url", "").strip(); commit = r.get("commit_sha", "").strip()
        srcs = []
        matched = match_delivery_files(deliv_files, pid, pname)
        for f in matched:
            txt = open(f, encoding="utf-8", errors="ignore").read()
            rr = repos_in_text(txt)
            if rr and not repo: repo = rr[0]
            for u in rr: srcs.append(f"deliv:{os.path.basename(f)}:{u}")
            c = commit_in_text(txt)
            if c and not commit: commit = c
        if not repo and have_g:  # fallback: application repo links
            for apf in glob.glob(os.path.join(grants, "applications", "*.md")):
                if slug(os.path.basename(apf).replace(".md", "")) == slug(pid):
                    rr = repos_in_text(open(apf, encoding="utf-8", errors="ignore").read())
                    if rr: repo = rr[-1]; srcs.append(f"app:{os.path.basename(apf)}:{rr[-1]}")
                    break
        out.append(dict(project_id=pid, best_repo=repo, best_commit=commit,
                        n_delivery_files=len(matched), sources=" | ".join(srcs[:8])))
        if a.fill:
            if repo: r["repo_url"] = repo
            if commit: r["commit_sha"] = commit
        print(f"  {pid:22} repo={repo or 'NONE':48} commit={(commit[:12] or '-')}")

    os.makedirs("reports", exist_ok=True)
    with open("reports/resolved_repos.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["project_id","best_repo","best_commit","n_delivery_files","sources"])
        w.writeheader(); w.writerows(out)
    if a.fill:
        with open("projects_manifest.online.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    nr = sum(1 for o in out if o["best_repo"]); nc = sum(1 for o in out if o["best_commit"])
    print(f"Resolved repo for {nr}/{len(rows)}, commit for {nc}/{len(rows)} -> reports/resolved_repos.csv")

if __name__ == "__main__":
    main()
