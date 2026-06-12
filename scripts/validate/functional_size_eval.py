#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
functional_size_eval.py  —  the usable, PROSPECTIVE blockchain effort estimator
================================================================================
Goal: PM = PM from inputs a developer can write down BEFORE coding. KSLOC needs the
finished code; FUNCTIONAL SIZE (pallets, extrinsics, storage, events, ink! messages,
Solidity functions, contracts, RPCs; off-chain exports/functions/classes/routes) is
countable from a design spec. We calibrate effort on functional size and test it
head-to-head against KSLOC, leak-free, under one LOOCV protocol.

Models (log space, LOOCV, Duan smearing), target = measured PM:
  size_ksloc     : lnPM ~ a + b*ln(KSLOC)                      (retrospective baseline)
  size_equiv     : lnPM ~ a + b*ln(equivalent SLOC)            (retrospective baseline)
  fs_total       : lnPM ~ a + b*ln(1+ total functional units)  (PROSPECTIVE)
  fs_groups      : lnPM ~ a + b*ln(1+onchain) + c*ln(1+offchain)(PROSPECTIVE; learned weights)
  fs_groups_team : + d*ln(team_size)   (team_size = DOCUMENTED, leak-free, pre-build) (PROSPECTIVE)
  fs_plus_size   : lnPM ~ a + b*ln(equiv) + c*ln(1+units)      (does FS add over size?)

Leak-free: NO git-derived author/active-day count is used as a predictor (that leaks the
target). team_size comes from the grant application (documented_effort.csv), known before build.

Reuses cocomo_fit.load (clean gated set + equivalent SLOC). Reads functional units from
repo_attributes (joined in F.load's attribute row) and team_size from documented_effort.csv.
Output: reports/functional_size_eval.json (per-model metrics + best prospective model
coefficients + a predicted-vs-actual PM=PM table).
"""
import argparse, csv, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import cocomo_fit as F

ONCHAIN = ["n_pallets","n_extrinsics","n_storage","n_events","n_ink_msgs","n_sol_funcs","n_contracts_def","n_rpc"]
OFFCHAIN = ["n_exports","n_funcs","n_classes","n_routes"]

def _i(a, k):
    try: return max(int(float(a.get(k, 0) or 0)), 0)
    except (ValueError, TypeError): return 0

def loocv_ols(y, X):
    """LOOCV real-PM preds (Duan smearing) + full-data beta. X without intercept."""
    n = len(y); Xi = np.column_stack([np.ones(n), X]); preds = np.zeros(n)
    for i in range(n):
        idx = [j for j in range(n) if j != i]
        b, *_ = np.linalg.lstsq(Xi[idx], y[idx], rcond=None)
        r = y[idx] - Xi[idx] @ b
        preds[i] = math.exp(Xi[i] @ b) * math.exp(np.var(r) / 2)
    beta, *_ = np.linalg.lstsq(Xi, y, rcond=None)
    return preds, beta

def metrics(actual, pred):
    actual = np.asarray(actual); pred = np.asarray(pred); mre = np.abs(actual - pred) / actual
    mae = np.mean(np.abs(actual - pred)); n = len(actual)
    marp0 = np.mean(np.abs(actual[:, None] - actual[None, :]))
    return dict(SA=round(float(1 - mae/marp0), 4) if marp0 > 0 else None,
                MMRE=round(float(np.mean(mre)), 4), MdMRE=round(float(np.median(mre)), 4),
                PRED25=round(float(np.mean(mre <= .25)), 4), PRED30=round(float(np.mean(mre <= .30)), 4))

def main():
    ap = argparse.ArgumentParser()
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--meas", default=os.path.join(root, "data/calibration/measurements_census.csv"))
    ap.add_argument("--attr", default=os.path.join(root, "data/calibration/repo_attributes.csv"))
    ap.add_argument("--doc",  default=os.path.join(root, "data/calibration/documented_effort.csv"))
    ap.add_argument("--out",  default=os.path.join(root, "reports/functional_size_eval.json"))
    ap.add_argument("--pm", default="pm_mid", choices=["pm_mid","pm_low","pm_high"])
    a = ap.parse_args()

    cand = F.load(a.meas, a.attr, a.pm)
    n = len(cand)
    if n < 10: sys.exit(f"only {n} rows")

    # documented team_size (leak-free, pre-build) joined by project_id
    team = {}
    if os.path.exists(a.doc):
        for r in csv.DictReader(open(a.doc, encoding="utf-8")):
            try: team[r["project_id"]] = float(r["team_size"]) if r.get("team_size") else None
            except (ValueError, TypeError): pass
    team_vals = [t for t in team.values() if t and t > 0]
    team_median = float(np.median(team_vals)) if team_vals else 3.0

    y = np.array([math.log(pm) for (_m,_a,_S,pm) in cand])
    actual = np.exp(y)
    lnK = np.array([math.log(max(F._fnum(m,"ksloc_code") or 0.001, 0.001)) for (m,_a,_S,_pm) in cand])
    lnE = np.array([math.log(S) for (_m,_a,S,_pm) in cand])
    onU = np.array([sum(_i(a_,k) for k in ONCHAIN) for (_m,a_,_S,_pm) in cand], float)
    offU = np.array([sum(_i(a_,k) for k in OFFCHAIN) for (_m,a_,_S,_pm) in cand], float)
    totU = onU + offU
    ln1on = np.log1p(onU); ln1off = np.log1p(offU); ln1tot = np.log1p(totU)
    tcov = sum(1 for (m,_a,_S,_pm) in cand if team.get(m["project_id"]))
    lnteam = np.array([math.log(max(team.get(m["project_id"]) or team_median, 1.0)) for (m,_a,_S,_pm) in cand])

    specs = {
        "size_ksloc":      [lnK],
        "size_equiv":      [lnE],
        "fs_total":        [ln1tot],
        "fs_groups":       [ln1on, ln1off],
        "fs_groups_team":  [ln1on, ln1off, lnteam],
        "fs_plus_size":    [lnE, ln1tot],
    }
    prospective = {"fs_total", "fs_groups", "fs_groups_team"}   # no KSLOC -> usable before build

    results = {}; betas = {}
    for name, cols in specs.items():
        X = np.column_stack(cols)
        preds, beta = loocv_ols(y, X)
        results[name] = metrics(actual, preds)
        betas[name] = [round(float(b), 4) for b in beta]
        results[name]["prospective"] = name in prospective

    # best PROSPECTIVE model by SA (the usable tool)
    best = max(prospective, key=lambda k: results[k]["SA"] or -9)
    bcols = specs[best]; bX = np.column_stack(bcols)
    bpreds, bbeta = loocv_ols(y, bX)
    # PM=PM table (predicted vs actual) for the best prospective model, sorted by project size
    order = np.argsort(-totU)
    pmpm = []
    for i in list(order)[:20]:
        m = cand[i][0]
        pmpm.append(dict(project_id=m["project_id"], onchain_units=int(onU[i]), offchain_units=int(offU[i]),
                         team=round(float(math.exp(lnteam[i])),1),
                         pm_actual=round(float(actual[i]),2), pm_pred=round(float(bpreds[i]),2),
                         abs_pct_err=round(float(abs(actual[i]-bpreds[i])/actual[i]*100),1)))

    out = dict(pm_target=a.pm, n=n, team_size_coverage=f"{tcov}/{n}",
               models=results, coefficients=betas,
               best_prospective=dict(name=best, coefficients_intercept_then_terms=[round(float(b),4) for b in bbeta],
                                     terms=["intercept(lnA)"] + ([ "ln(1+onchain)","ln(1+offchain)","ln(team)"][:len(bbeta)-1]),
                                     A=round(math.exp(float(bbeta[0])),4), metrics=results[best]),
               pm_eq_pm_table=pmpm,
               note="Prospective models use ONLY design-spec-countable inputs (functional units, "
                    "documented team size) - no KSLOC, no git author/day counts (leak-free). "
                    "size_ksloc/size_equiv are retrospective baselines for the head-to-head.")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=2)

    print("="*72); print(f"  FUNCTIONAL-SIZE EVALUATION  (target={a.pm}, n={n}, team cov {tcov}/{n})"); print("="*72)
    for name, mm in results.items():
        tag = "PROSPECTIVE" if mm["prospective"] else "retrospective"
        print(f"  {name:>16} [{tag:>13}]: SA {mm['SA']:+.3f}  PRED25 {mm['PRED25']*100:3.0f}%  "
              f"PRED30 {mm['PRED30']*100:3.0f}%  MMRE {mm['MMRE']*100:3.0f}%")
    print(f"  best prospective = {best}: A={math.exp(bbeta[0]):.3f}  beta={[round(float(b),3) for b in bbeta[1:]]}")
    print(f"  wrote {a.out}")

if __name__ == "__main__":
    main()
