#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
explore_models.py — honest attempt to raise LOOCV accuracy with LEGITIMATE, prospective methods.
No target leakage (no ln_authors / post-hoc func counts). All inputs knowable before build.
Models tried (all LOOCV, Duan smearing, same protocol as paper_stats):
  B1   size-only log-OLS                         (baseline)
  ABE  analogy-based estimation, k-NN in log-size (Shepperd-Schofield; a recognised SOTA family)
  ABEa ABE within archetype stratum (prospective)
  RB   robust-ish: size + archetype, log-OLS
  SF   per-archetype size-only (stratified intercept+slope)
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import cocomo_fit as F
import cocomo_localcal as L

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
meas = os.path.join(root, "data/calibration/measurements_census.csv")
attr = os.path.join(root, "data/calibration/repo_attributes.csv")

def sa(actual, pred):
    actual = np.asarray(actual); pred = np.asarray(pred)
    mae = np.mean(np.abs(actual - pred)); marp0 = np.mean(np.abs(actual[:, None] - actual[None, :]))
    mre = np.abs(actual - pred) / actual
    return dict(SA=1 - mae / marp0, PRED25=np.mean(mre <= .25), PRED30=np.mean(mre <= .30),
                MdMRE=np.median(mre))

def ols_loocv(y, X):
    n = len(y); Xi = np.column_stack([np.ones(n), X]); preds = np.zeros(n)
    for i in range(n):
        idx = [j for j in range(n) if j != i]
        b, *_ = np.linalg.lstsq(Xi[idx], y[idx], rcond=None)
        r = y[idx] - Xi[idx] @ b
        preds[i] = math.exp(Xi[i] @ b) * math.exp(np.var(r) / 2)
    return preds

def abe_loocv(y, feats, k, strata=None):
    """k-NN analogy on standardised features; estimate = mean of k nearest neighbours' real PM."""
    n = len(y); pm = np.exp(y); preds = np.zeros(n)
    Z = (feats - feats.mean(0)) / (feats.std(0) + 1e-9)
    for i in range(n):
        cand = [j for j in range(n) if j != i and (strata is None or strata[j] == strata[i])]
        if len(cand) < 1: cand = [j for j in range(n) if j != i]
        d = np.array([np.sum((Z[i] - Z[j]) ** 2) for j in cand])
        nn = [cand[j] for j in np.argsort(d)[:min(k, len(cand))]]
        preds[i] = np.mean(pm[nn])
    return preds

def run(tag, minloc, maxloc, maxdur):
    cand = F.load(meas, attr, "pm_mid", maxlocday=maxloc, minlocday=minloc, maxduration=maxdur)
    n = len(cand)
    y = np.array([math.log(pm) for (_m, _a, _S, pm) in cand])
    lnS = np.array([math.log(S) for (_m, _a, S, _pm) in cand])
    onch = np.array([1.0 if L.archetype_of(a) in ("onchain_pallet", "smart_contract") else 0.0
                     for (_m, a, _S, _pm) in cand])
    arche = np.array([L.archetype_of(a) for (_m, a, _S, _pm) in cand])
    actual = np.exp(y)

    res = {}
    res["B1_size_only"] = sa(actual, ols_loocv(y, lnS.reshape(-1, 1)))
    res["RB_size+arch"] = sa(actual, ols_loocv(y, np.column_stack([lnS, onch])))
    for k in (1, 2, 3, 5):
        res[f"ABE_k{k}"] = sa(actual, abe_loocv(y, lnS.reshape(-1, 1), k))
        res[f"ABEarch_k{k}"] = sa(actual, abe_loocv(y, lnS.reshape(-1, 1), k, strata=arche))
    # per-archetype size-only (own intercept+slope per stratum)
    preds = np.zeros(n)
    for a_ in set(arche):
        idx = np.where(arche == a_)[0]
        if len(idx) >= 6:
            p = ols_loocv(y[idx], lnS[idx].reshape(-1, 1))
            preds[idx] = p
        else:
            preds[idx] = ols_loocv(y, lnS.reshape(-1, 1))[idx]
    res["SF_per_archetype_size"] = sa(actual, preds)

    print(f"\n===== {tag}  (n={n}) =====")
    for k, m in sorted(res.items(), key=lambda kv: -kv[1]["SA"]):
        print(f"  {k:22} SA {m['SA']:+.3f}  PRED25 {m['PRED25']*100:3.0f}%  "
              f"PRED30 {m['PRED30']*100:3.0f}%  MdMRE {m['MdMRE']:.3f}")

if __name__ == "__main__":
    run("GATED", 15.0, 200.0, 18.0)
    run("UN-GATED", 0.0, 1e6, 1e6)
