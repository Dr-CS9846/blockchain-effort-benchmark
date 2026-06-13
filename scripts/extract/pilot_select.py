#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pilot_select.py  —  Step 1: curate cleanly human-REPORTED PM pilot cases
========================================================================
Master plan (Boehm-style curated calibration): hand-pick cleanly reported PMs from many sources
into one heterogeneous, high-quality dataset, then calibrate COCOMO II to PM=PM. This script does
the first selection pass on the treasury harvest: it filters the raw proposals to DEVELOPMENT work
with a computable, plausible, human-stated PM, guards against mis-parses, and emits a ranked
CANDIDATE table for human hand-pick (Steps 1, 5, 6).

stated_pm (human-reported):
  - FTE x duration   (preferred: the team's own effort estimate -> person-months)
  - else team x duration  (reported upper estimate when only headcount is given; flagged lower-conf)

Filters:
  - DEV theme from the title (develop/build/implement/runtime/pallet/sdk/wallet/dapp/indexer/...);
    exclude non-dev (marketing/event/campaign/ambassador/translation/rpc-provider/collator/
    reimburse/refund/bounty top-up/academy/coverage/ETP/...).
  - mis-parse guards: 0.1<=FTE<=20, 0.1<=team<=40, 0.25<=duration<=36 mo, 0.5<=stated_pm<=300.
  - confidence: HIGH = FTE x duration + dev + has GitHub repo (measurable size -> COCOMO pilot);
                MED  = FTE x duration (no repo) or team x duration + dev; else excluded.

Reads data/calibration/treasury_proposals.csv. Output: data/calibration/pilot_cases.csv
"""
import argparse, csv, os, re, sys

DEV = re.compile(r"develop|build|implement|runtime|pallet|\bsdk\b|wallet|dapp|d-app|indexer|bridge|"
                 r"smart[\s-]?contract|protocol|client|tooling|\btool\b|integration|library|framework|"
                 r"node\b|parachain|substrate|ink!|zk|prover|compiler|api\b|registrar|explorer", re.I)
NONDEV = re.compile(r"marketing|campaign|ambassador|translation|\bevent\b|conference|meetup|hackathon|"
                    r"\bacademy\b|education|coverage|\bETP\b|reimburse|refund|deposit|collator|"
                    r"top[\s-]?up|rpc provider|public rpc|\bgrant program\b|bounty\b", re.I)

def _f(r, k):
    v = (r.get(k) or "").strip()
    try: return float(v)
    except (ValueError, TypeError): return None

def main():
    ap = argparse.ArgumentParser()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--inp", default=os.path.join(root, "data/calibration/treasury_proposals.csv"))
    ap.add_argument("--out", default=os.path.join(root, "data/calibration/pilot_cases.csv"))
    a = ap.parse_args()

    rows = [r for r in csv.DictReader(open(a.inp, encoding="utf-8")) if r.get("status") == "OK"]
    FIELDS = ["network", "proposal_type", "index", "title", "stated_pm", "pm_basis",
              "planned_fte", "team_size", "duration_months", "n_github_repos", "github_repos",
              "requested_dot", "confidence", "url"]
    out = []
    for r in rows:
        title = (r.get("title") or "").strip()
        if not title or not DEV.search(title) or NONDEV.search(title):
            continue
        fte = _f(r, "planned_fte"); team = _f(r, "team_size"); dur = _f(r, "planned_duration_months")
        if not (dur and 0.25 <= dur <= 36):
            continue
        basis = ""; pm = None
        if fte and 0.1 <= fte <= 20:
            pm = round(fte * dur, 2); basis = "fte*duration"
        elif team and 0.1 <= team <= 40:
            pm = round(team * dur, 2); basis = "team*duration"   # upper estimate (not all full-time)
        if pm is None or not (0.5 <= pm <= 300):
            continue
        nrepo = 0
        try: nrepo = int(float(r.get("n_github_repos") or 0))
        except (ValueError, TypeError): nrepo = 0
        conf = "HIGH" if (basis == "fte*duration" and nrepo > 0) else \
               ("MED" if basis == "fte*duration" else "LOW")
        req_dot = ""
        try: req_dot = round(float(r["requested"]) / 1e10, 1) if r.get("requested") else ""
        except (ValueError, TypeError): req_dot = ""
        net = r["network"]; idx = r.get("index", "")
        url = (f"https://{net}.subsquare.io/referenda/{idx}" if r.get("proposal_type") == "gov2"
               else f"https://{net}.subsquare.io/treasury/proposals/{idx}")
        out.append(dict(network=net, proposal_type=r.get("proposal_type", ""), index=idx,
                        title=title[:90], stated_pm=pm, pm_basis=basis, planned_fte=fte or "",
                        team_size=team or "", duration_months=dur, n_github_repos=nrepo,
                        github_repos=(r.get("github_repos") or "")[:200], requested_dot=req_dot,
                        confidence=conf, url=url))
    out.sort(key=lambda x: ({"HIGH": 0, "MED": 1, "LOW": 2}[x["confidence"]], -(x["n_github_repos"])))

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(out)

    hi = [x for x in out if x["confidence"] == "HIGH"]
    md = [x for x in out if x["confidence"] == "MED"]
    print(f"candidate pilots: {len(out)} | HIGH (FTE*dur + repo): {len(hi)} | MED: {len(md)} | "
          f"LOW: {len(out)-len(hi)-len(md)}")
    print("--- HIGH-confidence pilots (human-reported PM + measurable repo) ---")
    for x in hi[:25]:
        print(f"  #{x['index']:>5} PM={x['stated_pm']:>6} ({x['planned_fte']}fte x {x['duration_months']}mo) "
              f"repos={x['n_github_repos']}  {x['title'][:48]}")
    print(f"Wrote {a.out}")

if __name__ == "__main__":
    main()
