#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
paper_stats.py  —  referee-grade statistics for the COCOMO-Blockchain papers
============================================================================
Computes the analyses flagged [COMPUTE] in the methodology manuscript, on the frozen clean gated
set (F.load), under ONE LOOCV protocol so every model is apples-to-apples:

  1. Descriptive statistics of the clean set (size, PM, duration, authors, velocity).
  2. Size-effort decoupling refresh on n=127 (corr(log Size, log PM); productivity spread).
  3. Baselines: B0 guessing, B1 size-only power law, B2 ATLM-lite (Whigham 2015 spirit:
     transformed linear model, deterministic, no tuning), vs fixed-published COCOMO II and the
     Bayesian ridge-to-prior model.
  4. Bootstrap 95% CIs (case resampling, B=2000) for every model's SA.
  5. Shepperd-MacDonell standardised effect size Δ and randomisation-test p vs guessing.
  6. Nested cross-validation for the Bayesian τ (inner-fold selection) — guards selection optimism.
  7. Paired Wilcoxon signed-rank model comparisons (normal approx), win/tie/loss.

numpy-only (CI installs numpy). Reuses cocomo_fit (load + synthesis + q), cocomo_bayes (design),
cocomo_localcal (_f, archetype). Output: reports/paper_stats_{pm}.json
"""
import argparse, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import cocomo2_tables as T
import cocomo_fit as F
import cocomo_localcal as L
import cocomo_bayes as CB

RNG = np.random.default_rng(20260612)

# ── LOOCV predictors (real PM) ────────────────────────────────────────────────────────
def ols_loocv_preds(y, X):
    """LOOCV real-PM predictions for log-linear OLS (Duan smearing). X without intercept column."""
    n = len(y); Xi = np.column_stack([np.ones(n), X]); preds = np.zeros(n)
    for i in range(n):
        idx = [j for j in range(n) if j != i]
        b, *_ = np.linalg.lstsq(Xi[idx], y[idx], rcond=None)
        r = y[idx] - Xi[idx] @ b
        preds[i] = math.exp(Xi[i] @ b) * math.exp(np.var(r) / 2)
    return preds

def fixed_published_loocv_preds(y, q):
    """COCOMO II with published magnitudes; only lnA recalibrated per fold (Duan smearing)."""
    n = len(y); preds = np.zeros(n)
    for i in range(n):
        idx = [j for j in range(n) if j != i]
        lnA = np.mean(y[idx] - q[idx]); smear = math.exp(np.var(y[idx] - q[idx]) / 2)
        preds[i] = math.exp(lnA + q[i]) * smear
    return preds

def _bayes_beta(Xi, y, mu_full, D, tau):
    A = Xi.T @ Xi + tau * D; b = Xi.T @ y + tau * D @ mu_full
    try:
        return np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        return np.linalg.lstsq(A, b, rcond=None)[0]

def bayes_loocv_preds(yv, X, mu, tau):
    n = len(yv); Xi = np.column_stack([np.ones(n), X]); preds = np.zeros(n)
    k = X.shape[1]; mu_full = np.concatenate([[0.0], mu]); D = np.diag(np.concatenate([[0.0], np.ones(k)]))
    for i in range(n):
        idx = [j for j in range(n) if j != i]
        beta = _bayes_beta(Xi[idx], yv[idx], mu_full, D, tau)
        res = yv[idx] - Xi[idx] @ beta
        preds[i] = math.exp(Xi[i] @ beta) * math.exp(np.var(res) / 2)
    return preds

def bayes_nested_loocv_preds(yv, X, mu, grid):
    """Outer LOOCV; τ chosen on inner LOOCV of each training fold (nested) — unbiased τ selection."""
    n = len(yv); Xi = np.column_stack([np.ones(n), X]); preds = np.zeros(n); chosen = []
    k = X.shape[1]; mu_full = np.concatenate([[0.0], mu]); D = np.diag(np.concatenate([[0.0], np.ones(k)]))
    for i in range(n):
        tr = [j for j in range(n) if j != i]
        best_t, best_sa = grid[0], -1e9
        for t in grid:
            ip = np.zeros(len(tr)); ya = np.exp(yv[tr])
            for a2, iidx in enumerate(tr):
                inner = [j for j in tr if j != iidx]
                beta = _bayes_beta(Xi[inner], yv[inner], mu_full, D, t)
                res = yv[inner] - Xi[inner] @ beta
                ip[a2] = math.exp(Xi[iidx] @ beta) * math.exp(np.var(res) / 2)
            sa, _, _ = sa_of(ya, ip)
            if sa > best_sa: best_sa, best_t = sa, t
        beta = _bayes_beta(Xi[tr], yv[tr], mu_full, D, best_t)
        res = yv[tr] - Xi[tr] @ beta
        preds[i] = math.exp(Xi[i] @ beta) * math.exp(np.var(res) / 2)
        chosen.append(best_t)
    return preds, chosen

# ── metrics / inference ───────────────────────────────────────────────────────────────
def sa_of(actual, pred):
    actual = np.asarray(actual); pred = np.asarray(pred)
    mae = np.mean(np.abs(actual - pred)); n = len(actual)
    marp0 = np.mean(np.abs(actual[:, None] - actual[None, :]))
    return (1 - mae / marp0 if marp0 > 0 else float("nan")), float(mae), float(marp0)

def metrics(actual, pred):
    actual = np.asarray(actual); pred = np.asarray(pred); mre = np.abs(actual - pred) / actual
    sa, mae, _ = sa_of(actual, pred)
    return dict(SA=round(float(sa), 4), MAE=round(mae, 3), MMRE=round(float(np.mean(mre)), 4),
                MdMRE=round(float(np.median(mre)), 4), PRED25=round(float(np.mean(mre <= .25)), 4),
                PRED30=round(float(np.mean(mre <= .30)), 4))

def bootstrap_sa_ci(actual, pred, B=2000):
    actual = np.asarray(actual); pred = np.asarray(pred); n = len(actual); sas = []
    for _ in range(B):
        idx = RNG.integers(0, n, n); a = actual[idx]; p = pred[idx]
        mae = np.mean(np.abs(a - p)); marp0 = np.mean(np.abs(a[:, None] - a[None, :]))
        if marp0 > 0: sas.append(1 - mae / marp0)
    lo, hi = np.percentile(sas, [2.5, 97.5])
    return [round(float(lo), 4), round(float(hi), 4)]

def effect_vs_guessing(actual, model_mae, runs=5000):
    actual = np.asarray(actual); n = len(actual); maes = np.empty(runs)
    for r in range(runs):
        maes[r] = np.mean(np.abs(actual - actual[RNG.integers(0, n, n)]))
    mbar, s = maes.mean(), maes.std()
    delta = (mbar - model_mae) / s if s > 0 else float("nan")
    p = float(np.mean(maes <= model_mae))            # randomisation p: P(guess at least as good)
    return round(float(delta), 3), round(p, 5), round(float(mbar), 3), round(float(s), 3)

def wilcoxon(ae_a, ae_b):
    d = np.asarray(ae_a) - np.asarray(ae_b); d = d[d != 0]; n = len(d)
    wins = int(np.sum(d < 0)); losses = int(np.sum(d > 0))   # a better when its error smaller
    if n < 6: return dict(z=None, p=None, a_better=wins, b_better=losses, ties=int(len(ae_a)-n))
    r = np.argsort(np.argsort(np.abs(d))) + 1
    W = min(r[d > 0].sum(), r[d < 0].sum())
    mu = n * (n + 1) / 4; sig = math.sqrt(n * (n + 1) * (2 * n + 1) / 24); z = (W - mu) / sig
    p = 2 * (0.5 * (1 + math.erf(-abs(z) / math.sqrt(2))))
    return dict(z=round(float(z), 3), p=round(float(p), 5), a_better=wins, b_better=losses,
                ties=int(len(ae_a) - n))

def benjamini_hochberg(pairs):
    """pairs: list of (label, p). Returns label->(p, q) with BH-adjusted q."""
    valid = [(lab, p) for lab, p in pairs if p is not None]
    m = len(valid); out = {}
    for rank, (lab, p) in enumerate(sorted(valid, key=lambda x: x[1]), start=1):
        out[lab] = dict(p=round(p, 5), q=round(min(p * m / rank, 1.0), 5))
    for lab, p in pairs:
        if p is None: out[lab] = dict(p=None, q=None)
    return out

def main():
    ap = argparse.ArgumentParser()
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--meas", default=os.path.join(root, "data/calibration/measurements_census.csv"))
    ap.add_argument("--attr", default=os.path.join(root, "data/calibration/repo_attributes.csv"))
    ap.add_argument("--out",  default=os.path.join(root, "reports/paper_stats.json"))
    ap.add_argument("--pm", default="pm_mid", choices=["pm_mid", "pm_low", "pm_high"])
    ap.add_argument("--boot", type=int, default=2000)
    a = ap.parse_args()

    cand = F.load(a.meas, a.attr, a.pm)
    n = len(cand)
    if n < 10: sys.exit(f"only {n} rows")
    y, q, cols, rows = F.q_and_columns(cand)
    actual = np.exp(y)

    # 1. descriptive statistics
    def col(fn): return np.array([fn(m, a_, S, pm) for (m, a_, S, pm) in cand], float)
    ks   = col(lambda m, a_, S, pm: F._fnum(m, "ksloc_code") or 0.0)
    equiv= col(lambda m, a_, S, pm: S)
    pmv  = col(lambda m, a_, S, pm: pm)
    dur  = col(lambda m, a_, S, pm: F._fnum(m, "actual_duration_months") or 0.0)
    auth = col(lambda m, a_, S, pm: F._fnum(m, "distinct_authors") or 0.0)
    ad   = col(lambda m, a_, S, pm: F._fnum(m, "active_dev_days") or 0.0)
    vel  = np.divide(ks * 1000, ad, out=np.full_like(ks, np.nan), where=ad > 0)
    def desc(x):
        x = x[np.isfinite(x)]
        return dict(median=round(float(np.median(x)), 3), q1=round(float(np.percentile(x, 25)), 3),
                    q3=round(float(np.percentile(x, 75)), 3), min=round(float(x.min()), 3),
                    max=round(float(x.max()), 3))
    descriptive = dict(equivalent_ksloc=desc(equiv), pm=desc(pmv), duration_months=desc(dur),
                       distinct_authors=desc(auth), velocity_loc_per_active_day=desc(vel))

    # 2. size-effort decoupling refresh
    lnks = np.log(np.where(ks > 0, ks, np.nan)); lnpm = np.log(pmv); lneq = np.log(equiv)
    mks = np.isfinite(lnks)
    prod = pmv / np.where(ks > 0, ks, np.nan)   # PM per KSLOC
    decoupling = dict(
        n=int(mks.sum()),
        corr_logksloc_logpm=round(float(np.corrcoef(lnks[mks], lnpm[mks])[0, 1]), 3),
        corr_logequiv_logpm=round(float(np.corrcoef(lneq, lnpm)[0, 1]), 3),
        productivity_pm_per_ksloc=dict(min=round(float(np.nanmin(prod)), 3),
                                       max=round(float(np.nanmax(prod)), 3),
                                       spread_x=round(float(np.nanmax(prod) / np.nanmin(prod)), 1)))

    # 3-7. models -> LOOCV preds
    lnS = np.array([math.log(S) for (_m, _a, S, _pm) in cand])
    lnauth = np.array([math.log(max(L._f(m, "distinct_authors") or 1, 1)) for (m, _a, _S, _pm) in cand])
    fsize = np.array([math.log1p(sum(max(L._f(a_, k) or 0, 0) for k in
                     ("n_extrinsics", "n_ink_msgs", "n_sol_funcs", "n_exports", "n_funcs")))
                      for (_m, a_, _S, _pm) in cand])
    onchain = np.array([CB._onchain(a_) for (_m, a_, _S, _pm) in cand])

    preds = {}
    preds["B1_size_only"] = ols_loocv_preds(y, lnS.reshape(-1, 1))
    atlm_cols = [lnS, lnauth, fsize] + ([onchain] if np.std(onchain) > 1e-9 else [])
    preds["B2_ATLM"] = ols_loocv_preds(y, np.column_stack(atlm_cols))
    preds["fixed_published"] = fixed_published_loocv_preds(y, q)

    # Bayesian: identifiable design (drop proven-collinear), sweep τ, nested-CV τ
    all_mult = F.EM_NAMES + ["BC_BEM", "BC_DC", "BC_EM_GAS", "BC_EM_AUD", "BC_EM_MC", "BC_EM_REG", "BC_EM_NODE"]
    nonconst0 = [v for v in all_mult if np.std(cols[v]) > 1e-9]
    nonconst, dropped = [], []
    for v in nonconst0:
        cv = np.array(cols[v])
        if any(abs(np.corrcoef(cv, np.array(cols[k]))[0, 1]) > 0.999 for k in nonconst):
            dropped.append(v); continue
        nonconst.append(v)
    yv, Xb, mu, names = CB.design(cand, cols, rows, nonconst)
    taus = [0.0, 0.5, 1.0, 2.0, 5.0, 10.0]
    tau_sweep = {}
    for t in taus:
        p = bayes_loocv_preds(yv, Xb, mu, t); tau_sweep[f"tau_{t:g}"] = sa_of(actual, p)[0]
    best_t = max(taus, key=lambda t: tau_sweep[f"tau_{t:g}"])
    preds["bayesian_tau_opt"] = bayes_loocv_preds(yv, Xb, mu, best_t)
    nested_preds, chosen = bayes_nested_loocv_preds(yv, Xb, mu, [0.0, 1.0, 5.0])
    preds["bayesian_nested"] = nested_preds

    # metrics + bootstrap CI + effect size for each model
    model_block = {}
    for name, p in preds.items():
        mm = metrics(actual, p)
        mm["SA_95CI"] = bootstrap_sa_ci(actual, p, a.boot)
        d, pv, mbar, s = effect_vs_guessing(actual, np.mean(np.abs(actual - p)))
        mm["effect_size_delta"] = d; mm["randomisation_p"] = pv
        model_block[name] = mm
    guessing_marp0 = sa_of(actual, actual)[2]   # MAE_p0 reference (for context)

    # paired Wilcoxon vs the size-only baseline (does each model beat B1?) + BH correction
    ae = {k: np.abs(actual - v) for k, v in preds.items()}
    comparisons = {}
    raw_p = []
    for name in ("B2_ATLM", "fixed_published", "bayesian_tau_opt", "bayesian_nested"):
        w = wilcoxon(ae[name], ae["B1_size_only"])   # a=model, b=size-only
        comparisons[f"{name}_vs_B1"] = w; raw_p.append((f"{name}_vs_B1", w["p"]))
    bh = benjamini_hochberg(raw_p)

    out = dict(
        pm_target=a.pm, n=n,
        descriptive=descriptive,
        size_effort_decoupling=decoupling,
        guessing_MAE_reference=round(guessing_marp0, 3),
        models=model_block,
        bayesian=dict(drivers_used=nonconst, drivers_dropped_collinear=dropped,
                      tau_sweep_SA={k: round(v, 4) for k, v in tau_sweep.items()},
                      chosen_tau_fulldata=best_t,
                      nested_tau_distribution={str(t): int(chosen.count(t)) for t in sorted(set(chosen))}),
        model_comparison_vs_size_only=dict(wilcoxon=comparisons, benjamini_hochberg=bh),
        protocol="LOOCV, Duan smearing; SA per Shepperd-MacDonell 2012; bootstrap B=%d; "
                 "effect size Δ vs guessing with randomisation p; nested-CV τ; "
                 "Wilcoxon signed-rank vs size-only baseline with BH correction." % a.boot,
        note="B1 size-only and B2 ATLM are the mandatory baselines (Whigham 2015). A COCOMO model "
             "earns its complexity only if it beats B1/B2 by a meaningful, significant margin.")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=2)

    print("=" * 70); print(f"  PAPER STATS  (target={a.pm}, n={n})"); print("=" * 70)
    print(f"  decoupling: corr(logSize,logPM)={decoupling['corr_logequiv_logpm']}  "
          f"productivity spread {decoupling['productivity_pm_per_ksloc']['spread_x']}x")
    for name, mm in model_block.items():
        print(f"  {name:>20}: SA {mm['SA']:+.3f} CI{mm['SA_95CI']}  PRED30 {mm['PRED30']*100:3.0f}%  "
              f"Δ {mm['effect_size_delta']}  p {mm['randomisation_p']}")
    print(f"  chosen τ (full-data) = {best_t};  nested τ dist = "
          f"{ {str(t): chosen.count(t) for t in sorted(set(chosen))} }")
    print(f"  vs size-only (BH q): " + ", ".join(f"{k}={v['q']}" for k, v in bh.items()))
    print(f"  wrote {a.out}")

if __name__ == "__main__":
    main()
