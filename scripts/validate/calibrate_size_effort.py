#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
calibrate_size_effort.py  —  Step 3: the genuine COCOMO size->effort core
=========================================================================
Fits the constructive model
 
        PM = A * KSLOC^E * smear              (log-linear MLE, Duan smearing)
 
on the MEASURED data produced by measure_repos.py, where:
  * KSLOC   = measured code size (independent variable)  -- the COCOMO driver
  * PM      = effort, taken as measured active person-months (preferred) OR
              planned FTE x duration (reference), selectable via --effort.
 
It also reports corr(planned_pm, measured_pm): if these agree, the planned
effort target is validated and the planned-vs-actual concern is retired.
 
Deterministic: closed-form OLS in log space = MLE under lognormal errors.
Reports in-sample and leave-one-out (LOOCV) MMRE / PRED(25) and the Conte (1986)
verdict. Writes size_effort_params.json and size_effort_results.json.
 
USAGE
  python calibrate_size_effort.py --effort measured     # PM = active person-months
  python calibrate_size_effort.py --effort planned      # PM = FTE x duration (reference)
  python calibrate_size_effort.py --size ksloc_code     # or ksloc_all
"""
import argparse, csv, json, math, os, sys
try:
    import numpy as np
except ModuleNotFoundError:
    sys.exit("numpy is required. Install it with:  pip install numpy")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metrics as metricslib
 
def load(path, size_col, effort_mode, reliable_only=False):
    X=[]; y=[]; planned=[]; names=[]; raw=[]
    for r in csv.DictReader(open(path)):
        if r.get("status")!="OK": continue
        # sensitivity switch: headline fit uses only repos with a trustworthy
        # git-effort signal (>=2 authors, >=10 commits); full set kept for the
        # sensitivity table. Rows lacking the column (older runs) are treated as
        # reliable so the filter is backward-compatible.
        if reliable_only and str(r.get("effort_reliable","1")).strip() not in ("1","True","true"):
            continue
        try:
            size=float(r[size_col]);
            ppm=float(r["planned_pm"]) if r["planned_pm"] else float("nan")
            mpm=float(r["active_person_months"]) if r["active_person_months"] else float("nan")
        except (ValueError,KeyError): continue
        eff = mpm if effort_mode=="measured" else ppm
        if not (size>0 and eff>0): continue
        X.append(size); y.append(eff); planned.append(ppm); names.append(r["project_name"]); raw.append(r)
    return np.array(X), np.array(y), np.array(planned), names
 
def fit(lnX, lny):
    A=np.column_stack([np.ones_like(lnX), lnX])
    coef,*_=np.linalg.lstsq(A,lny,rcond=None)
    resid=lny-A@coef
    smear=float(np.mean(np.exp(resid)))
    return coef, smear, resid
 
# full metric suite (MMRE, MdMRE, PRED, MAE, SA vs random baseline) lives in metrics.py
 
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--csv", default="measurements.csv")
    ap.add_argument("--size", default="ksloc_code", choices=["ksloc_code","ksloc_all"])
    ap.add_argument("--effort", default="measured", choices=["measured","planned"])
    ap.add_argument("--reliable-only", action="store_true",
                    help="fit only on repos with a trustworthy git-effort signal (>=2 authors, >=10 commits)")
    a=ap.parse_args()
    if not os.path.exists(a.csv): sys.exit(f"{a.csv} not found - run measure_repos.py first.")

    size,eff,planned,names=load(a.csv,a.size,a.effort,a.reliable_only)
    n=len(size)
    if n<4: sys.exit(f"Only {n} usable rows. Resolve more repos in the manifest, then re-run.")
    lnX=np.log(size); lny=np.log(eff)
 
    coef,smear,resid=fit(lnX,lny)
    A=math.exp(coef[0]); E=coef[1]
    dof=max(n-2,1); sigma=float(math.sqrt(float(resid@resid)/dof))
    pred_in=np.exp(coef[0]+coef[1]*lnX)*smear
    ins=metricslib.summary(eff,pred_in)
 
    # LOOCV
    preds=np.zeros(n)
    for i in range(n):
        idx=[j for j in range(n) if j!=i]
        c,sm,_=fit(lnX[idx],lny[idx])
        preds[i]=math.exp(c[0]+c[1]*lnX[i])*sm
    cv=metricslib.summary(eff,preds)
 
    # planned vs measured cross-check (only meaningful when effort=measured)
    cross=None
    mask=np.isfinite(planned)&(planned>0)
    if a.effort=="measured" and mask.sum()>=3:
        r=float(np.corrcoef(np.log(eff[mask]),np.log(planned[mask]))[0,1])
        ratio=float(np.median(eff[mask]/planned[mask]))
        cross=dict(corr_log=r, median_measured_over_planned=ratio, n=int(mask.sum()))
 
    # headline driver-signal: correlation of log size with log effort
    size_effort_corr_log=float(np.corrcoef(lnX,lny)[0,1]) if n>=3 else float("nan")

    params=dict(model="PM = A * KSLOC^E * Duan", size_metric=a.size, effort=a.effort,
                reliable_only=bool(a.reliable_only),
                n=n, A=A, E=E, sigma_logspace=sigma, duan_smearing=smear,
                estimator="closed-form OLS log space = lognormal MLE (deterministic)")
    results=dict(conte_1986={"MMRE<":0.25,"PRED25>=":0.75},
                 reliable_only=bool(a.reliable_only),
                 size_effort_corr_log=size_effort_corr_log,
                 in_sample=ins, loocv=cv,
                 loocv_conte_pass=bool(cv["MMRE"]<0.25 and cv["PRED25"]>=0.75),
                 planned_vs_measured=cross,
                 projects=names, size=[float(x) for x in size],
                 effort_actual=[float(x) for x in eff],
                 loocv_pred=[float(x) for x in preds])
    json.dump(params,open("size_effort_params.json","w"),indent=2)
    json.dump(results,open("size_effort_results.json","w"),indent=2)
 
    print("="*60)
    print("  COCOMO SIZE -> EFFORT CORE  (measured, reproducible)")
    print("="*60)
    print(f"  n={n} | size={a.size} | effort={a.effort} | reliable_only={a.reliable_only}")
    print(f"  A={A:.4f}  E={E:.4f}  sigma={sigma:.4f}  Duan={smear:.4f}  corr(logKSLOC,logPM)={size_effort_corr_log:+.3f}")
    print(f"  In-sample : MMRE {ins['MMRE']*100:5.1f}%  PRED25 {ins['PRED25']*100:5.1f}%  MAE {ins['MAE']:.2f}  SA {ins['SA_vs_random']*100:5.1f}%")
    print(f"  LOOCV     : MMRE {cv['MMRE']*100:5.1f}%  PRED25 {cv['PRED25']*100:5.1f}%  PRED30 {cv['PRED30']*100:5.1f}%  MAE {cv['MAE']:.2f}  SA {cv['SA_vs_random']*100:5.1f}%")
    print(f"  Conte(1986) LOOCV verdict: {'PASS' if results['loocv_conte_pass'] else 'FAIL'}   (SA>0 = better than random guessing)")
    if cross: print(f"  planned vs measured PM: r(log)={cross['corr_log']:+.3f}  median ratio={cross['median_measured_over_planned']:.2f} (n={cross['n']})")
    print("-"*60)
    print("  project                         size   PM_act  PM_loocv")
    for nm,s,e,p in zip(names,size,eff,preds):
        print(f"  {nm[:28]:28} {s:7.2f} {e:7.2f} {p:8.2f}")
    print("="*60)
    print("  Wrote size_effort_params.json and size_effort_results.json")
 
if __name__=="__main__": main()