#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""calibrate_actual.py — calibrate PM = A*KSLOC^E on the ACTUAL reported-effort matched set
(reported delivery person-months paired with measured reuse-adjusted equivalent SLOC of the
same artifact). Free (A,E) and COCOMO-fixed E=0.91. LOOCV + Duan smearing. Honest small-n core."""
import json, math, sys
import numpy as np
from pathlib import Path

# matched pairs: (project, PM_actual_reported, equiv_ksloc_measured, source)
PAIRS = [
 ("Subsquare gov app",        24.70, 231.580, "3760 dev-hrs itemised; equiv SLOC measured"),
 ("ink! analyzer",             2.79,  37.849, "reported; equiv SLOC measured"),
 ("dotreasury",                0.95,  44.165, "~20 dev-days; equiv SLOC measured"),
 ("Kheopswap DEX UI",          3.16,  21.210, "480 dev-hrs; equiv SLOC measured"),
 ("Remarker NFT market",       7.24,  16.794, "1100 work-hrs; equiv SLOC measured"),
 ("Dot Code School",           0.95,   2.783, "reported; equiv SLOC measured"),
]

def metrics(actual, preds):
    actual=np.asarray(actual,float); preds=np.asarray(preds,float)
    mre=np.abs(actual-preds)/actual
    marp0=np.mean(np.abs(actual[:,None]-actual[None,:]))
    return dict(SA=round(float(1-np.mean(np.abs(actual-preds))/marp0),3),
                MMRE=round(float(np.mean(mre)),3), MdMRE=round(float(np.median(mre)),3),
                PRED25=round(float(np.mean(mre<=.25)),3), PRED30=round(float(np.mean(mre<=.30)),3))

def loocv(y, lnS, fixedE=None):
    n=len(y); preds=np.zeros(n)
    for i in range(n):
        idx=[j for j in range(n) if j!=i]
        if fixedE is None:
            X=np.column_stack([np.ones(n-1), lnS[idx]])
            b,*_=np.linalg.lstsq(X,y[idx],rcond=None); lnA,E=b[0],b[1]; res=y[idx]-X@b
        else:
            E=fixedE; resid=y[idx]-E*lnS[idx]; lnA=float(np.mean(resid)); res=resid-lnA
        preds[i]=math.exp(lnA+E*lnS[i])*math.exp(np.var(res)/2)   # Duan smearing
    return preds

def fit_full(y, lnS, fixedE=None):
    if fixedE is None:
        X=np.column_stack([np.ones(len(y)), lnS]); b,*_=np.linalg.lstsq(X,y,rcond=None)
        return math.exp(b[0]), float(b[1])
    lnA=float(np.mean(y-fixedE*lnS)); return math.exp(lnA), fixedE

pm=np.array([p[1] for p in PAIRS]); ks=np.array([p[2] for p in PAIRS])
y=np.log(pm); lnS=np.log(ks)
out={"n":len(PAIRS),"target":"actual reported delivery PM","pairs":[
       {"project":p[0],"pm_actual":p[1],"equiv_ksloc":p[2]} for p in PAIRS]}

for tag,fE in [("free",None),("fixedE0.91",0.91)]:
    A,E=fit_full(y,lnS,fE)
    preds=loocv(y,lnS,fE)
    m=metrics(pm,preds)
    out[tag]={"A":round(A,3),"E":round(E,3),"loocv":m,
              "insample_pred":[round(float(x),2) for x in (np.exp(fit_full and (math.log(A)+E*lnS)))]}
    print("%-12s A=%6.3f E=%5.3f | SA %5.3f PRED25 %3.0f%% PRED30 %3.0f%% MMRE %4.0f%% MdMRE %4.0f%%"%(
          tag,A,E,m["SA"],100*m["PRED25"],100*m["PRED30"],100*m["MMRE"],100*m["MdMRE"]))

# per-project parity for the free fit
A,E=fit_full(y,lnS,None)
print("\n project                       PM_actual  equiv_KSLOC  PM_pred  %err")
rows=[]
for (name,a,k,_),lk in zip(PAIRS,lnS):
    pred=A*(k**E); err=100*(pred-a)/a
    rows.append({"project":name,"pm_actual":a,"equiv_ksloc":k,"pm_pred":round(pred,2),"pct_err":round(err,1)})
    print("  %-28s %7.2f  %9.2f  %7.2f  %+6.1f"%(name,a,k,pred,err))
out["free_insample"]=rows
Path("reports").mkdir(exist_ok=True)
json.dump(out, open("reports/calibrate_actual.json","w"), indent=2)
print("\nwrote reports/calibrate_actual.json")
