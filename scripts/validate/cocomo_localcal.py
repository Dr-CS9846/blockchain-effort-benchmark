#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cocomo_localcal.py  —  LOCAL CALIBRATION toward PM = PM (fitted coefficients)
============================================================================
The fixed-weight COCOMO run (cocomo_fit.py) showed that applying Boehm's PUBLISHED
multiplier magnitudes + Duan smearing massively over-predicts mined PM (LOOCV SA < 0).
That is a calibration artefact, NOT proof that size is uninformative: fitting the
coefficients locally, ln(size) alone already yields LOOCV SA ~ +0.45.

This is the COCOMO II "local calibration" route (Boehm 2000, ch.4): instead of fixing
the exponent and EM magnitudes, we FIT them to the local data by OLS in log space —
  ln PM = b0 + b1*ln(KSLOC) + Σ b_k * driver_k  + ε
and search (greedy forward selection, LOOCV-validated) for the SMALLEST set of
PROSPECTIVELY-knowable drivers that maximises predictive accuracy. The chosen set +
fitted coefficients ARE the blockchain-aware effort model a firm applies pre-project.

Guards against fake PM=PM: every model is scored by LEAVE-ONE-OUT CV (SA, PRED25, MMRE),
not in-sample R²; forward selection stops when LOOCV SA stops improving; variable count
is capped to protect the n~63 sample.

Inputs: measurements_census.csv + repo_attributes.csv. Output: reports/cocomo_localcal_{pm}.json
"""
import argparse, csv, json, math, os, sys
import numpy as np

def _norm(u): return (u or "").strip().lower().rstrip("/").replace(".git","")
def _f(r,k):
    try: return float(r[k])
    except: return None
def _i(r,k): return 1.0 if str(r.get(k,"0")).strip() in ("1","True","true") else 0.0

PRIMARY_LANGS = ["rust","typescript","javascript","go","python","solidity","c++","java"]
def primary_lang(top_langs):
    try:
        d = json.loads(top_langs) if top_langs and top_langs.strip().startswith("{") else {}
    except Exception:
        d = {}
    if not d: return "other"
    lang = max(d, key=lambda k: d[k]).lower()
    return lang if lang in PRIMARY_LANGS else "other"

def load(meas_csv, attr_csv, pm_col, max_loc_per_active_day=0.0):
    """max_loc_per_active_day>0 applies an EFFORT-QUALITY gate: drop repos whose delivered
    LOC per active developer-day exceeds the threshold (history-artifact effort observations:
    imported/generated code or squashed history — implausible authoring velocity). Grounded
    in software-productivity literature (delivered code accrues at tens, not hundreds, of LOC/day)."""
    attrs = {r["project_id"]: r for r in csv.DictReader(open(attr_csv, encoding="utf-8"))}
    cand = []; excluded = []
    for m in csv.DictReader(open(meas_csv, encoding="utf-8")):
        if m.get("status")!="OK" or m.get("effort_reliable")!="1" or m.get("duration_plausible")!="1":
            continue
        a = attrs.get(m["project_id"])
        if not a or a.get("status")!="OK": continue
        pm=_f(m,pm_col); s=_f(m,"ksloc_code")
        if not (pm and pm>0 and s and s>0): continue
        if max_loc_per_active_day>0:
            ad=_f(m,"active_dev_days") or 0
            lpd = s*1000/ad if ad>0 else float("inf")
            if lpd > max_loc_per_active_day:
                excluded.append((m["project_id"], round(lpd,0))); continue
        cand.append((m,a,s,pm))
    # dedup by repo (latest delivered)
    best={}
    for t in cand:
        m=t[0]; k=_norm(m.get("repo_url","")) or m["project_id"]
        key=(m.get("effort_until",""), t[2])
        if k not in best or key>(best[k][0].get("effort_until",""), best[k][2]):
            best[k]=t
    load.excluded = excluded
    return list(best.values())

def build_features(cand):
    """Return y (ln pm), feature dict name->vector, and a 'prospective' flag per feature."""
    n=len(cand); y=np.array([math.log(t[3]) for t in cand])
    feats={}; prosp={}
    feats["ln_ksloc"]=np.array([math.log(t[2]) for t in cand]);                       prosp["ln_ksloc"]=True
    feats["ln_ksloc_all"]=np.array([math.log(max(_f(t[0],"ksloc_all") or t[2],1e-6)) for t in cand]); prosp["ln_ksloc_all"]=True
    # CANONICAL COCOMO II size: reuse-adjusted equivalent SLOC (gap #9). Added only when present
    # for every row (else degenerate); competes with ln_ksloc in selection.
    if all((_f(t[0],"equivalent_sloc") or 0) > 0 for t in cand):
        feats["ln_equiv_sloc"]=np.array([math.log(_f(t[0],"equivalent_sloc")) for t in cand]); prosp["ln_equiv_sloc"]=True
    # blockchain / engineering driver dummies from attributes (all pre-project knowable)
    for k in ["onchain_runtime","has_contracts","has_audit","has_ci","has_tests","has_docs",
              "has_docker","has_lintfmt","dep_consensus","dep_crosschain","dep_zkcrypto",
              "dep_contract","dep_frontend"]:
        v=np.array([_i(t[1],k) for t in cand])
        if 0<v.sum()<n: feats[k]=v; prosp[k]=True       # skip constant columns
    # primary-language one-hot (project archetype proxy)
    langs=[primary_lang(t[0].get("top_langs","")) for t in cand]
    for L in set(langs):
        v=np.array([1.0 if x==L else 0.0 for x in langs])
        if 0<v.sum()<n and L!="other": feats[f"lang_{L}"]=v; prosp[f"lang_{L}"]=True
    # FUNCTIONAL SIZE: blockchain feature-unit counts (prospective: estimable from a design spec).
    # ln(1+count) per family, plus a composite "callable surface" volume measure.
    FS=["n_pallets","n_extrinsics","n_storage","n_events","n_ink_msgs","n_sol_funcs",
        "n_contracts_def","n_rpc"]
    fs_present = any(k in (cand[0][1] or {}) for k in FS)
    if fs_present:
        def fscol(k): return np.array([math.log1p(max(_f(t[1],k) or 0,0)) for t in cand])
        for k in FS:
            v=fscol(k)
            if v.std()>1e-9: feats[f"ln_{k}"]=v; prosp[f"ln_{k}"]=True
        # composite functional size = total callable/feature surface
        comp=np.array([math.log1p(sum(max(_f(t[1],k) or 0,0) for k in
                       ["n_extrinsics","n_ink_msgs","n_sol_funcs","n_storage","n_events"])) for t in cand])
        if comp.std()>1e-9: feats["ln_feature_units"]=comp; prosp["ln_feature_units"]=True
    # team size: arguably a PLANNING input, flagged separately
    feats["ln_authors"]=np.array([math.log(max(_f(t[0],"distinct_authors") or 1,1)) for t in cand]); prosp["ln_authors"]="team"
    return y, feats, prosp

def loocv(y, X):
    n=len(y); Xi=np.column_stack([np.ones(n),X]) if X.size else np.ones((n,1))
    preds=np.zeros(n)
    for i in range(n):
        m=[j for j in range(n) if j!=i]
        beta,*_=np.linalg.lstsq(Xi[m],y[m],rcond=None)
        res_tr=y[m]-Xi[m]@beta; sm=math.exp(np.var(res_tr)/2)
        preds[i]=math.exp(Xi[i]@beta)*sm
    pm=np.exp(y); mre=np.abs(pm-preds)/pm; mae=np.mean(np.abs(pm-preds))
    marp0=np.mean([np.mean(np.abs(pm-pm[j])) for j in range(n)])
    beta_full,*_=np.linalg.lstsq(Xi,y,rcond=None)
    res=y-Xi@beta_full; r2=1-np.sum(res**2)/np.sum((y-y.mean())**2)
    return dict(SA=float(1-mae/marp0), PRED25=float(np.mean(mre<=.25)),
                PRED30=float(np.mean(mre<=.30)), MMRE=float(np.mean(mre)),
                MdMRE=float(np.median(mre)), R2_insample=float(r2))

def fit_coeffs(y, feats, names):
    n=len(y); X=np.column_stack([feats[k] for k in names]) if names else np.empty((n,0))
    Xi=np.column_stack([np.ones(n),X]); beta,*_=np.linalg.lstsq(Xi,y,rcond=None)
    return dict(zip(["intercept"]+list(names), [float(b) for b in beta]))

def forward_select(y, feats, allowed, cap=8, min_gain=0.005):
    chosen=[]; remaining=list(allowed); n=len(y)
    base=loocv(y, np.empty((n,0)))["SA"]; trail=[("<<baseline:mean>>", base)]
    while remaining and len(chosen)<cap:
        scored=[]
        for c in remaining:
            X=np.column_stack([feats[k] for k in chosen+[c]])
            scored.append((loocv(y,X)["SA"], c))
        scored.sort(reverse=True)
        best_sa, best_c = scored[0]
        if best_sa - base > min_gain:
            chosen.append(best_c); remaining.remove(best_c); base=best_sa
            trail.append((best_c, best_sa))
        else:
            break
    return chosen, trail

def archetype_of(a):
    oc=_i(a,"onchain_runtime"); npal=_f(a,"n_pallets") or 0; nex=_f(a,"n_extrinsics") or 0
    nsol=_f(a,"n_sol_funcs") or 0; nink=_f(a,"n_ink_msgs") or 0; ncon=_f(a,"n_contracts_def") or 0
    hc=_i(a,"has_contracts"); fr=_i(a,"dep_frontend")
    if oc or npal>0 or nex>0:               return "onchain_pallet"
    if hc or nsol>0 or nink>0 or ncon>0:    return "smart_contract"
    if fr:                                  return "offchain_app"
    return "library_tool"

def loocv_preds(y, X):
    n=len(y); Xi=np.column_stack([np.ones(n),X]) if X.size else np.ones((n,1)); preds=np.zeros(n)
    for i in range(n):
        m=[j for j in range(n) if j!=i]; b,*_=np.linalg.lstsq(Xi[m],y[m],rcond=None)
        r=y[m]-Xi[m]@b; preds[i]=math.exp(Xi[i]@b)*math.exp(np.var(r)/2)
    return preds

def coarse_of(a):
    return "onchain" if archetype_of(a) in ("onchain_pallet","smart_contract") else "offchain"

def stratified(y, feats, prosp, cand, label, keyfn=archetype_of, cap=3, with_preds=False, ids=None):
    """Per-archetype local calibration. keyfn=archetype_of (4-way) or coarse_of (2-way)."""
    arche=[keyfn(t[1]) for t in cand]
    cands=[k for k in feats if prosp[k] is True]
    groups={}
    for g in sorted(set(arche)):
        idx=[i for i,x in enumerate(arche) if x==g]; m=len(idx)
        if m<8:
            groups[g]=dict(n=m, note="too few for LOOCV"); continue
        yi=y[idx]; sub={k: feats[k][idx] for k in feats}
        allowed=[k for k in cands if sub[k].std()>1e-9]
        sel,trail=forward_select(yi, sub, allowed, cap=cap)
        X=np.column_stack([sub[k] for k in sel]) if sel else np.empty((m,0))
        rec=dict(n=m, selected=sel, trail=[(c,round(s,3)) for c,s in trail],
                 metrics=loocv(yi, X), coeffs=fit_coeffs(yi,sub,sel))
        # parsimony reference: size-only model, to separate stratification+size from incidental flags
        size_key="ln_ksloc" if sub.get("ln_ksloc") is not None and sub["ln_ksloc"].std()>1e-9 else None
        if size_key: rec["size_only_metrics"]=loocv(yi, sub[size_key].reshape(-1,1))
        if with_preds:
            preds=loocv_preds(yi, X)
            rec["loocv_pred_vs_actual"]=[[ (ids[idx[k]] if ids else idx[k]),
                                           round(float(preds[k]),2), round(float(math.exp(yi[k])),2),
                                           round(float(abs(preds[k]-math.exp(yi[k]))/math.exp(yi[k])),2)]
                                         for k in range(m)]
        groups[g]=rec
    return dict(group_counts={g:arche.count(g) for g in sorted(set(arche))}, groups=groups)

def run(y, feats, prosp, label, cand):
    n=len(y)
    prospective=[k for k in feats if prosp[k] is True]
    with_team=prospective+["ln_authors"]
    # single-variable LOOCV SA (univariate screen)
    uni={k: round(loocv(y, feats[k].reshape(-1,1))["SA"],3) for k in feats}
    # models
    out={}
    sel_p, trail_p = forward_select(y, feats, prospective)
    out["prospective_only"]=dict(selected=sel_p, trail=[(c,round(s,3)) for c,s in trail_p],
                                 metrics=loocv(y, np.column_stack([feats[k] for k in sel_p]) if sel_p else np.empty((n,0))),
                                 coeffs=fit_coeffs(y,feats,sel_p))
    sel_t, trail_t = forward_select(y, feats, with_team)
    out["with_team_size"]=dict(selected=sel_t, trail=[(c,round(s,3)) for c,s in trail_t],
                               metrics=loocv(y, np.column_stack([feats[k] for k in sel_t]) if sel_t else np.empty((n,0))),
                               coeffs=fit_coeffs(y,feats,sel_t))
    out["full_prospective"]=dict(selected=prospective,
                                 metrics=loocv(y, np.column_stack([feats[k] for k in prospective])))
    ids=[t[0].get("project_id","") for t in cand]
    out["by_archetype"]=stratified(y, feats, prosp, cand, label, keyfn=archetype_of, cap=3,
                                   with_preds=True, ids=ids)
    out["by_archetype_2group"]=stratified(y, feats, prosp, cand, label, keyfn=coarse_of,
                                          cap=4, with_preds=True, ids=ids)
    out["univariate_LOOCV_SA"]=dict(sorted(uni.items(), key=lambda kv:-kv[1]))
    out["n"]=n; out["pm_target"]=label
    return out

def main():
    ap=argparse.ArgumentParser()
    root=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--meas", default=os.path.join(root,"data/calibration/measurements_census.csv"))
    ap.add_argument("--attr", default=os.path.join(root,"data/calibration/repo_attributes.csv"))
    ap.add_argument("--out",  default=os.path.join(root,"reports/cocomo_localcal.json"))
    ap.add_argument("--pm", default="pm_mid", choices=["pm_mid","pm_low","pm_high"])
    ap.add_argument("--maxlocday", type=float, default=0.0,
                    help="effort-quality gate: drop repos with delivered LOC/active-day above this")
    a=ap.parse_args()
    cand=load(a.meas,a.attr,a.pm,max_loc_per_active_day=a.maxlocday)
    if len(cand)<10: sys.exit(f"only {len(cand)} joined rows")
    y,feats,prosp=build_features(cand)
    res=run(y,feats,prosp,a.pm,cand)
    res["effort_quality_gate"]=dict(max_loc_per_active_day=a.maxlocday,
                                    excluded=getattr(load,"excluded",[]))
    os.makedirs(os.path.dirname(a.out),exist_ok=True); json.dump(res,open(a.out,"w"),indent=2)
    p=res["prospective_only"]; t=res["with_team_size"]
    print("="*70); print(f"  LOCAL CALIBRATION  (target={a.pm}, n={res['n']})"); print("="*70)
    print(f"  prospective-only set: {p['selected']}")
    print(f"    LOOCV SA={p['metrics']['SA']:+.2f} PRED25={p['metrics']['PRED25']*100:.0f}% "
          f"PRED30={p['metrics']['PRED30']*100:.0f}% MMRE={p['metrics']['MMRE']*100:.0f}%")
    print(f"  +team-size set: {t['selected']}")
    print(f"    LOOCV SA={t['metrics']['SA']:+.2f} PRED25={t['metrics']['PRED25']*100:.0f}% "
          f"PRED30={t['metrics']['PRED30']*100:.0f}% MMRE={t['metrics']['MMRE']*100:.0f}%")
    print(f"  Wrote {a.out}")

if __name__=="__main__":
    main()
