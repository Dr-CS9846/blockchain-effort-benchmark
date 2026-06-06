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
 
def load(path, size_col, effort_mode):
    X=[]; y=[]; planned=[]; names=[]; raw=[]
    for r in csv.DictReader(open(path)):
        if r.get("status")!="OK": continue
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
 
def metrics(actual,pred):
    mre=np.abs(actual-pred)/actual
    return dict(MMRE=float(mre.mean()), MdMRE=float(np.median(mre)),
                PRED25=float(np.mean(mre<=0.25)), PRED30=float(np.mean(mre<=0.30)))
 
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--csv", default="measurements.csv")
    ap.add_argument("--size", default="ksloc_code", choices=["ksloc_code","ksloc_all"])
    ap.add_argument("--effort", default="measured", choices=["measured","planned"])
    a=ap.parse_args()
    if not os.path.exists(a.csv): sys.exit(f"{a.csv} not found - run measure_repos.py first.")
 
    size,eff,planned,names=load(a.csv,a.size,a.effort)
    n=len(size)
    if n<4: sys.exit(f"Only {n} usable rows. Resolve more repos in the manifest, then re-run.")
    lnX=np.log(size); lny=np.log(eff)
 
    coef,smear,resid=fit(lnX,lny)
    A=math.exp(coef[0]); E=coef[1]
    dof=max(n-2,1); sigma=float(math.sqrt(float(resid@resid)/dof))
    pred_in=np.exp(coef[0]+coef[1]*lnX)*smear
    ins=metrics(eff,pred_in)
 
    # LOOCV
    preds=np.zeros(n)
    for i in range(n):
        idx=[j for j in range(n) if j!=i]
        c,sm,_=fit(lnX[idx],lny[idx])
        preds[i]=math.exp(c[0]+c[1]*lnX[i])*sm
    cv=metrics(eff,preds)
 
    # planned vs measured cross-check (only meaningful when effort=measured)
    cross=None
    mask=np.isfinite(planned)&(planned>0)
    if a.effort=="measured" and mask.sum()>=3:
        r=float(np.corrcoef(np.log(eff[mask]),np.log(planned[mask]))[0,1])
        ratio=float(np.median(eff[mask]/planned[mask]))
        cross=dict(corr_log=r, median_measured_over_planned=ratio, n=int(mask.sum()))
 
    params=dict(model="PM = A * KSLOC^E * Duan", size_metric=a.size, effort=a.effort,
                n=n, A=A, E=E, sigma_logspace=sigma, duan_smearing=smear,
                estimator="closed-form OLS log space = lognormal MLE (deterministic)")
    results=dict(conte_1986={"MMRE<":0.25,"PRED25>=":0.75},
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
    print(f"  n={n} | size={a.size} | effort={a.effort}")
    print(f"  A={A:.4f}  E={E:.4f}  sigma={sigma:.4f}  Duan={smear:.4f}")
    print(f"  In-sample : MMRE {ins['MMRE']*100:5.1f}%  PRED25 {ins['PRED25']*100:5.1f}%")
    print(f"  LOOCV     : MMRE {cv['MMRE']*100:5.1f}%  PRED25 {cv['PRED25']*100:5.1f}%  PRED30 {cv['PRED30']*100:5.1f}%")
    print(f"  Conte(1986) LOOCV verdict: {'PASS' if results['loocv_conte_pass'] else 'FAIL'}")
    if cross: print(f"  planned vs measured PM: r(log)={cross['corr_log']:+.3f}  median ratio={cross['median_measured_over_planned']:.2f} (n={cross['n']})")
    print("-"*60)
    print("  project                         size   PM_act  PM_loocv")
    for nm,s,e,p in zip(names,size,eff,preds):
        print(f"  {nm[:28]:28} {s:7.2f} {e:7.2f} {p:8.2f}")
    print("="*60)
    print("  Wrote size_effort_params.json and size_effort_results.json")
 
if __name__=="__main__": main()