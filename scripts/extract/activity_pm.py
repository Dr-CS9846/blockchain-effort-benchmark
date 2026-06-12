#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
activity_pm.py  —  PM-First Rebuild, Experiment 1: a richer, web-grounded effort signal
========================================================================================
Our current effort proxy counts only COMMIT days (active-dev-days / 19). It structurally
drops the "invisible" development work that is, in fact, publicly recorded on GitHub:
pull requests, code reviews, issue triage, and discussion. This miner recovers the FULL
contribution record per developer over each project's delivery window and recomputes the
person-month with two methods, alongside the current commit-only figure for comparison:

  signals (GitHub REST API, window = [effort_since, effort_until]):
    - commits                     (/repos/{o}/{r}/commits)
    - pull requests + issues      (/repos/{o}/{r}/issues, pull_request flag separates them)
    - issue / PR discussion       (/repos/{o}/{r}/issues/comments)
    - PR review (code) comments   (/repos/{o}/{r}/pulls/comments)

  effort recomputation:
    - PM_mid_rich  = union active developer-days (ANY contribution type) / 19   (Boehm unit)
    - PM_low_rich  = session-hours over the union timestamp stream / 152         (git-hours model)
    - PM_rgb       = Robles & Gonzalez-Barahona (2022) style dedication estimate:
                     sum over (developer, active-month) of dedication = min(1, active_days / 19),
                     i.e. a full-time month is ~19 active days; part-timers contribute a fraction.
                     R&GB validated this activity->effort mapping against 1,000+ developer surveys.

Pure API (no clone). stdlib only. Reads measurements_census.csv for the per-project window and
the current pm_mid; writes data/calibration/activity_pm.csv with the new signals + the deltas.

Auth: set GH_TOKEN (CI: ${{ secrets.GITHUB_TOKEN }}). Public-repo reads only; 5000 req/h.
"""
import argparse, csv, json, os, re, sys, time, datetime, urllib.request, urllib.parse, urllib.error
from pathlib import Path

API = "https://api.github.com"
BOTS = re.compile(r"\[bot\]$|^github-actions|dependabot|renovate|mergify|codecov|^web-flow$", re.I)
PH_PER_PM, DAYS_PER_PM = 152.0, 19.0
SESSION_GAP_MIN, FIRST_COMMIT_MIN = 120.0, 120.0
MAX_PAGES = 15                       # bound pathological repos (1500 events/endpoint)

def _hdr():
    h = {"Accept": "application/vnd.github+json", "User-Agent": "blockchain-effort-benchmark"}
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if tok: h["Authorization"] = f"Bearer {tok}"
    return h

def gh_get(path, params):
    """Paginated GET. Returns list of JSON items. Handles rate-limit (403/429) with a wait,
    404 (gone) as empty, and stops at MAX_PAGES."""
    items, page = [], 1
    while page <= MAX_PAGES:
        q = dict(params); q["per_page"] = 100; q["page"] = page
        url = f"{API}{path}?{urllib.parse.urlencode(q)}"
        req = urllib.request.Request(url, headers=_hdr())
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                batch = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):                       # rate limited -> wait on reset
                reset = e.headers.get("X-RateLimit-Reset")
                wait = max(2, min(120, int(reset) - int(time.time()))) if reset else 30
                time.sleep(wait); continue
            if e.code in (404, 451, 409):                  # gone / blocked / empty repo
                return items
            if e.code >= 500:
                time.sleep(5); continue
            return items
        except Exception:
            time.sleep(3); continue
        if not isinstance(batch, list) or not batch:
            break
        items.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return items

def parse_owner_repo(url):
    m = re.search(r"github\.com[/:]([^/]+)/([^/#?]+)", (url or "").strip())
    if not m: return None, None
    return m.group(1), re.sub(r"\.git$", "", m.group(2))

def _dt(s):
    try: return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception: return None

def _isbot(login): return bool(login) and bool(BOTS.search(login))

def collect(owner, repo, since_iso, until_iso, until_day):
    """Return per-developer timestamp lists by event type, within [since, until]."""
    ev = {}     # login -> list[datetime]
    counts = dict(commits=0, prs=0, issues=0, issue_comments=0, review_comments=0)
    def add(login, t):
        if not login or _isbot(login): return
        if t is None: return
        ev.setdefault(login.lower(), []).append(t)

    # commits (default branch). author.login preferred; fall back to commit author name.
    for c in gh_get(f"/repos/{owner}/{repo}/commits", {"since": since_iso, "until": until_iso}):
        a = (c.get("author") or {}); login = a.get("login")
        t = _dt(((c.get("commit") or {}).get("author") or {}).get("date", ""))
        if not login: login = (((c.get("commit") or {}).get("author") or {}).get("name") or "").lower()
        add(login, t); counts["commits"] += 1
    # issues + PRs (creation). issues endpoint returns both; pull_request key marks PRs.
    for it in gh_get(f"/repos/{owner}/{repo}/issues", {"since": since_iso, "state": "all"}):
        t = _dt(it.get("created_at", ""))
        if t is None or it.get("created_at", "")[:10] > until_day: continue
        add((it.get("user") or {}).get("login"), t)
        counts["prs" if it.get("pull_request") else "issues"] += 1
    # issue / PR discussion comments
    for cm in gh_get(f"/repos/{owner}/{repo}/issues/comments", {"since": since_iso}):
        t = _dt(cm.get("created_at", ""))
        if t is None or cm.get("created_at", "")[:10] > until_day: continue
        add((cm.get("user") or {}).get("login"), t); counts["issue_comments"] += 1
    # PR review (code) comments
    for cm in gh_get(f"/repos/{owner}/{repo}/pulls/comments", {"since": since_iso}):
        t = _dt(cm.get("created_at", ""))
        if t is None or cm.get("created_at", "")[:10] > until_day: continue
        add((cm.get("user") or {}).get("login"), t); counts["review_comments"] += 1
    return ev, counts

def session_hours(times):
    if not times: return 0.0
    ts = sorted(times); minutes = FIRST_COMMIT_MIN
    for prev, cur in zip(ts, ts[1:]):
        gap = (cur - prev).total_seconds() / 60.0
        minutes += gap if gap <= SESSION_GAP_MIN else FIRST_COMMIT_MIN
    return minutes / 60.0

def effort_from_events(ev):
    """Fuse all event types into the rich PM estimates."""
    union_days, union_times = set(), []
    rgb = 0.0                                   # R&GB dedication-weighted person-months
    for login, times in ev.items():
        if not times: continue
        union_times += times
        days_by_month = {}
        for t in times:
            d = t.strftime("%Y-%m-%d"); union_days.add((login, d))
            days_by_month.setdefault(t.strftime("%Y-%m"), set()).add(d)
        for _m, days in days_by_month.items():
            rgb += min(1.0, len(days) / DAYS_PER_PM)        # dedication this month, capped at full-time
    pm_mid_rich = round(len(union_days) / DAYS_PER_PM, 4)
    pm_low_rich = round(session_hours(union_times) / PH_PER_PM, 4)
    return dict(pm_mid_rich=pm_mid_rich, pm_low_rich=pm_low_rich, pm_rgb=round(rgb, 4),
                active_days_union=len(union_days), contributors_all=len(ev))

def main():
    ap = argparse.ArgumentParser()
    root = Path(__file__).resolve().parents[1]
    ap.add_argument("--meas", default=str(root / "data/calibration/measurements_census.csv"))
    ap.add_argument("--out",  default=str(root / "data/calibration/activity_pm.csv"))
    ap.add_argument("--only", default="", help="comma-separated project_ids (debug)")
    ap.add_argument("--limit", type=int, default=0, help="cap repos this run (0=all)")
    a = ap.parse_args()
    only = {x.strip() for x in a.only.split(",") if x.strip()}

    rows = [r for r in csv.DictReader(open(a.meas, encoding="utf-8")) if r.get("status") == "OK"]
    if not os.environ.get("GH_TOKEN") and not os.environ.get("GITHUB_TOKEN"):
        print("WARNING: no GH_TOKEN/GITHUB_TOKEN — unauthenticated (60 req/h), will rate-limit.", file=sys.stderr)

    FIELDS = ["project_id", "repo_url", "effort_since", "effort_until",
              "pm_mid_current", "pm_mid_commitonly_recheck",
              "n_commits", "n_prs", "n_issues", "n_issue_comments", "n_review_comments",
              "contributors_all", "contributors_committing", "active_days_union",
              "pm_mid_rich", "pm_low_rich", "pm_rgb", "status", "note"]
    out, done = [], 0
    for r in rows:
        pid = r["project_id"]
        if only and pid not in only: continue
        owner, repo = parse_owner_repo(r.get("repo_url", ""))
        since = (r.get("effort_since", "") or "")[:10]; until = (r.get("effort_until", "") or "")[:10]
        rec = {f: "" for f in FIELDS}
        rec.update({"project_id": pid, "repo_url": r.get("repo_url", ""),
                    "effort_since": since, "effort_until": until,
                    "pm_mid_current": r.get("pm_mid", "")})
        if not owner or not since or not until:
            rec["status"] = "SKIP"; rec["note"] = "no owner/repo or window"; out.append(rec); continue
        if a.limit and done >= a.limit:
            rec["status"] = "PENDING"; out.append(rec); continue
        since_iso = f"{since}T00:00:00Z"; until_iso = f"{until}T23:59:59Z"
        try:
            ev, counts = collect(owner, repo, since_iso, until_iso, until)
            committing = {lg for lg, ts in ev.items() if ts}   # any author with a timestamp (commits incl.)
            eff = effort_from_events(ev)
            rec.update({"n_commits": counts["commits"], "n_prs": counts["prs"], "n_issues": counts["issues"],
                        "n_issue_comments": counts["issue_comments"], "n_review_comments": counts["review_comments"],
                        "contributors_all": eff["contributors_all"], "contributors_committing": len(committing),
                        "active_days_union": eff["active_days_union"],
                        "pm_mid_rich": eff["pm_mid_rich"], "pm_low_rich": eff["pm_low_rich"],
                        "pm_rgb": eff["pm_rgb"], "status": "OK"})
            print(f"  OK {pid}: commits={counts['commits']} prs={counts['prs']} issues={counts['issues']} "
                  f"comments={counts['issue_comments']+counts['review_comments']} | "
                  f"pm_mid cur={r.get('pm_mid')} rich={eff['pm_mid_rich']} rgb={eff['pm_rgb']}")
        except Exception as e:
            rec["status"] = "ERROR"; rec["note"] = str(e)[:160]
            print(f"  ERROR {pid}: {e}")
        out.append(rec); done += 1

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(out)

    # quick relation summary (current commit-only pm_mid vs the rich signals), log-space
    try:
        import math
        ok = [x for x in out if x["status"] == "OK" and x["pm_mid_current"]]
        def corr(k):
            pairs = [(math.log(float(x["pm_mid_current"])), math.log(float(x[k])))
                     for x in ok if _pos(x["pm_mid_current"]) and _pos(x.get(k))]
            if len(pairs) < 8: return None, len(pairs)
            xs = [p[0] for p in pairs]; ys = [p[1] for p in pairs]
            mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
            num = sum((x-mx)*(y-my) for x, y in pairs)
            den = (sum((x-mx)**2 for x in xs) * sum((y-my)**2 for y in ys)) ** 0.5
            return (round(num/den, 3) if den else None), len(pairs)
        for k in ("pm_mid_rich", "pm_rgb", "pm_low_rich"):
            c, n = corr(k); print(f"  corr(log pm_mid_current, log {k}) = {c}  (n={n})")
    except Exception as e:
        print(f"  (summary skipped: {e})")
    print(f"Wrote {a.out}  ({sum(1 for x in out if x['status']=='OK')} OK / {len(out)})")

def _pos(v):
    try: return float(v) > 0
    except (TypeError, ValueError): return False

if __name__ == "__main__":
    main()
