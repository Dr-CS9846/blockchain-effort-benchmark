#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
treasury_mine.py  —  mine PLANNED / REPORTED effort from OpenGov Treasury proposals (Subsquare)
================================================================================================
Polkassembly required a per-item detail call that failed/was slow (600 NO_DETAIL in 17 min).
Subsquare returns the proposal CONTENT (markdown body) INSIDE the listing, so one fast call per
page yields the text we parse for effort signals - no per-item detail.

Per proposal we record: requested amount, proposer, and documented effort signals (FTE, estimated
duration, team size, explicit person-month statements) parsed from the markdown, plus GitHub repo
links. Clean human-stated effort is valuable EVEN WITHOUT a repo (a reported-effort anchor in its
own right), so every proposal carrying effort is kept; the repo-matched subset additionally grows
the size -> planned_pm calibration set.

stdlib only. Output: data/calibration/treasury_proposals.csv
"""
import argparse, csv, json, os, re, sys, time, urllib.request, urllib.parse, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harvest_deliveries as H          # GH regex
import documented_effort as DE          # team_size, documented_pm_explicit, milestone_signals

# Subsquare REST. content (markdown) is included in the listing items.
ENDPOINTS = {
    "treasury": "https://{net}-api.subsquare.io/treasury/proposals?page={p}&pageSize={ps}",
    "gov2":     "https://{net}-api.subsquare.io/gov2/referendums?page={p}&pageSize={ps}",
}

def gj(url, tries=6, debug=False):
    req = urllib.request.Request(url, headers={"Accept": "application/json",
        "User-Agent": "Mozilla/5.0 blockchain-effort-benchmark"})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503): time.sleep(5 * (attempt + 1)); continue   # progressive backoff
            if debug: print(f"  [debug] HTTP {e.code} {url}", file=sys.stderr)
            return None
        except Exception as ex:
            if debug: print(f"  [debug] err {ex} {url}", file=sys.stderr)
            time.sleep(3); continue
    return None

def items_of(d):
    if d is None: return []
    if isinstance(d, list): return d
    for k in ("items", "data", "results"):
        v = d.get(k) if isinstance(d, dict) else None
        if isinstance(v, list): return v
        if isinstance(v, dict) and isinstance(v.get("items"), list): return v["items"]
    return []

def deep_get(it, *paths):
    for path in paths:
        cur = it; ok = True
        for key in path:
            if isinstance(cur, dict) and key in cur: cur = cur[key]
            else: ok = False; break
        if ok and cur not in (None, ""): return cur
    return None

# effort regexes (broadened: treasury/gov2 prose, not just the W3F template phrasing)
FTE  = re.compile(r"\b(?:FTE|full[\s-]?time equivalent)\b[^\d]{0,12}([\d.]+)", re.I)
FTE2 = re.compile(r"\b([\d.]+)\s*(?:FTE|full[\s-]?time(?:\s*equivalent)?|developers?|engineers?|devs?)\b", re.I)
DUR  = re.compile(r"\b(?:duration|timeline|time\s*frame|period)\b[^\d]{0,18}([\d.]+)\s*(week|month)", re.I)
DUR2 = re.compile(r"\b([\d.]+)[\s-]*(month|week)s?\b", re.I)            # "8 months", "8-month", "12 weeks"
TEAMN = re.compile(r"\bteam of\s+([\d.]+)\b|\b([\d.]+)\s*(?:team members|teammates|contributors|people)\b", re.I)

def _months(val, unit):
    try: return round(float(val) * (1/4.345 if unit.lower().startswith("week") else 1.0), 2)
    except ValueError: return ""

def parse_planned(txt):
    f = FTE.search(txt) or FTE2.search(txt); fte = f.group(1) if f else ""
    m = DUR.search(txt) or DUR2.search(txt)
    months = _months(m.group(1), m.group(2)) if m else ""
    return fte, months

def team_n(txt):
    t = DE.team_size(txt)            # W3F-style "Team members" list first
    if t not in ("", None): return t
    m = TEAMN.search(txt)
    if m:
        g = m.group(1) or m.group(2)
        try:
            n = int(float(g));  return n if 1 <= n <= 40 else ""
        except (ValueError, TypeError): return ""
    return ""

def repos_in(txt):
    out = []
    for m in H.GH.finditer(txt or ""):
        o, r = m.group(1), m.group(2).rstrip(").,").replace(".git", "")
        if r.lower() in ("polkadot", "polkadot-sdk", "substrate"): continue
        if (o, r) not in out: out.append((o, r))
    return [f"{o}/{r}" for o, r in out]

def main():
    ap = argparse.ArgumentParser()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--out", default=os.path.join(root, "data/calibration/treasury_proposals.csv"))
    ap.add_argument("--networks", default="polkadot,kusama")
    ap.add_argument("--types", default="treasury,gov2")
    ap.add_argument("--pages", type=int, default=6)
    ap.add_argument("--page-size", type=int, default=100)
    a = ap.parse_args()

    FIELDS = ["network", "proposal_type", "index", "title", "requested", "proposer",
              "planned_fte", "planned_duration_months", "team_size", "documented_pm_explicit",
              "sum_milestone_duration_months", "n_github_repos", "github_repos", "content_len", "status"]
    out = []
    for net in [x.strip() for x in a.networks.split(",") if x.strip()]:
        for ptype in [x.strip() for x in a.types.split(",") if x.strip()]:
            tmpl = ENDPOINTS.get(ptype)
            if not tmpl: continue
            got = 0
            for p in range(1, a.pages + 1):
                d = gj(tmpl.format(net=net, p=p, ps=a.page_size), debug=(p == 1))
                its = items_of(d)
                if p == 1 and its:
                    print(f"  [debug] {net}/{ptype} first-item keys: {sorted(list(its[0].keys()))[:20]}", file=sys.stderr)
                if not its: break
                for it in its:
                    content = deep_get(it, ["content"], ["contentSummary"], ["onchainData", "content"]) or ""
                    title = deep_get(it, ["title"]) or ""
                    corpus = str(content) + "\n" + str(title)
                    idx = deep_get(it, ["referendumIndex"], ["proposalIndex"], ["index"],
                                   ["onchainData", "index"], ["_id"])
                    req = deep_get(it, ["value"], ["onchainData", "value"],
                                   ["onchainData", "treasuryProposal", "value"],
                                   ["onchainData", "proposal", "value"])
                    proposer = deep_get(it, ["proposer"], ["author", "username"],
                                        ["onchainData", "proposer"], ["onchainData", "meta", "proposer"]) or ""
                    fte, dur = parse_planned(corpus)
                    ts = team_n(corpus)
                    dpm, _raw = DE.documented_pm_explicit(corpus)
                    ms_dur, _n, _fn = DE.milestone_signals(corpus)
                    repos = repos_in(corpus)
                    out.append(dict(network=net, proposal_type=ptype, index=idx,
                                    title=str(title)[:120], requested=req, proposer=str(proposer)[:50],
                                    planned_fte=fte, planned_duration_months=dur, team_size=ts,
                                    documented_pm_explicit=dpm, sum_milestone_duration_months=ms_dur,
                                    n_github_repos=len(repos), github_repos=";".join(repos[:8]),
                                    content_len=len(str(content)), status="OK"))
                    got += 1
                # Subsquare ignores pageSize (returns ~10/page); paginate by page number until an
                # empty page. ~1s/page keeps us under the rate limit so LATER sources (gov2/kusama)
                # are not starved (the earlier fast pace got them 429'd after the treasury burst).
                time.sleep(1.0)
            print(f"[{net}/{ptype}] {got} proposals")
            time.sleep(3)          # let any rate-limit window reset before the next source

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(out)

    ok = [r for r in out if r["status"] == "OK"]
    has_content = sum(1 for r in ok if r["content_len"] and int(r["content_len"]) > 50)
    has_repo = sum(1 for r in ok if r["n_github_repos"] and int(r["n_github_repos"]) > 0)
    has_plan = sum(1 for r in ok if r["planned_fte"] or r["planned_duration_months"])
    has_team = sum(1 for r in ok if r["team_size"])
    has_expl = sum(1 for r in ok if r["documented_pm_explicit"])
    any_effort = sum(1 for r in ok if r["planned_fte"] or r["planned_duration_months"] or r["team_size"] or r["documented_pm_explicit"])
    useful = sum(1 for r in ok if (r["n_github_repos"] and int(r["n_github_repos"]) > 0)
                 and (r["planned_fte"] or r["planned_duration_months"]))
    print(f"Total {len(out)} | with content {has_content} | repo {has_repo} | FTE/duration {has_plan} "
          f"| team {has_team} | explicit-PM {has_expl} | ANY effort {any_effort} | repo+plan {useful}")
    print(f"Wrote {a.out}")

if __name__ == "__main__":
    main()
