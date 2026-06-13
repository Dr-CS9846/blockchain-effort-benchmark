#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
treasury_mine.py  —  mine PLANNED / REPORTED effort from Polkadot OpenGov Treasury proposals
=============================================================================================
W3F grants gave us ~184 human-stated planned-effort points (planned_pm = FTE x duration), which
target-compare showed is the better-behaved, more defensible target than mined git PM - but it is
too small to break the accuracy ceiling. Polkadot OpenGov Treasury proposals are a far larger,
structured, ON-CHAIN pool of the SAME human-stated effort data (FTE, team, per-milestone
duration + budget, requested DOT), tracked on Polkassembly. This miner harvests them.

For each proposal it records: requested amount (DOT), proposer, and the documented effort signals
(FTE, estimated duration, team size, explicit person-month/week/day statements) parsed from the
proposal markdown, plus any GitHub repository links (so the proposal can later be matched to a
measurable delivered repo and joined to size). This is the discovery + extraction step; the count
that matters is "proposals that carry BOTH a GitHub repo AND a stated FTE/duration" - the rows that
can grow the size -> planned_pm calibration set.

Polkassembly REST v1 (needs header x-network). stdlib only. Output: data/calibration/treasury_proposals.csv
"""
import argparse, csv, json, os, re, sys, time, urllib.request, urllib.parse, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harvest_deliveries as H          # GH regex, slug
import documented_effort as DE          # team_size, documented_pm_explicit, milestone_signals

API = "https://api.polkassembly.io/api/v1"
PLANCK = 1e10                            # 1 DOT = 1e10 planck

def gj(url, network, tries=4):
    req = urllib.request.Request(url, headers={"x-network": network,
        "Accept": "application/json", "User-Agent": "blockchain-effort-benchmark"})
    for _ in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503): time.sleep(8); continue
            return None
        except Exception:
            time.sleep(4); continue
    return None

def listing(ptype, network, pages, limit_per):
    ids = []
    for p in range(1, pages + 1):
        url = f"{API}/listing/on-chain-posts?proposalType={ptype}&listingLimit={limit_per}&page={p}&sortBy=newest"
        d = gj(url, network)
        posts = (d or {}).get("posts") or []
        if not posts: break
        for po in posts:
            pid = po.get("post_id", po.get("postId"))
            if pid is not None: ids.append((pid, po.get("title", "")))
        if len(posts) < limit_per: break
        time.sleep(0.4)
    return ids

def detail(ptype, pid, network):
    url = f"{API}/posts/on-chain-post?proposalType={ptype}&postId={pid}"
    return gj(url, network)

# parse a "FTE: x" / "Estimated Duration: x months" out of free proposal text (same family as W3F)
FTE = re.compile(r"\b(?:FTE|full[\s-]?time equivalent)\b[^\d]{0,12}([\d.]+)", re.I)
DUR = re.compile(r"\b(?:duration|timeline|time\s*frame)\b[^\d]{0,18}([\d.]+)\s*(week|month)", re.I)

def parse_planned(txt):
    f = FTE.search(txt); fte = f.group(1) if f else ""
    months = ""; m = DUR.search(txt)
    if m:
        v = float(m.group(1)); months = round(v * (1/4.345 if m.group(1) and m.group(2).lower().startswith("week") else 1.0), 2)
    return fte, (months if months != "" else "")

def repos_in(txt):
    out = []
    for m in H.GH.finditer(txt or ""):
        o, r = m.group(1), m.group(2).rstrip(").,").replace(".git", "")
        if r.lower() in ("polkadot","polkadot-sdk","substrate"): continue
        if (o, r) not in out: out.append((o, r))
    return [f"{o}/{r}" for o, r in out]

def main():
    ap = argparse.ArgumentParser()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--out", default=os.path.join(root, "data/calibration/treasury_proposals.csv"))
    ap.add_argument("--networks", default="polkadot,kusama")
    ap.add_argument("--types", default="Treasury,ReferendumV2")
    ap.add_argument("--pages", type=int, default=8)         # listing pages per type
    ap.add_argument("--limit-per", type=int, default=100)
    ap.add_argument("--max-detail", type=int, default=600)  # cap detail fetches (rate)
    a = ap.parse_args()

    FIELDS = ["network","proposal_type","post_id","title","requested_dot","proposer",
              "planned_fte","planned_duration_months","team_size","documented_pm_explicit",
              "sum_milestone_duration_months","n_github_repos","github_repos","url","status"]
    out, fetched = [], 0
    for network in [x.strip() for x in a.networks.split(",") if x.strip()]:
        for ptype in [x.strip() for x in a.types.split(",") if x.strip()]:
            ids = listing(ptype, network, a.pages, a.limit_per)
            print(f"[{network}/{ptype}] listed {len(ids)} proposals")
            for pid, title in ids:
                if fetched >= a.max_detail: break
                fetched += 1
                d = detail(ptype, pid, network)
                if not d:
                    out.append({**{k:"" for k in FIELDS}, "network":network, "proposal_type":ptype,
                                "post_id":pid, "title":title[:120], "status":"NO_DETAIL"}); continue
                content = (d.get("content") or "") + "\n" + (d.get("title") or title or "")
                req = d.get("requested") or d.get("reward") or ((d.get("proposed_call") or {}).get("args") or {}).get("amount")
                try: req_dot = round(float(req)/PLANCK, 2) if req else ""
                except (ValueError, TypeError): req_dot = ""
                fte, dur = parse_planned(content)
                ts = DE.team_size(content)
                dpm, _raw = DE.documented_pm_explicit(content)
                ms_dur, _n, _fn = DE.milestone_signals(content)
                repos = repos_in(content)
                out.append(dict(network=network, proposal_type=ptype, post_id=pid, title=(d.get("title") or title or "")[:120],
                                requested_dot=req_dot, proposer=(d.get("proposer") or "")[:50],
                                planned_fte=fte, planned_duration_months=dur, team_size=ts,
                                documented_pm_explicit=dpm, sum_milestone_duration_months=ms_dur,
                                n_github_repos=len(repos), github_repos=";".join(repos[:8]),
                                url=f"https://{network}.polkassembly.io/referenda/{pid}" if ptype=="ReferendumV2"
                                    else f"https://{network}.polkassembly.io/treasury/{pid}",
                                status="OK"))
                time.sleep(0.3)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(out)

    ok = [r for r in out if r["status"] == "OK"]
    with_repo = [r for r in ok if r["n_github_repos"] and int(r["n_github_repos"]) > 0]
    with_plan = [r for r in ok if r["planned_fte"] or r["planned_duration_months"]]
    useful = [r for r in ok if (r["n_github_repos"] and int(r["n_github_repos"])>0) and (r["planned_fte"] or r["planned_duration_months"])]
    print(f"Total {len(out)} | OK {len(ok)} | with GitHub repo {len(with_repo)} | with FTE/duration {len(with_plan)} "
          f"| with team {sum(1 for r in ok if r['team_size'])} | useful (repo AND plan) {len(useful)}")
    print(f"Wrote {a.out}")

if __name__ == "__main__":
    main()
