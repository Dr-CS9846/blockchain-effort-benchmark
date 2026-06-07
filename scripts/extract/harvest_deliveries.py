#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harvest_deliveries.py  —  pre-registered CENSUS of W3F delivered milestones
===========================================================================
Scans EVERY delivery file in w3f/Grant-Milestone-Delivery (not just a hand list),
groups files by project, and emits a candidate calibration manifest for ALL
projects that pass a pre-registered eligibility rule. This is a census, not a
sample: there is no selection by the analyst, only a transparent inclusion rule.

ELIGIBILITY (pre-registered, applied uniformly):
  E1  Separable primary repo: the project's delivery files reference at least one
      repo in the project's OWN org (a project-controlled repo). The primary repo
      is chosen deterministically (slug-match first, then most-referenced own-org
      repo). Projects whose ONLY referenced repos are shared / third-party
      monorepos (paritytech, AcalaNetwork, ...) are EXCLUDED as un-separable.
  E2  Resolvable delivery date: at least one delivery file has a git add-date
      (the milestone-submission moment). [full-history clone required]
  E3  (applied later, at measurement) source-language KSLOC > 0 and a clonable
      repo. Recorded here but enforced by measure_repos.py.

PLANNED FIELDS come from the matching grant application (applications/<slug>.md):
  Total Estimated Duration, FTE, Total Costs -> planned_duration_months / fte /
  cost; planned_pm = fte * duration. Missing -> blank (planned cross-check only;
  the headline size->effort fit does not need them; the effort window falls back
  to the resolver's commit-date anchor in measure_repos.py).

OUTPUTS:
  data/calibration/projects_manifest.census.csv   (INCLUDED projects, full schema)
  reports/census_audit.csv                         (EVERY project + verdict + reason)

Human review of census_audit.csv is expected before promotion to main.
"""
import argparse, csv, glob, os, re, subprocess, sys

GH = re.compile(r"https?://github\.com/([A-Za-z0-9_.\-]+)/([A-Za-z0-9_.\-]+)", re.I)
COMMIT_REPO = re.compile(
    r"github\.com/([A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+)/(?:tree|commit)/([0-9a-f]{7,40})", re.I)
DELIV_URL = "https://github.com/w3f/Grant-Milestone-Delivery.git"
GRANTS_URL = "https://github.com/w3f/Grants-Program.git"
GENERAL_GRANTS_URL = "https://github.com/w3f/General-Grants-Program.git"  # older grants live here

# repo-name fragments indicating a THIN meta/submission repo (not the substantive code)
META_REPO_HINTS = ("submission", "grant-submission", "proposal", "grants", "application", "docs")

# repos NOT controlled by a grantee -> deliverable inside them is un-separable
SHARED_OWNERS = {
    "paritytech", "acalanetwork", "w3f", "polkadot-fellows", "substrate-developer-hub",
    "paritytech-stg", "open-web3-stack", "polkadot-js", "ipfs", "libp2p",
}
# repo NAMES that are never a grant deliverable (templates / generic)
GENERIC_REPONAMES = {
    "grants-program", "grant-milestone-delivery", "substrate-node-template",
    "substrate-front-end-template", "substrate", "polkadot-sdk", "polkadot",
}

MANIFEST_FIELDS = ["project_id", "project_name", "repo_url", "commit_sha", "cutoff_date",
                   "since_date", "subdir", "planned_fte", "planned_duration_months",
                   "planned_pm", "cost_usd", "application_url", "notes"]
AUDIT_FIELDS = ["project_id", "verdict", "reason", "primary_repo", "commit", "delivered_date",
                "n_delivery_files", "own_org_repos", "shared_repos", "planned_pm"]


def slug(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def clone(url, dest, shallow):
    if os.path.isdir(os.path.join(dest, ".git")):
        return True
    cmd = ["git", "clone"] + (["--depth", "1"] if shallow else []) + [url, dest]
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=1800).returncode == 0
    except Exception:
        return False


def project_key(filename):
    """Strip trailing milestone markers to get a stable project key.
    Handles: _Milestone1, _Milestone_1, -Milestone_1, -milestone-1, -1, _1, -m1."""
    stem = re.sub(r"\.md$", "", filename, flags=re.I)
    # remove a trailing milestone marker (with optional sub-number like 3-4)
    stem = re.sub(r"[-_ ]*milestones?[-_ ]*\d+([-_]\d+)?$", "", stem, flags=re.I)
    stem = re.sub(r"[-_ ]*m\d+$", "", stem, flags=re.I)          # -m1
    stem = re.sub(r"[-_]\d+([-_]\d+)?$", "", stem)               # trailing -1 / _1 / -3-4
    return stem


def repos_in_text(t):
    """All github repos referenced, as (owner, repo), excluding generic/template names."""
    out = []
    for m in GH.finditer(t):
        o, r = m.group(1), m.group(2)
        r = r.rstrip(").,").replace(".git", "")
        if r.lower() in GENERIC_REPONAMES:
            continue
        out.append((o, r))
    seen = set()
    return [x for x in out if not (x in seen or seen.add(x))]


def commit_for_repo(text, owner_repo):
    target = owner_repo.lower()
    for m in COMMIT_REPO.finditer(text):
        if m.group(1).rstrip("/").replace(".git", "").lower() == target:
            return m.group(2)
    return ""


def first_add_date(repo_root, rel):
    r = subprocess.run(["git", "log", "--reverse", "--format=%ad", "--date=short", "--", rel],
                       cwd=repo_root, capture_output=True, text=True)
    lines = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()] if r.returncode == 0 else []
    return lines[0] if lines else ""


# ── planned fields from the application ─────────────────────────────────────────
DUR = re.compile(r"Total Estimated Duration:\*\*\s*([\d.]+)\s*month", re.I)
FTE = re.compile(r"Full[- ]Time Equivalent\s*\(FTE\):\*\*\s*([\d.]+)", re.I)
COST = re.compile(r"Total Cost[s]?:\*\*\s*\$?\s*([\d,]+)", re.I)


def _parse_planned(txt, app_url):
    d = DUR.search(txt); f = FTE.search(txt); c = COST.search(txt)
    if not (d or f or c):
        return None
    return (f.group(1) if f else "", d.group(1) if d else "",
            (c.group(1).replace(",", "") if c else ""), app_url)

def planned_from_application(app_index, key, primary_repo):
    """Find the grant application across BOTH w3f grant repos and parse planned fields.
    Matches (in order): repo-URL inside the application == the delivered primary repo
    (most robust); exact slug; slug prefix/containment. Returns (fte, dur, cost, url)."""
    target = primary_repo.lower() if primary_repo else ""
    # 1) repo-URL match: the application that links the same repo we delivered
    if target:
        for (apf, stem, txt, url) in app_index:
            if target in txt.lower():
                p = _parse_planned(txt, url)
                if p: return p
    # 2) exact slug, then 3) prefix/containment
    for exact in (True, False):
        for (apf, stem, txt, url) in app_index:
            s = slug(stem)
            hit = (s == key) if exact else (s and (s.startswith(key) or key.startswith(s)
                   or (len(key) >= 6 and key in s) or (len(s) >= 6 and s in key)))
            if hit:
                p = _parse_planned(txt, url)
                if p: return p
    return ("", "", "", "")

def build_app_index(grants_root, general_root):
    """Pre-load all application .md files (recursively) from BOTH grant repos."""
    idx = []
    for root, base in ((grants_root, "Grants-Program"), (general_root, "General-Grants-Program")):
        if not root or not os.path.isdir(root):
            continue
        for apf in glob.glob(os.path.join(root, "**", "*.md"), recursive=True):
            low = apf.lower()
            if "template" in low or "readme" in low:
                continue
            if "/applications/" not in low.replace("\\", "/") and "/grants/" not in low.replace("\\", "/"):
                continue
            try:
                txt = open(apf, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            stem = os.path.basename(apf)[:-3]
            url = f"github.com/w3f/{base}/blob/master/" + os.path.relpath(apf, root).replace("\\", "/")
            idx.append((apf, stem, txt, url))
    return idx


def pick_primary(all_repos, key):
    """Deterministic primary-repo choice among project-controlled repos, preferring the
    SUBSTANTIVE repo over thin meta/submission repos. Returns (owner_repo, own, shared)."""
    own, shared = [], []
    for (o, r) in all_repos:
        (shared if o.lower() in SHARED_OWNERS else own).append(f"{o}/{r}")
    if not own:
        return "", own, shared
    def is_meta(orr):
        nm = orr.split("/")[1].lower()
        return any(h in nm for h in META_REPO_HINTS)
    def score(orr):
        name = slug(orr.split("/")[1]); owner = slug(orr.split("/")[0])
        s = 0
        if name == key or key == owner: s += 4            # exact name/owner match
        elif key in name or name in key or key in owner: s += 2  # partial match
        if not is_meta(orr): s += 1                        # prefer substantive over meta
        return s
    # highest score, stable by original order for ties
    best = max(range(len(own)), key=lambda i: (score(own[i]), -i))
    return own[best], own, shared


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="resolve_cache")
    ap.add_argument("--out-manifest", default="data/calibration/projects_manifest.census.csv")
    ap.add_argument("--out-audit", default="reports/census_audit.csv")
    a = ap.parse_args()

    deliv = os.path.join(a.cache, "deliv"); grants = os.path.join(a.cache, "grants")
    general = os.path.join(a.cache, "general")
    os.makedirs(a.cache, exist_ok=True)
    if not clone(DELIV_URL, deliv, shallow=False):
        sys.exit("[FATAL] could not clone delivery repo (need full history for dates).")
    have_g = clone(GRANTS_URL, grants, shallow=True)
    have_gg = clone(GENERAL_GRANTS_URL, general, shallow=True)   # older grants' applications
    if not have_g:
        print("[WARN] grants repo clone failed; planned fields will be sparse.")
    app_index = build_app_index(grants if have_g else "", general if have_gg else "")
    print(f"[info] application index: {len(app_index)} files across both grant repos")

    files = [f for f in glob.glob(os.path.join(deliv, "deliveries", "*.md"))
             if not os.path.basename(f).startswith(".")
             and "template" not in os.path.basename(f).lower()]

    # group delivery files by NORMALISED (slug) project key so case-variant filenames
    # (e.g. ParaSpell-followup vs Paraspell-followup) collapse into one project. Keep a
    # readable display name = the most common original stem.
    groups = {}; display = {}
    for f in files:
        stem = project_key(os.path.basename(f))
        gkey = slug(stem)
        if not gkey:
            continue
        groups.setdefault(gkey, []).append(f)
        display.setdefault(gkey, {}).setdefault(stem, 0)
        display[gkey][stem] += 1

    manifest_rows, audit_rows = [], []
    for key in sorted(groups):
        gfiles = sorted(groups[key])
        pid = max(display[key], key=lambda s: display[key][s])   # readable project_id
        all_repos, delivered = [], ""
        primary_commit = ""
        for f in gfiles:
            txt = open(f, encoding="utf-8", errors="ignore").read()
            for x in repos_in_text(txt):
                if x not in all_repos:
                    all_repos.append(x)
            d = first_add_date(deliv, os.path.relpath(f, deliv))
            if d and d > delivered:
                delivered = d
        primary, own, shared = pick_primary(all_repos, key)

        # try to pin a commit belonging to the primary repo (latest milestone first)
        if primary:
            for f in reversed(gfiles):
                c = commit_for_repo(open(f, encoding="utf-8", errors="ignore").read(), primary)
                if c:
                    primary_commit = c; break

        fte, dur, cost, appurl = planned_from_application(app_index, key, primary)
        planned_pm = ""
        try:
            if fte and dur:
                planned_pm = f"{float(fte) * float(dur):.2f}"
        except ValueError:
            pass

        # ── eligibility verdict ────────────────────────────────────────────────
        if not primary:
            verdict, reason = "EXCLUDED", ("un-separable: only shared/3rd-party monorepos"
                                           if shared else "no project repo referenced")
        elif not delivered:
            verdict, reason = "EXCLUDED", "no resolvable delivery date"
        else:
            verdict, reason = "INCLUDED", "single separable primary repo + dated delivery"

        audit_rows.append(dict(project_id=pid, verdict=verdict, reason=reason,
                               primary_repo=("https://github.com/" + primary) if primary else "",
                               commit=primary_commit, delivered_date=delivered,
                               n_delivery_files=len(gfiles),
                               own_org_repos=";".join(own[:6]), shared_repos=";".join(shared[:6]),
                               planned_pm=planned_pm))
        if verdict == "INCLUDED":
            manifest_rows.append(dict(
                project_id=pid, project_name=pid, repo_url="https://github.com/" + primary,
                commit_sha=primary_commit, cutoff_date=delivered, since_date="", subdir="",
                planned_fte=fte, planned_duration_months=dur, planned_pm=planned_pm,
                cost_usd=cost, application_url=appurl,
                notes="census auto-harvested; primary=substantive own-org rule; grouped by slug"))

    os.makedirs(os.path.dirname(a.out_manifest), exist_ok=True)
    os.makedirs(os.path.dirname(a.out_audit), exist_ok=True)
    with open(a.out_manifest, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS); w.writeheader(); w.writerows(manifest_rows)
    with open(a.out_audit, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=AUDIT_FIELDS); w.writeheader(); w.writerows(audit_rows)

    inc = sum(1 for r in audit_rows if r["verdict"] == "INCLUDED")
    print(f"Projects scanned: {len(groups)} | INCLUDED: {inc} | EXCLUDED: {len(groups)-inc}")
    print(f"  -> {a.out_manifest} ({inc} rows)")
    print(f"  -> {a.out_audit} (all {len(groups)} projects + verdict)")


if __name__ == "__main__":
    main()
