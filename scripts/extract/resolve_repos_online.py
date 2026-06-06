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

# commit URL that also captures which repo it belongs to (owner/repo)
COMMIT_REPO = re.compile(r"github\.com/([A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+)/(?:tree|commit)/([0-9a-f]{7,40})", re.I)

def commit_for_repo(text, repo_url):
    """Return a commit sha ONLY if it belongs to repo_url (avoids cross-repo mis-pin)."""
    target = repo_url.split("github.com/")[-1].rstrip("/").replace(".git", "").lower()
    for m in COMMIT_REPO.finditer(text):
        if m.group(1).rstrip("/").replace(".git", "").lower() == target:
            return m.group(2)
    return ""

def delivery_file_date(repo_root, file_path):
    """Git commit date (YYYY-MM-DD) of the delivery file = when the milestone was submitted."""
    rel = os.path.relpath(file_path, repo_root)
    r = subprocess.run(["git", "log", "-1", "--format=%ad", "--date=short", "--", rel],
                       cwd=repo_root, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""

def match_delivery_files(files, pid, pname):
    """Return delivery files whose name (before -milestone) matches the project."""
    # prefix-based to avoid substring collisions (e.g. 'lastic' in 'eLASTIClabs',
    # 'tdot' in 'daTDOT'). A delivery file matches only if its stem starts with the
    # project key (or vice-versa), or they share a >=6-char prefix.
    keys = [k for k in {slug(pid), slug(pname)} if len(k) >= 4]
    hits = []
    for f in files:
        stem = slug(os.path.basename(f).split("-milestone")[0].replace(".md", ""))
        if not stem: continue
        for k in keys:
            if (stem == k or stem.startswith(k)
                    or (len(k) >= 6 and k.startswith(stem))
                    or (len(stem) >= 6 and len(k) >= 6 and stem[:6] == k[:6])):
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
        # respect human EXCLUSIONS: do not re-resolve or fill these
        if "EXCLUDED" in (r.get("notes", "") or "").upper():
            out.append(dict(project_id=pid, best_repo=r.get("repo_url", ""), best_commit="",
                            delivered_date="", n_delivery_files=0, sources="EXCLUDED - skipped"))
            print(f"  {pid:22} EXCLUDED - skipped")
            continue
        repo = r.get("repo_url", "").strip(); commit = r.get("commit_sha", "").strip()
        srcs = []; delivered = ""
        matched = match_delivery_files(deliv_files, pid, pname)
        for f in matched:
            txt = open(f, encoding="utf-8", errors="ignore").read()
            rr = repos_in_text(txt)
            if rr and not repo: repo = rr[0]
            for u in rr: srcs.append(f"deliv:{os.path.basename(f)}:{u}")
            d = delivery_file_date(deliv, f)
            if d and d > delivered: delivered = d           # latest milestone-submission date
        # a commit is only trustworthy if it belongs to the chosen repo
        if repo and not commit:
            for f in matched:
                c = commit_for_repo(open(f, encoding="utf-8", errors="ignore").read(), repo)
                if c: commit = c; break
        if not repo and have_g:  # fallback: application repo links
            for apf in glob.glob(os.path.join(grants, "applications", "*.md")):
                if slug(os.path.basename(apf).replace(".md", "")) == slug(pid):
                    rr = repos_in_text(open(apf, encoding="utf-8", errors="ignore").read())
                    if rr: repo = rr[-1]; srcs.append(f"app:{os.path.basename(apf)}:{rr[-1]}")
                    break
        out.append(dict(project_id=pid, best_repo=repo, best_commit=commit,
                        delivered_date=delivered, n_delivery_files=len(matched),
                        sources=" | ".join(srcs[:8])))
        if a.fill:
            if repo and not r.get("repo_url", "").strip(): r["repo_url"] = repo
            if commit and not r.get("commit_sha", "").strip(): r["commit_sha"] = commit
            if delivered and not r.get("cutoff_date", "").strip(): r["cutoff_date"] = delivered
        print(f"  {pid:22} repo={repo or 'NONE':40} commit={(commit[:10] or '-')} delivered={delivered or '-'}")

    os.makedirs("reports", exist_ok=True)
    with open("reports/resolved_repos.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["project_id","best_repo","best_commit","delivered_date","n_delivery_files","sources"])
        w.writeheader(); w.writerows(out)
    if a.fill:
        with open("projects_manifest.online.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    nr = sum(1 for o in out if o["best_repo"]); nc = sum(1 for o in out if o["best_commit"])
    print(f"Resolved repo for {nr}/{len(rows)}, commit for {nc}/{len(rows)} -> reports/resolved_repos.csv")

if __name__ == "__main__":
    main()
