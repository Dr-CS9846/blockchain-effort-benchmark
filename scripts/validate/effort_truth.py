#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
effort_truth.py  —  Boehm-style standardisation of the EFFORT ground truth
==========================================================================
Boehm calibrated COCOMO to REPORTED person-months, not a single proxy. We have THREE
independent effort signals per W3F grant milestone; this script reconciles them into a
robust ground truth and tells us which to calibrate against.

  (1) git_pm     = active_dev_days / 19            (mined activity proxy; what we used)
  (2) planned_pm = planned_FTE x planned_duration  (team's own effort estimate, from the grant app)
  (3) cost_pm    = cost_usd / (rate* x 152)         (PAID labour; rate* derived, see below)

rate* (effective blended $/PH) is DERIVED, not assumed: anchored on the self-estimates,
  rate* = median over repos having BOTH cost and planned of  cost_usd / (planned_pm x 152).
We then apply rate* to every repo with a cost to obtain a money-grounded effort, and we
report how the three measures agree (log-space corr, ratios, coverage). Output:
reports/effort_truth.json — the evidence for choosing the calibration target.
"""
import argparse, csv, json, math, os, statistics, sys
try:
    import numpy as np
except ModuleNotFoundError:
    sys.exit("numpy required")

PH_PER_PM = 152.0      # Boehm person-month = 152 person-hours (verified earlier)

def _f(r, k):
    try: return float(r[k])
    except (ValueError, KeyError, TypeError): return None
def _norm(u): return (u or "").strip().lower().rstrip("/").replace(".git", "")

def main():
    ap = argparse.ArgumentParser()
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--meas", default=os.path.join(root, "data/calibration/measurements_census.csv"))
    ap.add_argument("--audit", default=os.path.join(root, "reports/census_audit.csv"))
    ap.add_argument("--out",  default=os.path.join(root, "reports/effort_truth.json"))
    a = ap.parse_args()

    # milestone count per project (whole-grant cost/planned span this many delivered milestones)
    mile = {}
    if os.path.exists(a.audit):
        for r in csv.DictReader(open(a.audit, encoding="utf-8")):
            try: mile[r["project_id"]] = max(1, int(float(r.get("n_delivery_files") or 1)))
            except (ValueError, TypeError): mile[r["project_id"]] = 1

    rows = [r for r in csv.DictReader(open(a.meas, encoding="utf-8")) if r.get("status") == "OK"]
    # dedup by repo (latest delivery)
    best = {}
    for r in rows:
        k = _norm(r.get("repo_url","")) or r["project_id"]
        key = (r.get("effort_until",""), _f(r,"ksloc_code") or 0)
        if k not in best or key > (best[k].get("effort_until",""), _f(best[k],"ksloc_code") or 0):
            best[k] = r
    R = list(best.values())

    recs = []
    for r in R:
        git_pm = _f(r,"pm_mid")
        fte = _f(r,"planned_fte"); dur = _f(r,"planned_duration_months")
        planned_pm = _f(r,"planned_pm") or ((fte*dur) if (fte and dur) else None)
        cost = _f(r,"cost_usd")
        recs.append(dict(pid=r["project_id"], git_pm=git_pm, planned_pm=planned_pm, cost=cost))

    # rate* from repos with BOTH cost and planned_pm>0
    rate_samples = [r["cost"]/(r["planned_pm"]*PH_PER_PM)
                    for r in recs if r["cost"] and r["planned_pm"] and r["planned_pm"]>0 and r["cost"]>0]
    rate_star = statistics.median(rate_samples) if rate_samples else None

    for r in recs:
        r["cost_pm"] = (r["cost"]/(rate_star*PH_PER_PM)) if (rate_star and r["cost"] and r["cost"]>0) else None
        K = mile.get(r["pid"], 1)
        r["milestones"] = K
        # SCOPE-MATCHED economic effort: whole-grant cost spread over its delivered milestones
        r["cost_pm_permilestone"] = (r["cost_pm"]/K) if r.get("cost_pm") else None

    def logpairs(ka, kb):
        xs = [(math.log(r[ka]), math.log(r[kb])) for r in recs
              if r.get(ka) and r.get(kb) and r[ka]>0 and r[kb]>0]
        if len(xs) < 8: return None
        a_ = np.array([p[0] for p in xs]); b_ = np.array([p[1] for p in xs])
        ratio = [math.exp(p[0]-p[1]) for p in xs]   # ka/kb
        return dict(n=len(xs), corr_log=round(float(np.corrcoef(a_,b_)[0,1]),3),
                    median_ratio=round(float(statistics.median(ratio)),3))

    cov = lambda k: sum(1 for r in recs if r.get(k) and r[k]>0)
    out = dict(
        n_repos=len(recs), person_hours_per_pm=PH_PER_PM,
        derived_blended_rate_usd_per_hour=round(rate_star,1) if rate_star else None,
        rate_sample_n=len(rate_samples),
        coverage=dict(git_pm=cov("git_pm"), planned_pm=cov("planned_pm"),
                      cost_pm=cov("cost_pm"), cost=cov("cost")),
        median_milestones_per_grant=round(statistics.median([r["milestones"] for r in recs]),1),
        agreement=dict(
            git_vs_planned=logpairs("git_pm","planned_pm"),
            git_vs_cost   =logpairs("git_pm","cost_pm"),
            planned_vs_cost=logpairs("planned_pm","cost_pm"),
            # the clinching test: at the SAME (per-milestone) scope, does git track paid effort?
            git_vs_cost_PERMILESTONE=logpairs("git_pm","cost_pm_permilestone")),
        note="median_ratio ka/kb. If git_pm systematically < planned/cost, the git proxy "
             "under-counts true labour (Boehm calibrated to reported effort).")
    # proposed reconciled effort: prefer cost_pm (paid labour) where present & sane, else planned, else git
    rec_rows = []
    for r in recs:
        src = None; val = None
        if r.get("cost_pm") and r["cost_pm"]>0: src, val = "cost", r["cost_pm"]
        elif r.get("planned_pm") and r["planned_pm"]>0: src, val = "planned", r["planned_pm"]
        elif r.get("git_pm") and r["git_pm"]>0: src, val = "git", r["git_pm"]
        if val: rec_rows.append((r["pid"], src, round(val,3)))
    out["reconciled_effort_source_counts"] = {
        s: sum(1 for _,ss,_ in rec_rows if ss==s) for s in ("cost","planned","git")}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out,"w"), indent=2)
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
