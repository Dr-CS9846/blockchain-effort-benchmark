#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cocomo_bayes.py  —  Bayesian calibration of blockchain COCOMO II (Chulani-Boehm-Steece 1999)
=============================================================================================
Boehm did NOT trust raw regression on noisy data (it yields unstable / sign-flipped driver
coefficients — exactly our pure-OLS exponent 0.46 problem). COCOMO II is calibrated by a
*Bayesian* update: the PRIOR is the published model (Boehm's expert weights), and the POSTERIOR
is a precision-weighted combination of that prior with the local-data regression. Where the data
is weak (high variance), the coefficient stays near Boehm's expert value; where the data is
strong, it follows the data.

Model (log space):   ln PM = lnA + b_S * ln S + b_sf * (E - B)*ln S + Σ_i b_i * ln(EM_i)
Prior means (the published COCOMO II model):  b_S = B = 0.91,  b_sf = 1,  b_i = 1 for every EM/BC.
lnA (the local productivity constant) gets a FLAT prior — Boehm always recalibrates A locally.

Posterior (ridge-to-prior / g-prior):   b* = (XᵀX + τ·D)⁻¹ (Xᵀy + τ·D·μ)
  D = diag(prior precisions, 0 for the flat intercept), τ = prior strength (swept; τ→0 is free OLS,
  τ→∞ is the fixed published model). We report LOOCV SA/PRED across τ and pick the variance-justified
  point, with full sensitivity — no single hand-set value drives the result.

Reuses cocomo_fit.load (clean gated set + equivalent SLOC) and its 22+7-driver synthesis.
Output: reports/cocomo_bayes_{pm}.json.
"""
import argparse, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import cocomo2_tables as T
import cocomo_fit as F
import cocomo_localcal as L     # archetype_of, _f, _i

def _onchain(a):
    return 1.0 if L.archetype_of(a) in ("onchain_pallet", "smart_contract") else 0.0

def design(cand, cols, rows, nonconst):
    """Universal COCOMO-Blockchain design. Canonical terms (size exponent, scale-factor sensitivity,
    standard EMs) carry the PUBLISHED prior (mean 1 / B). Blockchain drivers that earned their place
    empirically (archetype, team size, functional size) are added with a regularising prior (mean 0)."""
    y   = np.array([math.log(pm) for (_m,_a,_S,pm) in cand])
    lnS = np.array([math.log(S)  for (_m,_a,S,_pm) in cand])
    E   = np.array([E for (_pid,_S,_pm,E,_SF,_EM,_BC) in rows])
    cols_list = [lnS, (E - T.B)*lnS] + [np.array(cols[v]) for v in nonconst]
    mu_list   = [T.B, 1.0] + [1.0]*len(nonconst)            # published-model prior
    names     = ["lnS(exponent)", "sf_sensitivity"] + list(nonconst)
    # blockchain drivers (prior mean 0 -> shrink to no-effect unless data supports them)
    onchain = np.array([_onchain(a) for (_m,a,_S,_pm) in cand])
    lnauth  = np.array([math.log(max(L._f(m,"distinct_authors") or 1, 1)) for (m,_a,_S,_pm) in cand])
    fsize   = np.array([math.log1p(sum(max(L._f(a,k) or 0, 0) for k in
                        ("n_extrinsics","n_ink_msgs","n_sol_funcs","n_exports","n_funcs"))) for (_m,a,_S,_pm) in cand])
    for nm, c in (("onchain", onchain), ("ln_authors", lnauth), ("ln_funcsize", fsize)):
        if np.std(c) > 1e-9:
            cols_list.append(c); mu_list.append(0.0); names.append(nm)
    return y, np.column_stack(cols_list), np.array(mu_list), names

def bayes_solve(y, X, mu, tau):
    """Ridge-to-prior posterior. Intercept (lnA) flat (precision 0); other terms shrink to mu·prior.
    lstsq (least-norm) so τ=0 with any residual collinearity is still well-posed."""
    n, k = X.shape
    Xi = np.column_stack([np.ones(n), X])                 # col0 = intercept (lnA)
    mu_full = np.concatenate([[0.0], mu])
    d = np.concatenate([[0.0], np.ones(k)])               # flat on intercept, prior precision on rest
    D = np.diag(d)
    A = Xi.T @ Xi + tau*D
    b = Xi.T @ y + tau*D @ mu_full
    return np.linalg.lstsq(A, b, rcond=None)[0]

def loocv(y, X, mu, tau):
    n = len(y); Xi = np.column_stack([np.ones(n), X]); preds = np.zeros(n)
    k = X.shape[1]; mu_full = np.concatenate([[0.0], mu]); d = np.concatenate([[0.0], np.ones(k)]); D = np.diag(d)
    for i in range(n):
        idx = [j for j in range(n) if j != i]
        Ai = Xi[idx].T @ Xi[idx] + tau*D
        bi = Xi[idx].T @ y[idx] + tau*D @ mu_full
        beta = np.linalg.lstsq(Ai, bi, rcond=None)[0]
        res = y[idx] - Xi[idx] @ beta; smear = math.exp(np.var(res)/2)
        preds[i] = math.exp(Xi[i] @ beta) * smear
    pm = np.exp(y); mre = np.abs(pm-preds)/pm; mae = np.mean(np.abs(pm-preds))
    marp0 = np.mean([np.mean(np.abs(pm-pm[j])) for j in range(n)])
    return dict(SA=float(1-mae/marp0), PRED25=float(np.mean(mre<=.25)),
                PRED30=float(np.mean(mre<=.30)), MMRE=float(np.mean(mre)), MdMRE=float(np.median(mre)))

def main():
    ap = argparse.ArgumentParser()
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--meas", default=os.path.join(root,"data/calibration/measurements_census.csv"))
    ap.add_argument("--attr", default=os.path.join(root,"data/calibration/repo_attributes.csv"))
    ap.add_argument("--out",  default=os.path.join(root,"reports/cocomo_bayes.json"))
    ap.add_argument("--pm", default="pm_mid", choices=["pm_mid","pm_low","pm_high"])
    a = ap.parse_args()

    cand = F.load(a.meas, a.attr, a.pm)         # clean gated set + equivalent SLOC
    n = len(cand)
    if n < 10: sys.exit(f"only {n} rows")
    y, q, cols, rows = F.q_and_columns(cand)
    all_mult = F.EM_NAMES + ["BC_BEM","BC_DC","BC_EM_GAS","BC_EM_AUD","BC_EM_MC","BC_EM_REG","BC_EM_NODE"]
    nonconst0 = [v for v in all_mult if np.std(cols[v]) > 1e-9]
    # drop PROVEN-collinear drivers (BC_EM_AUD=RELY, BC_EM_GAS=TIME, BC_DC=PVOL, etc.) -> identifiable set
    nonconst = []; dropped = []
    for v in nonconst0:
        cv = np.array(cols[v])
        if any(abs(np.corrcoef(cv, np.array(cols[k]))[0,1]) > 0.999 for k in nonconst):
            dropped.append(v); continue
        nonconst.append(v)
    yv, X, mu, names = design(cand, cols, rows, nonconst)

    # sweep prior strength tau: 0 = free OLS, large = fixed published model
    taus = [0.0, 0.5, 1.0, 2.0, 5.0, 10.0, 25.0, 100.0, 1e6]
    sweep = {}
    for t in taus:
        sweep[f"tau_{t:g}"] = loocv(yv, X, mu, t)
    # choose the LOOCV-optimal tau (best out-of-sample SA) as the calibrated model
    best_t = max(taus, key=lambda t: sweep[f"tau_{t:g}"]["SA"])
    beta = bayes_solve(yv, X, mu, best_t)
    coeffs = dict(intercept_lnA=round(float(beta[0]),4))
    for nm, b in zip(names, beta[1:]): coeffs[nm] = round(float(b),4)

    out = dict(pm_target=a.pm, n=n, B_prior=T.B,
               drivers_used=nonconst, drivers_dropped_collinear=dropped,
               method="Bayesian ridge-to-prior (Chulani-Boehm-Steece 1999); prior=published COCOMO II",
               tau_sweep=sweep, chosen_tau=best_t,
               calibrated=dict(metrics=sweep[f"tau_{best_t:g}"], A=round(math.exp(float(beta[0])),4),
                               coefficients=coeffs),
               free_ols=sweep["tau_0"], fixed_published=sweep["tau_1e+06"],
               note="tau->0 free OLS (unstable); tau->inf fixed published COCOMO II. Bayesian optimum "
                    "shrinks noisy driver weights toward Boehm's expert values, stabilising the model.")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out,"w"), indent=2)
    print(f"n={n}  chosen tau={best_t}")
    for t in taus:
        m = sweep[f"tau_{t:g}"]
        print(f"  tau={t:>8g}: SA {m['SA']:+.3f}  PRED25 {m['PRED25']*100:3.0f}%  PRED30 {m['PRED30']*100:3.0f}%  MMRE {m['MMRE']*100:3.0f}%")
    print(f"  calibrated A={math.exp(beta[0]):.3f}, size exponent={beta[1]:.3f}")

if __name__ == "__main__":
    main()
