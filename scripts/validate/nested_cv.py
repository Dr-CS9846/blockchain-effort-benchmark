#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nested_cv.py  —  leakage-proof tuning harness (Stage-1 guardrail).

WHY THIS EXISTS
  The closed-form OLS calibrators (calibrate_size_effort / calibrate_bc_cocomo)
  have NO tuned hyperparameters, so plain LOOCV is already unbiased for them.
  Nested CV becomes essential the moment a model TUNES something (k in analogy,
  lambda in ridge, an outlier threshold, feature selection). This harness makes
  that tuning leakage-proof: for each outer held-out project, the hyperparameter
  is chosen by an INNER cross-validation over the remaining projects only — the
  held-out point is never seen during selection.

It is demonstrated on Analogy-Based Estimation (ABE / k-NN), a standard effort
baseline whose neighbour count k IS a real hyperparameter. The same harness will
wrap any tuned Stage-2 model.

USAGE
  python nested_cv.py --csv data/calibration/measurements.csv --size ksloc_code --effort measured
"""
import argparse, csv, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metrics as metricslib

def abe_predict(train_X, train_y, x, k):
    """k-NN analogy: mean log-effort of the k nearest neighbours (Euclidean in feature space)."""
    d = np.sqrt(((train_X - x) ** 2).sum(axis=1))
    idx = np.argsort(d)[:k]
    return float(np.mean(train_y[idx]))

def _inner_loocv_mae(X, y, k):
    n = len(y); preds = np.zeros(n)
    for i in range(n):
        mask = [j for j in range(n) if j != i]
        preds[i] = abe_predict(X[mask], y[mask], X[i], k)
    return metricslib.mae(np.exp(y), np.exp(preds))   # MAE in effort units

def inner_select_k(X, y, grid):
    """Pick k that minimises INNER-LOOCV MAE on the given training subset only."""
    best_k, best = grid[0], float("inf")
    for k in grid:
        if k > len(y) - 1: continue
        m = _inner_loocv_mae(X, y, k)
        if m < best: best, best_k = m, k
    return best_k

def nested_loocv(X, y, grid):
    """Outer LOOCV; k selected by inner CV on outer-train only. Returns (preds, chosen_k)."""
    n = len(y); preds = np.zeros(n); chosen = []
    for i in range(n):
        outer = [j for j in range(n) if j != i]          # held-out i excluded here ...
        k = inner_select_k(X[outer], y[outer], grid)     # ... so tuning never sees i
        chosen.append(int(k))
        preds[i] = abe_predict(X[outer], y[outer], X[i], k)
    return preds, chosen

def load(path, size_col, effort_mode):
    S=[]; Y=[]; names=[]
    for r in csv.DictReader(open(path)):
        if r.get("status") != "OK": continue
        try:
            size=float(r[size_col])
            eff=float(r["active_person_months"]) if effort_mode=="measured" else float(r["planned_pm"])
        except (ValueError, KeyError): continue
        if size>0 and eff>0:
            S.append(size); Y.append(eff); names.append(r.get("project_name",""))
    return np.array(S), np.array(Y), names

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/calibration/measurements.csv")
    ap.add_argument("--size", default="ksloc_code")
    ap.add_argument("--effort", default="measured", choices=["measured","planned"])
    ap.add_argument("--grid", default="1,2,3")
    a=ap.parse_args()
    if not os.path.exists(a.csv): sys.exit(f"{a.csv} not found - run measure first.")
    size, eff, names = load(a.csv, a.size, a.effort)
    n=len(size)
    if n<4: sys.exit(f"Only {n} usable rows; need >=4 for nested CV. Resolve more repos first.")
    grid=[int(x) for x in a.grid.split(",")]
    X=np.log(size).reshape(-1,1); y=np.log(eff)
    preds_log, chosen = nested_loocv(X, y, grid)
    preds=np.exp(preds_log)
    s=metricslib.summary(eff, preds)
    out=dict(model="ABE (k-NN analogy), k tuned by nested LOOCV",
             grid=grid, chosen_k_per_fold=chosen, metrics=s, projects=names)
    json.dump(out, open("nested_cv_results.json","w"), indent=2)
    print("="*60); print("  NESTED-CV ABE BASELINE (leakage-proof tuning)"); print("="*60)
    print(f"  n={n}  grid={grid}  chosen k per fold={chosen}")
    print(f"  MMRE {s['MMRE']*100:5.1f}%  PRED25 {s['PRED25']*100:5.1f}%  MAE {s['MAE']:.2f}  SA {s['SA_vs_random']*100:5.1f}%")
    print("="*60)

if __name__=="__main__": main()
