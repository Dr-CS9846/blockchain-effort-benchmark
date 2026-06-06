#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resolve_repos_online.py  —  scalable, reproducible repo + commit resolver
=========================================================================
For every row in projects_manifest.csv this resolves the DELIVERED repository
and, where possible, the exact delivered COMMIT, by reading two public sources
and ranking candidates by how authoritative the source is:

  1. W3F milestone-delivery records  (deliveries/<project_id>-milestone_*.md)
     -> AUTHORITATIVE: states the delivered repo and often a /tree/<sha> or
        /commit/<sha> pin. Ranked highest.
  2. The grant application  (application_url)
     -> SUPPORTING: "Development Status" / milestone "Source code" sections.
        Ranked next; "Team Code Repos" (pre-existing projects) ranked lowest.

A human still confirms before measurement, but the top candidate + commit are
usually correct. Runs anywhere with web access (your machine or GitHub Actions);
scales 13 -> 150 unchanged; deterministic given the upstream files.

Output:
  repo_candidates_online.csv  — project_id, best_repo, best_commit, ranked_candidates
  (with --fill, also writes best_repo/best_commit into empty cells of
   projects_manifest.online.csv for review)

USAGE
  python resolve_repos_online.py --manifest data/calibration/projects_manifest.csv
  python resolve_repos_online.py --manifest data/calibration/projects_manifest.csv --fill
"""
import argparse, csv, re, sys, urllib.request

UA = {"User-Agent": "repo-resolver/1.0"}
REPO_RE = re.compile(r"https?://github\.com/([A-Za-z0-9_.\-]+)/([A-Za-z0-9_.\-]+)", re.I)
# delivered commit, if the link pins one
COMMIT_RE = re.compile(r"github\.com/[^/\s)]+/[^/\s)]+/(?:tree|commit)/([0-9a-f]{7,40})", re.I)
EXCLUDE_OWNERS = {"w3f"}
EXCLUDE_REPONAMES = {"grants-program", "grant-milestone-delivery"}
DELIV_BASE = "https://raw.githubusercontent.com/w3f/Grant-Milestone-Delivery/master/deliveries/"
# application-section ranking (lower = stronger signal of the delivered repo)
SECTION_RANK = [
    (re.compile(r"development status", re.I), 1),
    (re.compile(r"source code|deliverable|milestone", re.I), 2),
    (re.compile(r"team code repos|repositor", re.I), 4),
]
DEFAULT_RANK = 3
DELIVERY_RANK = 0  # authoritative — beats every application section

def raw_url(app_url):
    u = app_url.strip()
    if not u: return ""
    if not u.startswith("http"): u = "https://" + u
    u = u.replace("https://github.com/", "https://raw.githubusercontent.com/")
    u = u.replace("/blob/", "/")
    return u

def section_rank_for(heading):
    for rx, rank in SECTION_RANK:
        if rx.search(heading): return rank
    return DEFAULT_RANK

def _repos_in(line):
    out = []
    for m in REPO_RE.finditer(line):
        owner, repo = m.group(1), m.group(2)
        repo = repo.rstrip(").,").replace(".git", "")
        if owner.lower() in EXCLUDE_OWNERS: continue
        if repo.lower() in EXCLUDE_REPONAMES: continue
        out.append(f"https://github.com/{owner}/{repo}")
    return out

def extract_from_application(md_text):
    """Return {repo_url: rank} from a grant application, ranked by section."""
    best = {}
    cur = DEFAULT_RANK
    for line in md_text.splitlines():
        if line.lstrip().startswith("#"):
            cur = section_rank_for(line); continue
        for url in _repos_in(line):
            if url not in best or cur < best[url]: best[url] = cur
    return best

def extract_from_delivery(md_text):
    """Return ({repo_url: DELIVERY_RANK}, commit_or_None) from a delivery record."""
    repos = {}
    commit = None
    for line in md_text.splitlines():
        for url in _repos_in(line):
            repos[url] = DELIVERY_RANK
        m = COMMIT_RE.search(line)
        if m and commit is None:
            commit = m.group(1)
    return repos, commit

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")

def resolve_one(row):
    """Return (best_repo, best_commit, ranked_list)."""
    cand = {}      # repo_url -> rank
    commit = ""
    # 1. delivery records (authoritative); try milestones 1..5
    pid = row["project_id"]
    for k in range(1, 6):
        url = f"{DELIV_BASE}{pid}-milestone_{k}.md"
        try:
            repos, c = extract_from_delivery(fetch(url))
        except Exception:
            continue
        for u, rk in repos.items():
            cand[u] = min(rk, cand.get(u, 99))
        if c and not commit:
            commit = c
    # 2. application (supporting)
    ru = raw_url(row.get("application_url", ""))
    if ru:
        try:
            for u, rk in extract_from_application(fetch(ru)).items():
                cand[u] = min(rk, cand.get(u, 99))
        except Exception as e:
            print(f"  [WARN] {pid}: application fetch failed ({str(e)[:60]})")
    ranked = sorted(cand.items(), key=lambda kv: kv[1])
    best = ranked[0][0] if ranked else ""
    return best, commit, ranked

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="projects_manifest.csv")
    ap.add_argument("--fill", action="store_true")
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.manifest)))
    out = []
    for r in rows:
        best, commit, ranked = resolve_one(r)
        out.append((r["project_id"], best, commit,
                    " | ".join(f"{u}(r{rk})" for u, rk in ranked) or "NONE"))
        if a.fill:
            if best and not r.get("repo_url", "").strip(): r["repo_url"] = best
            if commit and not r.get("commit_sha", "").strip(): r["commit_sha"] = commit
        print(f"  {r['project_id']:22} -> {best or 'NONE':45} {('@'+commit) if commit else ''}")
    with open("repo_candidates_online.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["project_id", "best_repo", "best_commit", "ranked_candidates"])
        w.writerows(out)
    if a.fill:
        with open("projects_manifest.online.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
        print("Wrote projects_manifest.online.csv (review before using).")
    nr = sum(1 for _, b, _, _ in out if b)
    nc = sum(1 for _, _, c, _ in out if c)
    print(f"Resolved repo for {nr}/{len(rows)} and commit for {nc}/{len(rows)} projects.")

if __name__ == "__main__":
    main()
