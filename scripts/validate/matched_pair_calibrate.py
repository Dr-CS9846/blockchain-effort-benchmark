#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
matched_pair_calibrate.py  —  the right model: calibrate COCOMO II to REPORTED PM on MATCHED pairs
===================================================================================================
Every prior PM=PM attempt broke the one rule COCOMO requires: each data point must pair the EFFORT
that built ONE artifact with the SIZE of that SAME artifact. Here we enforce it on the W3F grant
census, which is close to an ideal matched pair: one team, one own-org repo built for the grant,
one REPORTED effort (planned_pm = FTE x duration from the application).

  unit:   one grant -> one repo (census single-separable own-org repo)
  effort: planned_pm  (human-REPORTED, not git-mined)              <- the clean target
  size:   equivalent SLOC of that repo at delivery (already measured)
  gate:   greenfield-ish (measured first-commit->delivery span <= maxduration), planned_pm>0,
          size>0, real dev history (effort_reliable). NO git velocity gate (irrelevant to a
          reported target), and deliberately NO size/effort-ratio gate (that would manufacture
          the very correlation we are testing).

Calibrations (LOOCV, Duan smearing): size-only power law PM=A*Size^E (free A,E and fixed E=0.91),
and the full fixed-weight COCOMO II (A recalibrated). Reports SA/MMRE/PRED + per-project residuals
(reported vs predicted) so we can SEE which projects the size model misses -> where hand-assigned
drivers must do the work. This is the foundation triple-set; hand-curated drivers come next.

Reuses cocomo_fit (load + synthesis + q). Output: reports/matched_pair_pm.json
"""
import argparse, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import cocomo_fit as F

def loocv_size(y, lnS, fixedE=None):
    n = len(y); preds = np.zeros(n)
    for i in range(n):
        idx = [j for j in range(n) if j != i]
        if fixedE is None:
            X = np.column_stack([np.ones(n - 1), lnS[idx]])
            b, *_ = np.linalg.lstsq(X, y[idx], rcond=None)
            res = y[idx] - X @ b; lnA, E = b[0], b[1]
        else:
            E = fixedE; resid = y[idx] - E * lnS[idx]; lnA = float(np.mean(resid)); res = resid - lnA
        preds[i] = math.exp(lnA + E * lnS[i]) * math.exp(np.var(res) / 2)
    return preds

def metrics(actual, preds):
    actual = np.asarray(actual); preds = np.asarray(preds); mre = np.abs(actual - preds) / actual
    marp0 = np.mean(np.abs(actual[:, None] - actual[None, :]))
    return dict(SA=round(float(1 - np.mean(np.abs(actual - preds)) / marp0), 3),
                MMRE=round(float(np.mean(mre)), 3), MdMRE=round(float(np.median(mre)), 3),
                PRED25=round(float(np.mean(mre <= .25)), 3), PRED30=round(float(np.mean(mre <= .30)), 3))

def main():
    ap = argparse.ArgumentParser()
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--meas", default=os.path.join(root, "data/calibration/measurements_census.csv"))
    ap.add_argument("--attr", default=os.path.join(root, "data/calibration/repo_attributes.csv"))
    ap.add_argument("--out",  default=os.path.join(root, "reports/matched_pair_pm.json"))
    ap.add_argument("--maxdur", type=float, default=18.0)
    a = ap.parse_args()

    # matched pairs: target = REPORTED planned_pm; size = equivalent SLOC; velocity gate OFF.
    cand = F.load(a.meas, a.attr, "planned_pm", reliable_only=True, plausible_only=True, dedup=True,
                  maxlocday=1e12, minlocday=0.0, maxduration=a.maxdur)
    n = len(cand)
    if n < 8: sys.exit(f"only {n} matched pairs")
    y, q, cols, rows = F.q_and_columns(cand)             # y=ln(planned_pm), q=ln(COCOMO pred w/o A)
    lnS = np.array([math.log(S) for (_m, _a, S, _pm) in cand])
    actual = np.exp(y)

    # 1) size-only power law (free A,E) and (fixed E=0.91)
    pf = loocv_size(y, lnS, None); pe = loocv_size(y, lnS, 0.91)
    Xa = np.column_stack([np.ones(n), lnS]); ba, *_ = np.linalg.lstsq(Xa, y, rcond=None)
    # 2) full fixed-weight COCOMO II (only A recalibrated), LOOCV
    cocomo = F.loocv_metrics(y, q)

    # per-project residuals for the size-only-free model (where do drivers need to help?)
    resid = []
    for i, (m, a_, S, pm) in enumerate(cand):
        resid.append(dict(project_id=m["project_id"], reported_pm=round(pm, 2),
                          ksloc=round(F._fnum(m, "ksloc_code") or 0, 2), equiv_ksloc=round(S, 2),
                          pred_size_pm=round(float(pf[i]), 2),
                          pct_err=round(abs(pm - pf[i]) / pm * 100, 1)))
    resid.sort(key=lambda r: -r["pct_err"])

    out = dict(n=n, target="planned_pm (reported FTE*duration)", note="matched-pair calibration",
               size_only_free=dict(A=round(math.exp(ba[0]), 3), E=round(float(ba[1]), 3), loocv=metrics(actual, pf)),
               size_only_fixedE0_91=dict(loocv=metrics(actual, pe)),
               full_cocomoII_fixedweight=dict(loocv=cocomo),
               worst_residuals=resid[:15], best_residuals=resid[-10:])
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=2)
    sf = out["size_only_free"]
    print("=" * 70); print(f"MATCHED-PAIR PM=PM  (target=planned_pm, n={n})"); print("=" * 70)
    print(f"  size-only free (A={sf['A']}, E={sf['E']}): SA {sf['loocv']['SA']}  "
          f"PRED25 {sf['loocv']['PRED25']*100:.0f}%  PRED30 {sf['loocv']['PRED30']*100:.0f}%  MMRE {sf['loocv']['MMRE']*100:.0f}%")
    print(f"  size-only fixed E=0.91: SA {out['size_only_fixedE0_91']['loocv']['SA']}  "
          f"PRED30 {out['size_only_fixedE0_91']['loocv']['PRED30']*100:.0f}%")
    print(f"  full fixed-weight COCOMO II: SA {cocomo['SA']}  PRED30 {cocomo['PRED30']*100:.0f}%")
    print(f"  wrote {a.out}")

if __name__ == "__main__":
    main()
