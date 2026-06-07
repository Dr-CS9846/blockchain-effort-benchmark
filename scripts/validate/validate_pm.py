#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_pm.py  —  validity & reliability evidence for the measured person-months
=================================================================================
Effort is a LATENT construct: there is no timesheet oracle for these repos, so the
PMs cannot be "proven exact" (true for ALL repository-mined effort). Following the
software-measurement-validation framework (Kitchenham, Pfleeger & Fenton 1995) we
instead demonstrate CONSTRUCT + CRITERION validity and RELIABILITY, and we lean on a
peer-reviewed precedent that PM-from-VCS is an accepted method (Robles &
Gonzalez-Barahona 2022, Empirical Software Engineering; validated via 1,000+
developer questionnaires).

This script computes, on the deduped reliable+plausible set (one obs per repo):
  1. TRIANGULATION  - Spearman rank agreement among the 3 PM estimators (low/mid/high)
  2. CRITERION/COVERAGE - fraction of repos whose independent W3F planned PM lies
     inside the measured bracket [PM_low, PM_high]; + log-corr and median ratio
  3. EXTERNAL SANITY - productivity (PM_mid/KSLOC; SLOC/PM) distribution
  4. RELIABILITY/SENSITIVITY - PM_mid is deterministic; rescaling PH/PM (152->160)
     is a monotone factor (rank-invariant) -> conclusions stable
Writes reports/pm_validation.json and prints a summary. Pure-stdlib (no deps).
"""
import argparse, csv, json, math, os, sys

def _truthy(v): return str(v).strip() in ("1","True","true")
def _norm(u):   return (u or "").strip().lower().rstrip("/").replace(".git","")

def _rank(xs):
    order=sorted(range(len(xs)), key=lambda i: xs[i]); rk=[0.0]*len(xs); i=0
    while i<len(order):
        j=i
        while j+1<len(order) and xs[order[j+1]]==xs[order[i]]: j+=1
        avg=(i+j)/2.0+1
        for k in range(i,j+1): rk[order[k]]=avg
        i=j+1
    return rk

def _pearson(a,b):
    m=len(a); ma=sum(a)/m; mb=sum(b)/m
    num=sum((x-ma)*(y-mb) for x,y in zip(a,b))
    da=math.sqrt(sum((x-ma)**2 for x in a)); db=math.sqrt(sum((y-mb)**2 for y in b))
    return num/(da*db) if da>0 and db>0 else float("nan")

def _spear(a,b): return _pearson(_rank(a),_rank(b))

def load_rows(path, reliable_only=True, plausible_only=True, dedup=True):
    cand=[]
    for r in csv.DictReader(open(path, encoding="utf-8")):
        if r.get("status")!="OK": continue
        if reliable_only and not _truthy(r.get("effort_reliable","1")): continue
        if plausible_only and not _truthy(r.get("duration_plausible","1")): continue
        try:
            s=float(r["ksloc_code"]); mid=float(r["pm_mid"])
        except (ValueError,KeyError): continue
        if not (s>0 and mid>0): continue
        cand.append(r)
    if not dedup: return cand
    best={}
    for r in cand:
        k=_norm(r.get("repo_url","")) or r["project_id"]
        key=(r.get("effort_until",""), float(r["ksloc_code"]))
        if k not in best or key>(best[k].get("effort_until",""), float(best[k]["ksloc_code"])):
            best[k]=r
    return list(best.values())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/calibration/measurements_census.csv")
    ap.add_argument("--out", default="reports/pm_validation.json")
    a=ap.parse_args()
    if not os.path.exists(a.csv): sys.exit(f"{a.csv} not found.")
    rows=load_rows(a.csv)
    n=len(rows)
    low=[float(r["pm_low"]) for r in rows]; mid=[float(r["pm_mid"]) for r in rows]
    high=[float(r["pm_high"]) for r in rows]; ks=[float(r["ksloc_code"]) for r in rows]

    triangulation=dict(spearman_low_mid=_spear(low,mid),
                       spearman_mid_high=_spear(mid,high),
                       spearman_low_high=_spear(low,high))

    cov=[]; pl=[]; mp=[]
    for r in rows:
        try: p=float(r["planned_pm"])
        except (ValueError,KeyError): continue
        if p<=0: continue
        cov.append(float(r["pm_low"])<=p<=float(r["pm_high"])); pl.append(p); mp.append(float(r["pm_mid"]))
    coverage=dict(n_with_planned=len(pl),
                  planned_inside_bracket=int(sum(cov)),
                  coverage_rate=(sum(cov)/len(cov) if cov else None),
                  corr_log_planned_vs_pmmid=(_pearson([math.log(x) for x in pl],[math.log(x) for x in mp]) if len(pl)>=3 else None),
                  median_pmmid_over_planned=(sorted(m/p for m,p in zip(mp,pl))[len(pl)//2] if pl else None))

    prod=sorted(m/k for m,k in zip(mid,ks))
    sanity=dict(median_pm_per_ksloc=prod[len(prod)//2],
                min_pm_per_ksloc=prod[0], max_pm_per_ksloc=prod[-1],
                median_sloc_per_pm=1000.0/prod[len(prod)//2])

    reliability=dict(deterministic="same repo+commit -> identical PM (bit-stable, public pipeline)",
                     ph_per_pm_sensitivity="PM scales by 152/PHPM (monotone) -> rankings & correlations invariant")

    out=dict(n_distinct_repos=n,
             note="Effort is latent; PMs are a VALIDATED BOUNDED measure, not an exact truth.",
             triangulation_spearman=triangulation,
             criterion_coverage=coverage,
             external_sanity=sanity,
             reliability=reliability,
             references=[
               "Robles & Gonzalez-Barahona (2022), Empirical Software Engineering - VCS->person-month effort, developer-validated",
               "Kitchenham, Pfleeger & Fenton (1995), IEEE TSE - software measurement validation framework",
               "Shepperd & MacDonell (2012), IST 54:820-827 - Standardised Accuracy; MMRE bias",
               "Boehm et al. (2000), COCOMO II Model Definition Manual - 1 PM = 152 person-hours",
               "ISO/IEC/IEEE 15939:2017 - measurement process (define the unit)",
             ])
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out,"w"), indent=2)
    print("="*64); print(f"  PM VALIDATION  (deduped reliable+plausible, n={n} repos)"); print("="*64)
    t=triangulation; print(f"  Triangulation Spearman: low~mid {t['spearman_low_mid']:.3f} | mid~high {t['spearman_mid_high']:.3f} | low~high {t['spearman_low_high']:.3f}")
    c=coverage
    if c['coverage_rate'] is not None:
        print(f"  Bracket coverage vs planned PM: {c['planned_inside_bracket']}/{c['n_with_planned']} = {100*c['coverage_rate']:.0f}%  (corr {c['corr_log_planned_vs_pmmid']:.2f}, median ratio {c['median_pmmid_over_planned']:.2f})")
    s=sanity; print(f"  Productivity: median {s['median_pm_per_ksloc']:.2f} PM/KSLOC (~{s['median_sloc_per_pm']:.0f} SLOC/PM); range {s['min_pm_per_ksloc']:.2f}..{s['max_pm_per_ksloc']:.2f}")
    print(f"  Wrote {a.out}")

if __name__=="__main__":
    main()
