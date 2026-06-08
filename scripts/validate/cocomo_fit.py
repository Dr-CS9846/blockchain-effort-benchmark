#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cocomo_fit.py  —  synthesize COCOMO II variables, calibrate A (MLE), prove variable roles
==========================================================================================
Implements docs/method/cocomoII_mathematical_framework.md on the measured benchmark.
Keeps ALL COCOMO II variables (5 SF + 17 EM) + the 7 COCOBLOCK blockchain EMs; each is
synthesized from OBJECTIVE repo signals (Nominal when no signal). Published multiplier
magnitudes come from the verified cocomo2_tables.py (Manual). Then:
  - calibrate ln A by closed-form OLS = lognormal MLE (B fixed 0.91)
  - REDUNDANCY: pairwise corr + VIF of the log-multiplier columns (proves double-counting)
  - NECESSITY: per-variable ablation ΔSA under LOOCV
  - SUFFICIENCY: residual structure check
Inputs: measurements_census.csv + repo_attributes.csv. Outputs reports/cocomo_analysis.json
and data/calibration/cocomo_synth.csv. Headline target = PM_mid on the deduped
reliable+plausible set (sensitivity: pm_low/pm_high).
"""
import argparse, csv, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cocomo2_tables as T
try:
    import numpy as np
except ModuleNotFoundError:
    sys.exit("numpy required")

def _truthy(v): return str(v).strip() in ("1","True","true")
def _norm(u):   return (u or "").strip().lower().rstrip("/").replace(".git","")
def _i(a, k):   return 1 if str(a.get(k,"0")).strip() in ("1","True","true") else 0

# ── synthesis rules: objective signal -> COCOMO rating (Nominal default) ──────────────
def synth_ratings(m, a):
    """m = measurements row, a = attributes row. Returns (sf_ratings, em_ratings, bc_ems)."""
    ci, tests, docker, docs = _i(a,"has_ci"), _i(a,"has_tests"), _i(a,"has_docker"), _i(a,"has_docs")
    audit, lint = _i(a,"has_audit"), _i(a,"has_lintfmt")
    onchain, contracts = _i(a,"onchain_runtime"), _i(a,"has_contracts")
    consensus, xchain = _i(a,"dep_consensus"), _i(a,"dep_crosschain")
    zk, dcontract = _i(a,"dep_zkcrypto"), _i(a,"dep_contract")

    SF = {}
    # PREC: novel crypto/consensus => less precedented (Low); else Nominal
    SF["PREC"] = "L" if zk else "N"
    SF["FLEX"] = "N"                                   # milestone-driven grants
    SF["RESL"] = "H" if (docs and tests) else ("N" if (docs or tests) else "L")
    SF["TEAM"] = "N"                                   # avoid endogeneity with effort proxy
    pm_score = ci + tests + docker + lint
    SF["PMAT"] = "H" if pm_score >= 3 else ("N" if pm_score >= 1 else "L")

    EM = {}
    EM["RELY"] = "H" if audit else "N"
    EM["DATA"] = "N"
    EM["CPLX"] = "VH" if zk else ("H" if (consensus or onchain or contracts) else "N")
    EM["RUSE"] = "N"                                   # SDK/library not objectively detectable yet
    EM["DOCU"] = "H" if docs else "N"
    EM["TIME"] = "H" if contracts else "N"             # gas/exec constraint (smart contracts)
    EM["STOR"] = "N"
    EM["PVOL"] = "H" if (onchain or consensus) else "N"  # Substrate/SDK volatility
    for p in ("ACAP","PCAP","PCON","APEX","PLEX","LTEX"):
        EM[p] = "N"                                    # personnel skill unobservable from repo
    EM["TOOL"] = "H" if (ci and lint) else ("N" if (ci or lint) else "L")
    EM["SITE"] = "N"
    EM["SCED"] = "N"

    # COCOBLOCK blockchain EMs (multipliers; deliberately allowed to overlap standard EMs
    # so the redundancy test can PROVE collinearity rather than us deciding by hand).
    BC = {
        "BC_BEM":    1.0,
        "BC_DC":     1.10 if (consensus or onchain) else 1.0,
        "BC_EM_GAS": 1.05 if contracts else 1.0,
        "BC_EM_AUD": 1.20 if audit else 1.0,
        "BC_EM_MC":  1.20 if xchain else 1.0,
        "BC_EM_REG": 1.0,                              # no objective signal yet
        "BC_EM_NODE":1.10 if onchain else 1.0,
    }
    return SF, EM, BC

# ── load + join + dedup ──────────────────────────────────────────────────────────────
def load(meas_csv, attr_csv, pm_col, reliable_only=True, plausible_only=True, dedup=True):
    attrs = {r["project_id"]: r for r in csv.DictReader(open(attr_csv, encoding="utf-8"))}
    cand = []
    for m in csv.DictReader(open(meas_csv, encoding="utf-8")):
        if m.get("status") != "OK": continue
        if reliable_only and not _truthy(m.get("effort_reliable","1")): continue
        if plausible_only and not _truthy(m.get("duration_plausible","1")): continue
        a = attrs.get(m["project_id"])
        if a is None or a.get("status") != "OK": continue
        try:
            S = float(m["ksloc_code"]); pm = float(m[pm_col])
        except (ValueError, KeyError): continue
        if not (S > 0 and pm > 0): continue
        cand.append((m, a, S, pm))
    if dedup:
        best = {}
        for tup in cand:
            m = tup[0]; k = _norm(m.get("repo_url","")) or m["project_id"]
            key = (m.get("effort_until",""), tup[2])
            if k not in best or key > (best[k][0].get("effort_until",""), best[k][2]):
                best[k] = tup
        cand = list(best.values())
    return cand

# ── COCOMO prediction (without A) and column extraction ──────────────────────────────
EM_NAMES = list(T.EFFORT_MULTIPLIERS.keys())
def q_and_columns(cand):
    """Return y=ln PM, q=ln(predicted PM without A), and log-multiplier columns per variable."""
    y = []; q = []; cols = {v: [] for v in EM_NAMES}
    bc_names = ["BC_BEM","BC_DC","BC_EM_GAS","BC_EM_AUD","BC_EM_MC","BC_EM_REG","BC_EM_NODE"]
    for v in bc_names: cols[v] = []
    rows = []
    for (m, a, S, pm) in cand:
        SF, EM, BC = synth_ratings(m, a)
        E = T.exponent_E(SF)
        lnS = math.log(S)
        lq = E * lnS
        for v in EM_NAMES:
            mv = T.em_value(v, EM[v]); lv = math.log(mv); lq += lv; cols[v].append(lv)
        for v in bc_names:
            lv = math.log(BC[v]); lq += lv; cols[v].append(lv)
        y.append(math.log(pm)); q.append(lq)
        rows.append((m["project_id"], S, pm, E, SF, EM, BC))
    return np.array(y), np.array(q), cols, rows

# ── metrics ──────────────────────────────────────────────────────────────────────────
def sa_mmre_pred(actual, pred):
    actual = np.asarray(actual); pred = np.asarray(pred)
    mre = np.abs(actual - pred) / actual
    mae = np.mean(np.abs(actual - pred))
    n = len(actual); marp0 = np.mean([np.mean(np.abs(actual - actual[j])) for j in range(n)])
    return dict(MMRE=float(np.mean(mre)), MdMRE=float(np.median(mre)),
                PRED25=float(np.mean(mre <= 0.25)), PRED30=float(np.mean(mre <= 0.30)),
                MAE=float(mae), SA=float(1 - mae/marp0) if marp0 > 0 else None)

def calibrate_lnA(y, q):
    resid = y - q
    return float(np.mean(resid)), float(np.var(resid))   # MLE intercept, sigma^2

def loocv_metrics(y, q):
    n = len(y); preds = np.zeros(n)
    for i in range(n):
        idx = [j for j in range(n) if j != i]
        lnA = np.mean(y[idx] - q[idx]); smear = math.exp(np.var(y[idx]-q[idx])/2)
        preds[i] = math.exp(lnA + q[i]) * smear
    return sa_mmre_pred(np.exp(y), preds)

def vif(cols_matrix, names):
    X = np.array([cols_matrix[v] for v in names]).T   # n x k
    keep = [j for j in range(len(names)) if np.std(X[:,j]) > 1e-9]   # drop constant columns
    out = {}
    for jpos, j in enumerate(keep):
        others = [k for k in keep if k != j]
        if not others: out[names[j]] = 1.0; continue
        A = np.column_stack([np.ones(X.shape[0])] + [X[:,k] for k in others])
        coef, *_ = np.linalg.lstsq(A, X[:,j], rcond=None)
        r = X[:,j] - A @ coef
        ss_tot = np.sum((X[:,j]-X[:,j].mean())**2)
        R2 = 1 - np.sum(r**2)/ss_tot if ss_tot > 0 else 0
        out[names[j]] = float(1/(1-R2)) if R2 < 0.999999 else float("inf")
    const = [names[j] for j in range(len(names)) if j not in keep]
    return out, const

def main():
    ap = argparse.ArgumentParser()
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../06_measurement/scripts
    root = os.path.dirname(base)
    ap.add_argument("--meas", default=os.path.join(root, "data/calibration/measurements_census.csv"))
    ap.add_argument("--attr", default=os.path.join(root, "data/calibration/repo_attributes.csv"))
    ap.add_argument("--out",  default=os.path.join(root, "reports/cocomo_analysis.json"))
    ap.add_argument("--synth-out", default=os.path.join(root, "data/calibration/cocomo_synth.csv"))
    ap.add_argument("--pm", default="pm_mid", choices=["pm_mid","pm_low","pm_high"])
    a = ap.parse_args()

    cand = load(a.meas, a.attr, a.pm)
    n = len(cand)
    if n < 5: sys.exit(f"only {n} joined rows")
    y, q, cols, rows = q_and_columns(cand)

    lnA, sig2 = calibrate_lnA(y, q)
    A = math.exp(lnA); smear = math.exp(sig2/2)
    pred_in = np.exp(lnA + q) * smear
    insample = sa_mmre_pred(np.exp(y), pred_in)
    cv = loocv_metrics(y, q)

    all_mult = EM_NAMES + ["BC_BEM","BC_DC","BC_EM_GAS","BC_EM_AUD","BC_EM_MC","BC_EM_REG","BC_EM_NODE"]
    vifs, constants = vif(cols, all_mult)
    # pairwise correlation among non-constant multiplier columns
    nonconst = [v for v in all_mult if np.std(cols[v]) > 1e-9]
    corr_pairs = []
    for i in range(len(nonconst)):
        for j in range(i+1, len(nonconst)):
            u, w = np.array(cols[nonconst[i]]), np.array(cols[nonconst[j]])
            c = float(np.corrcoef(u, w)[0,1])
            if abs(c) >= 0.6: corr_pairs.append([nonconst[i], nonconst[j], round(c,3)])

    # NECESSITY: ablation — set each non-constant variable Nominal (ln=0), recompute LOOCV SA
    base_sa = cv["SA"]; abl = {}
    for v in nonconst:
        q2 = q - np.array(cols[v])                      # remove this variable's contribution
        abl[v] = round(base_sa - (loocv_metrics(y, q2)["SA"] or 0), 4)

    # SUFFICIENCY: residual structure vs fitted
    resid = y - (lnA + q)
    out = dict(
        pm_target=a.pm, n=n, A=round(A,4), B=T.B, sigma_logspace=round(math.sqrt(sig2),4),
        nominal_constant_variables=constants,
        in_sample=insample, loocv=cv,
        redundancy=dict(high_corr_pairs=corr_pairs,
                        VIF=dict(sorted(((k, round(v,2) if v!=float('inf') else 1e9)
                                         for k,v in vifs.items()), key=lambda kv:-kv[1]))),
        necessity_ablation_dSA=dict(sorted(abl.items(), key=lambda kv:-kv[1])),
        residual=dict(corr_resid_vs_fitted=float(np.corrcoef(resid, (lnA+q))[0,1]),
                      resid_std=float(np.std(resid))),
        note="Verdicts: VIF>>5 or |corr|->1 => redundant; dSA<=0 => inert (keep Nominal); "
             "residual structure => insufficient. Magnitudes from verified COCOMO II.2000 tables.")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out,"w"), indent=2)

    # per-repo synthesized dataset
    with open(a.synth_out, "w", newline="", encoding="utf-8") as f:
        cols_hdr = ["project_id","ksloc","pm_actual","E"] + [f"SF_{s}" for s in T.SCALE_FACTORS] \
                   + EM_NAMES + ["BC_BEM","BC_DC","BC_EM_GAS","BC_EM_AUD","BC_EM_MC","BC_EM_REG","BC_EM_NODE"] \
                   + ["pm_pred"]
        w = csv.writer(f); w.writerow(cols_hdr)
        for i,(pid,S,pm,E,SF,EM,BC) in enumerate(rows):
            w.writerow([pid, round(S,3), round(pm,4), round(E,4)]
                       + [SF[s] for s in T.SCALE_FACTORS]
                       + [EM[e] for e in EM_NAMES]
                       + [BC[b] for b in ("BC_BEM","BC_DC","BC_EM_GAS","BC_EM_AUD","BC_EM_MC","BC_EM_REG","BC_EM_NODE")]
                       + [round(float(pred_in[i]),3)])

    print("="*64); print(f"  BLOCKCHAIN COCOMO II  (target={a.pm}, n={n})"); print("="*64)
    print(f"  A={A:.3f}  B={T.B}  sigma={math.sqrt(sig2):.3f}")
    print(f"  In-sample: MMRE {insample['MMRE']*100:.0f}% PRED25 {insample['PRED25']*100:.0f}% SA {insample['SA']:.2f}")
    print(f"  LOOCV    : MMRE {cv['MMRE']*100:.0f}% PRED25 {cv['PRED25']*100:.0f}% SA {cv['SA']:.2f}")
    print(f"  redundant (|corr|>=0.6) pairs: {corr_pairs}")
    print(f"  necessity ΔSA (top): {list(out['necessity_ablation_dSA'].items())[:6]}")
    print(f"  Wrote {a.out} and {a.synth_out}")

if __name__ == "__main__":
    main()
