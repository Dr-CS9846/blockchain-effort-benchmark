#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
target_compare.py  —  which EFFORT TARGET is most predictable? (don't fight the noise floor)
=============================================================================================
Four predictor strategies all hit the same SA~0.64 / PRED30~44% ceiling against git PM. That
ceiling is set by the TARGET's noise, not the model. So instead of changing the model, we test
which target a developer can actually predict from size:

  targets (each on the subset of projects where it is present & >0):
    git_pm     = pm_mid                              (mined; what we used; noisy)
    planned_pm = planned_FTE x planned_duration      (HUMAN-STATED effort estimate, from the app)
    cost_pm    = cost_usd / (rate* x 152)            (PAID labour; rate* ~ $26/h)

For each target, fit the SAME models (LOOCV, Duan smearing, log space) and report accuracy:
    size_equiv : lnT ~ a + b*ln(equivalent SLOC)
    size_ksloc : lnT ~ a + b*ln(KSLOC)
    fs_total   : lnT ~ a + b*ln(1+ functional units)
    equiv+fs   : lnT ~ a + b*ln(equiv) + c*ln(1+units)

Headline question: is PRED(30) for size_equiv HIGHER against planned_pm (a human-reported target)
than against git_pm? If yes, the human-stated effort is the better foundation - and predicting it
is itself a usable deliverable (a grant applicant wants the planned FTE x duration).

Self-contained (numpy + csv). Reads measurements_census.csv + repo_attributes.csv.
Output: reports/target_compare.json
"""
import argparse, csv, json, math, os, sys
import numpy as np

RATE = 26.0; PH_PER_PM = 152.0
ONCHAIN = ["n_pallets","n_extrinsics","n_storage","n_events","n_ink_msgs","n_sol_funcs","n_contracts_def","n_rpc"]
OFFCHAIN = ["n_exports","n_funcs","n_classes","n_routes"]

def _f(r, k):
    try: return float(r[k])
    except (ValueError, KeyError, TypeError): return None
def _i(r, k):
    try: return max(int(float(r.get(k,0) or 0)),0)
    except (ValueError, TypeError): return 0
def _norm(u): return (u or "").strip().lower().rstrip("/").replace(".git","")

def loocv_ols(y, X):
    n=len(y); Xi=np.column_stack([np.ones(n),X]); preds=np.zeros(n)
    for i in range(n):
        idx=[j for j in range(n) if j!=i]
        b,*_=np.linalg.lstsq(Xi[idx],y[idx],rcond=None)
        r=y[idx]-Xi[idx]@b; preds[i]=math.exp(Xi[i]@b)*math.exp(np.var(r)/2)
    return preds

def metrics(actual,pred):
    actual=np.asarray(actual);pred=np.asarray(pred);mre=np.abs(actual-pred)/actual
    mae=np.mean(np.abs(actual-pred));n=len(actual)
    marp0=np.mean(np.abs(actual[:,None]-actual[None,:]))
    return dict(SA=round(float(1-mae/marp0),4) if marp0>0 else None,
                MMRE=round(float(np.mean(mre)),4),MdMRE=round(float(np.median(mre)),4),
                PRED25=round(float(np.mean(mre<=.25)),4),PRED30=round(float(np.mean(mre<=.30)),4))

def main():
    ap=argparse.ArgumentParser()
    root=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--meas",default=os.path.join(root,"data/calibration/measurements_census.csv"))
    ap.add_argument("--attr",default=os.path.join(root,"data/calibration/repo_attributes.csv"))
    ap.add_argument("--out", default=os.path.join(root,"reports/target_compare.json"))
    a=ap.parse_args()

    attrs={r["project_id"]:r for r in csv.DictReader(open(a.attr,encoding="utf-8"))}
    rows=[r for r in csv.DictReader(open(a.meas,encoding="utf-8")) if r.get("status")=="OK"]
    # dedup by repo (latest delivery)
    best={}
    for r in rows:
        k=_norm(r.get("repo_url","")) or r["project_id"]
        key=(r.get("effort_until",""), _f(r,"ksloc_code") or 0)
        if k not in best or key>(best[k].get("effort_until",""), _f(best[k],"ksloc_code") or 0):
            best[k]=r
    R=list(best.values())

    def target_val(r,name):
        if name=="git_pm":     return _f(r,"pm_mid")
        if name=="planned_pm": return _f(r,"planned_pm")
        if name=="cost_pm":
            c=_f(r,"cost_usd");  return (c/(RATE*PH_PER_PM)) if (c and c>0) else None
        return None

    out={"rate_usd_per_hour":RATE,"models_per_target":{}}
    for tname in ("git_pm","planned_pm","cost_pm"):
        cand=[]
        for r in R:
            t=target_val(r,tname)
            ks=_f(r,"ksloc_code"); eq=_f(r,"equivalent_sloc") or ks
            a_=attrs.get(r["project_id"])
            if not (t and t>0 and ks and ks>0 and eq and eq>0 and a_): continue
            units=sum(_i(a_,k) for k in ONCHAIN+OFFCHAIN)
            cand.append((math.log(t),math.log(eq),math.log(ks),math.log1p(units)))
        n=len(cand)
        if n<12:
            out["models_per_target"][tname]={"n":n,"note":"too few"}; continue
        y=np.array([c[0] for c in cand]); actual=np.exp(y)
        lnE=np.array([c[1] for c in cand]); lnK=np.array([c[2] for c in cand]); ln1t=np.array([c[3] for c in cand])
        res={"n":n}
        res["size_equiv"]=metrics(actual,loocv_ols(y,lnE.reshape(-1,1)))
        res["size_ksloc"]=metrics(actual,loocv_ols(y,lnK.reshape(-1,1)))
        res["fs_total"]=metrics(actual,loocv_ols(y,ln1t.reshape(-1,1)))
        res["equiv_plus_fs"]=metrics(actual,loocv_ols(y,np.column_stack([lnE,ln1t])))
        out["models_per_target"][tname]=res

    os.makedirs(os.path.dirname(a.out),exist_ok=True)
    json.dump(out,open(a.out,"w"),indent=2)
    print("="*74); print("  TARGET PREDICTABILITY (which effort target can size predict best?)"); print("="*74)
    for t,res in out["models_per_target"].items():
        if "size_equiv" not in res: print(f"  {t}: n={res.get('n')} {res.get('note','')}"); continue
        m=res["size_equiv"]
        print(f"  {t:>11} (n={res['n']:>3}): size_equiv SA {m['SA']:+.3f}  PRED25 {m['PRED25']*100:3.0f}%  "
              f"PRED30 {m['PRED30']*100:3.0f}%  MMRE {m['MMRE']*100:3.0f}%")
    print(f"  wrote {a.out}")

if __name__=="__main__":
    main()
