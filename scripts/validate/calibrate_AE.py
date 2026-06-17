#!/usr/bin/env python3
"""
calibrate_AE.py — fit Effort = A * Size^E on the verified matched-triple set (measured KSLOC vs stated PM).
Reports A, E with bootstrap CIs, fit quality (R^2 log, MMRE, PRED(25/30)), and sensitivity:
  - gold-6 actual-hours subset (A re-fit at the full-set E)
  - E forced to 1 (constant productivity PM = A*KSLOC)
Honest: no winsorising, no dropping of outliers beyond the already-adjudicated repo fixes. numpy only.
"""
import csv, re, sys, numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PILOTS = ROOT / "data/calibration/VERIFIED_PILOTS.md"
# size source: default raw whole-repo cloc; pass "equiv" to use reuse-adjusted grant-burst equivalent SLOC
MODE = sys.argv[1] if len(sys.argv) > 1 else "raw"
if MODE == "equiv":
    SIZES = ROOT / "data/calibration/pilot_equiv_sloc.csv"
    KSCOL = "equiv_ksloc"
else:
    SIZES = ROOT / "data/calibration/pilot_sizes.csv"
    KSCOL = "ksloc"
GOLD = {"1","4","10","11","12","13"}   # actual-logged-hours rows

def pm_by_id():
    d={}
    for ln in open(PILOTS, encoding="utf-8"):
        if not re.match(r"^\|\s*\d+\s*\|", ln): continue
        c=[x.strip() for x in ln.split("|")]
        if len(c)<9: continue
        idn=c[1]
        m=re.search(r"([0-9]+\.?[0-9]*)", c[7].replace("*",""))
        if m:
            try: d[idn]=float(m.group(1))
            except ValueError: pass
    return d

def main():
    pm=pm_by_id()
    rows=[]
    for r in csv.DictReader(open(SIZES, encoding="utf-8")):
        if r.get("status")!="ok" or not r.get(KSCOL): continue
        idn=r["id"]
        if idn not in pm: continue
        try: ks=float(r[KSCOL])
        except ValueError: continue
        if ks<=0: continue
        rows.append((idn, pm[idn], ks, r.get("source","")))
    ids=[r[0] for r in rows]; P=np.array([r[1] for r in rows]); K=np.array([r[2] for r in rows])
    n=len(rows)
    x=np.log(K); y=np.log(P)

    def fit(x,y):
        E,b0=np.polyfit(x,y,1); return np.exp(b0),E
    A,E=fit(x,y)
    pred=A*K**E
    mre=np.abs(pred-P)/P
    ss_res=np.sum((y-(np.log(A)+E*x))**2); ss_tot=np.sum((y-y.mean())**2)
    r2=1-ss_res/ss_tot
    pear=np.corrcoef(x,y)[0,1]

    # bootstrap CIs
    rng=np.random.default_rng(42); As=[]; Es=[]
    for _ in range(5000):
        idx=rng.integers(0,n,n)
        a,e=fit(x[idx],y[idx]); As.append(a); Es.append(e)
    Aci=np.percentile(As,[2.5,97.5]); Eci=np.percentile(Es,[2.5,97.5])

    print(f"=== Effort = A * KSLOC^E   (n={n} measured matched triples) ===")
    print(f"  A = {A:.3f}   95% CI [{Aci[0]:.3f}, {Aci[1]:.3f}]")
    print(f"  E = {E:.3f}   95% CI [{Eci[0]:.3f}, {Eci[1]:.3f}]")
    print(f"  log-log R^2 = {r2:.3f}   Pearson(lnK,lnP) = {pear:.3f}")
    print(f"  MMRE = {mre.mean():.2f}   MdMRE = {np.median(mre):.2f}   PRED(25) = {100*np.mean(mre<=.25):.0f}%   PRED(30) = {100*np.mean(mre<=.30):.0f}%")

    # E forced to 1 (constant productivity)
    A1=np.exp(np.mean(y-x))
    pred1=A1*K; mre1=np.abs(pred1-P)/P
    print(f"\n  [E:=1 constant productivity]  A = {A1:.3f} PM/KSLOC  → {1000/A1:.0f} SLOC per PM | MMRE {mre1.mean():.2f} PRED30 {100*np.mean(mre1<=.30):.0f}%")

    # gold-6 sensitivity: A refit at full-set E
    gi=[i for i,idn in enumerate(ids) if idn in GOLD]
    if gi:
        Kg=K[gi]; Pg=P[gi]
        Ag=np.exp(np.mean(np.log(Pg)-E*np.log(Kg)))
        # also free fit if >=3
        line=f"\n  [gold-6 actual-hours, n={len(gi)}]  A@E={E:.2f} = {Ag:.3f}  (full-set A {A:.3f}) → shift {100*(Ag-A)/A:+.0f}%"
        print(line)
        print("   gold rows:", ", ".join(f"{ids[i]}(K={K[i]:.1f},PM={P[i]:.1f})" for i in gi))

    # source split
    for s in ("W3F","Crust","POSG"):
        si=[i for i,r in enumerate(rows) if r[3]==s]
        if len(si)>=2:
            print(f"  source {s:5} n={len(si):3}  meanK {K[si].mean():6.1f}  meanPM {P[si].mean():4.1f}")

    # biggest residuals (honest outlier surface)
    resid=np.log(P)-(np.log(A)+E*np.log(K))
    order=np.argsort(-np.abs(resid))[:8]
    print("\n  largest residuals (review): " + ", ".join(f"{ids[i]}({'over' if resid[i]<0 else 'under'}-est x{np.exp(abs(resid[i])):.1f})" for i in order))

if __name__=="__main__":
    main()
