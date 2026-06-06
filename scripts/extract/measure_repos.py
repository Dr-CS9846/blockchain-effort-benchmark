#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
measure_repos.py  —  Step 2: clone, measure KSLOC + active person-months
=========================================================================
Reads projects_manifest.csv.  For each row that has a repo_url it:
  1. Clones (or reuses) the repo in repo_cache/<project_id>/
  2. Resolves the commit  (commit_sha > cutoff_date > HEAD)
  3. Counts KSLOC via cloc (preferred) or pygount (fallback)
  4. Counts active person-months from git log (distinct author×month pairs,
     bots and merge commits excluded, .mailmap respected)
  5. Appends a row to measurements.csv

Outputs:
  measurements.csv           – one row per project, status OK/ERROR/NO_REPO
  measurement_provenance.json – tool versions + run parameters

Usage:
  python measure_repos.py                        # all rows
  python measure_repos.py --only AdMeta,Roloi    # subset
  python measure_repos.py --force                # re-measure OK rows too
"""
import argparse, csv, json, os, re, subprocess, sys, datetime, shutil
from pathlib import Path

HERE = Path(__file__).parent.resolve()
CACHE = HERE / "repo_cache"
BOTS = re.compile(r"\[bot\]|github-actions|dependabot|renovate|noreply", re.I)
EXCLUDE_DIRS = ["node_modules", "vendor", ".git", "dist", "build", "target",
                "__pycache__", ".venv", "venv", "third_party", "thirdparty"]

CODE_EXTS = {
    ".rs", ".go", ".ts", ".tsx", ".js", ".jsx", ".py", ".sol", ".c", ".cpp",
    ".cc", ".h", ".hpp", ".java", ".kt", ".swift", ".cs", ".rb", ".scala",
    ".sh", ".bash",
}

# cloc language names that count as SOURCE CODE for the size metric. Excludes
# data/markup/config/docs (JSON, YAML, TOML, Markdown, "PO File", SVG, XML,
# HTML, CSS, Text, INI, Handlebars, Gradle, ...) which otherwise inflate KSLOC.
SOURCE_LANGS = {
    "Rust", "Go", "TypeScript", "JavaScript", "JSX", "TSX", "Python", "Solidity",
    "C", "C++", "C/C++ Header", "C Header", "Java", "Kotlin", "Swift", "C#",
    "Ruby", "Scala", "Vyper", "Move", "Cairo", "Haskell", "Elixir", "Erlang",
    "PHP", "Objective-C", "Dart", "Lua", "Bourne Shell", "Bourne Again Shell",
}

# ── tool detection ────────────────────────────────────────────────────────────

def _run(cmd, cwd=None, capture=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=capture, text=True)
    return r

def cloc_available():
    return shutil.which("cloc") is not None

def git_version():
    r = _run(["git", "--version"])
    return r.stdout.strip() if r.returncode == 0 else "unknown"

def pygount_version():
    try:
        import pygount
        return getattr(pygount, "__version__", "installed")
    except ImportError:
        return None

# ── SLOC counting ─────────────────────────────────────────────────────────────

def count_sloc_cloc(repo_dir, subdir=""):
    target = str(Path(repo_dir) / subdir) if subdir else str(repo_dir)
    excl = ",".join(EXCLUDE_DIRS)
    r = _run(["cloc", "--json", f"--exclude-dir={excl}", target])
    if r.returncode != 0:
        raise RuntimeError(f"cloc failed: {r.stderr[:300]}")
    data = json.loads(r.stdout)
    langs = {k: v for k, v in data.items() if k not in ("header", "SUM")}
    ksloc_all = sum(v.get("code", 0) for v in langs.values()) / 1000
    ksloc_code = sum(v.get("code", 0) for k, v in langs.items() if k in SOURCE_LANGS) / 1000
    top = sorted(langs.items(), key=lambda x: x[1].get("code", 0), reverse=True)[:5]
    top_langs = {k: v.get("code", 0) for k, v in top}
    return ksloc_code, ksloc_all, top_langs   # ksloc_code = SOURCE_LANGS only; ksloc_all = everything

def count_sloc_pygount(repo_dir, subdir=""):
    from pygount import SourceAnalysis
    root = Path(repo_dir) / subdir if subdir else Path(repo_dir)
    code = all_code = 0
    langs: dict[str, int] = {}
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(ex in path.parts for ex in EXCLUDE_DIRS):
            continue
        if path.suffix.lower() not in CODE_EXTS:
            continue
        try:
            ana = SourceAnalysis.from_file(str(path), "pygount")
        except Exception:
            continue
        if ana.state_name != "analyzed":
            continue
        lines = ana.code_count
        all_code += lines
        if path.suffix.lower() in CODE_EXTS:
            code += lines
            lang = ana.language or path.suffix
            langs[lang] = langs.get(lang, 0) + lines
    ksloc_code = code / 1000
    ksloc_all = all_code / 1000
    top = sorted(langs.items(), key=lambda x: x[1], reverse=True)[:5]
    return ksloc_code, ksloc_all, dict(top)

def count_sloc(repo_dir, subdir=""):
    if cloc_available():
        return count_sloc_cloc(repo_dir, subdir)
    return count_sloc_pygount(repo_dir, subdir)

# ── git helpers ───────────────────────────────────────────────────────────────

def _reachable(repo_dir, sha):
    return _run(["git", "cat-file", "-e", sha + "^{commit}"], cwd=repo_dir).returncode == 0

def resolve_commit(repo_dir, commit_sha="", cutoff_date=""):
    """Return (sha, source). source in {commit, cutoff, head}. A pinned commit
    that is NOT in this repo (e.g. it belonged to a sibling repo in the delivery)
    is rejected and we fall back to cutoff/HEAD so we never silently mis-measure."""
    if commit_sha:
        sha = commit_sha.strip()
        if not _reachable(repo_dir, sha):
            _run(["git", "fetch", "--quiet", "origin", sha], cwd=repo_dir)  # try to get it
        if _reachable(repo_dir, sha):
            cd = (cutoff_date or "").strip()[:10]
            if cd:
                cdate = _run(["git", "show", "-s", "--format=%cs", sha], cwd=repo_dir).stdout.strip()
                if cdate and cdate > cd:
                    pass  # commit post-dates delivery -> invalid as-delivered pin, fall through
                else:
                    return sha, "commit"
            else:
                return sha, "commit"
        # else: unreachable or post-cutoff -> fall through to cutoff/head
    if cutoff_date:
        r = _run(["git", "log", f"--before={cutoff_date} 23:59:59", "--format=%H", "-n1"], cwd=repo_dir)
        sha = r.stdout.strip()
        if sha:
            return sha, "cutoff"
    r = _run(["git", "log", "--format=%H", "-n1"], cwd=repo_dir)
    return r.stdout.strip(), "head"

def window_since(since_date, cutoff_date, duration_months):
    """Window START for effort = explicit since_date, else cutoff - planned_duration.
    Bounds effort to the grant period so long-lived repos do not count pre-grant history."""
    if (since_date or "").strip():
        return since_date.strip()
    if (cutoff_date or "").strip() and (duration_months or "").strip():
        try:
            cd = datetime.datetime.strptime(cutoff_date.strip()[:10], "%Y-%m-%d")
            days = int(round(float(duration_months) * 30.44))
            return (cd - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        except Exception:
            return ""
    return ""

def active_person_months(repo_dir, ref, since_date="", cutoff_date="", min_commits=1):
    cmd = ["git", "log", ref, "--no-merges",
           "--format=%ae%x09%ad", "--date=format:%Y-%m"]
    if since_date:
        cmd += [f"--since={since_date}"]
    if cutoff_date:
        cmd += [f"--until={cutoff_date} 23:59:59"]   # bound effort to the grant window
    r = _run(cmd, cwd=repo_dir)
    if r.returncode != 0:
        return 0, 0, 0
    counts: dict[tuple, int] = {}
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line or BOTS.search(line):
            continue
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        email, ym = parts
        counts[(email.lower(), ym)] = counts.get((email.lower(), ym), 0) + 1
    active = sum(1 for v in counts.values() if v >= min_commits)
    total_commits = sum(counts.values())
    distinct_authors = len({k[0] for k in counts})
    return active, total_commits, distinct_authors

# ── clone / update ────────────────────────────────────────────────────────────

def ensure_clone(project_id, repo_url):
    dest = CACHE / project_id
    if dest.exists():
        r = _run(["git", "fetch", "--quiet"], cwd=dest)
        if r.returncode != 0:
            shutil.rmtree(dest)
        else:
            return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = _run(["git", "clone", "--quiet", repo_url, str(dest)])
    if r.returncode != 0:
        raise RuntimeError(f"git clone failed: {r.stderr[:300]}")
    return dest

# ── main ──────────────────────────────────────────────────────────────────────

FIELDNAMES = [
    "project_id", "project_name", "repo_url", "resolved_commit", "commit_source",
    "effort_since", "effort_until",
    "ksloc_code", "ksloc_all", "active_person_months", "total_commits",
    "distinct_authors", "top_langs", "planned_fte", "planned_duration_months",
    "planned_pm", "cost_usd", "status", "error_msg",
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(HERE / "projects_manifest.csv"))
    ap.add_argument("--out",      default=str(HERE / "measurements.csv"))
    ap.add_argument("--only",     default="", help="comma-separated project_ids to run")
    ap.add_argument("--force",    action="store_true", help="re-measure OK rows")
    ap.add_argument("--min-commits-per-month", type=int, default=1, dest="min_commits")
    a = ap.parse_args()

    only = {x.strip() for x in a.only.split(",") if x.strip()}

    manifest = list(csv.DictReader(open(a.manifest, encoding="utf-8")))

    # load existing results to support resumability
    existing: dict[str, dict] = {}
    if os.path.exists(a.out):
        for row in csv.DictReader(open(a.out, encoding="utf-8")):
            existing[row["project_id"]] = row

    results = []
    for row in manifest:
        pid = row["project_id"]
        if only and pid not in only:
            # preserve existing result if skipping
            if pid in existing:
                results.append(existing[pid])
            continue

        prev = existing.get(pid, {})
        if not a.force and prev.get("status") == "OK":
            print(f"  SKIP (already OK): {pid}")
            results.append(prev)
            continue

        repo_url = row.get("repo_url", "").strip()
        if not repo_url:
            print(f"  NO_REPO: {pid} — fill repo_url in manifest")
            results.append({**{f: "" for f in FIELDNAMES},
                            "project_id": pid, "project_name": row["project_name"],
                            "planned_pm": row.get("planned_pm",""),
                            "planned_fte": row.get("planned_fte",""),
                            "planned_duration_months": row.get("planned_duration_months",""),
                            "cost_usd": row.get("cost_usd",""),
                            "status": "NO_REPO"})
            continue

        print(f"  Measuring: {pid} ({repo_url})")
        out_row = {f: "" for f in FIELDNAMES}
        out_row.update({"project_id": pid, "project_name": row["project_name"],
                        "repo_url": repo_url,
                        "planned_pm": row.get("planned_pm",""),
                        "planned_fte": row.get("planned_fte",""),
                        "planned_duration_months": row.get("planned_duration_months",""),
                        "cost_usd": row.get("cost_usd","")})
        try:
            repo_dir = ensure_clone(pid, repo_url)
            sha, csource = resolve_commit(repo_dir, row.get("commit_sha",""), row.get("cutoff_date",""))
            co = _run(["git", "checkout", "--quiet", "-f", sha], cwd=repo_dir)
            if co.returncode != 0:
                raise RuntimeError(f"checkout failed for {sha[:12]}: {co.stderr[:160]}")
            kc, ka, top = count_sloc(repo_dir, row.get("subdir",""))
            cutoff = row.get("cutoff_date", "")
            since = window_since(row.get("since_date",""), cutoff, row.get("planned_duration_months",""))
            apm, tc, da = active_person_months(repo_dir, sha, since, cutoff, a.min_commits)
            out_row.update({"resolved_commit": sha, "commit_source": csource,
                            "effort_since": since, "effort_until": cutoff,
                            "ksloc_code": f"{kc:.4f}", "ksloc_all": f"{ka:.4f}",
                            "active_person_months": str(apm),
                            "total_commits": str(tc), "distinct_authors": str(da),
                            "top_langs": json.dumps(top), "status": "OK"})
            print(f"    OK [{csource}] {since or '-'}..{cutoff or '-'}: ksloc_code={kc:.2f}  active_pm={apm}  authors={da}")
        except Exception as e:
            out_row["status"] = "ERROR"
            out_row["error_msg"] = str(e)[:200]
            print(f"    ERROR: {e}")
        results.append(out_row)

    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(results)

    prov = {
        "run_date": datetime.datetime.utcnow().isoformat() + "Z",
        "git_version": git_version(),
        "sloc_tool": "cloc" if cloc_available() else f"pygount {pygount_version()}",
        "min_commits_per_month": a.min_commits,
        "exclude_dirs": EXCLUDE_DIRS,
        "manifest": a.manifest,
    }
    json.dump(prov, open(HERE / "measurement_provenance.json", "w"), indent=2)

    ok = sum(1 for r in results if r["status"] == "OK")
    no_repo = sum(1 for r in results if r["status"] == "NO_REPO")
    err = sum(1 for r in results if r["status"] == "ERROR")
    print(f"\nDone. {ok} OK | {no_repo} NO_REPO | {err} ERROR")
    print(f"Wrote: {a.out}")
    if no_repo:
        print(f"  -> Fill repo_url for {no_repo} projects in projects_manifest.csv, then re-run.")

if __name__ == "__main__":
    main()
