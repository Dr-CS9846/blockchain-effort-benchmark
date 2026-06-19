#!/usr/bin/env python3
"""Fit Effort = A * Size^E on the verified matched-triple set.
Usage: calibrate_AE.py [raw|equiv]   (raw = whole-repo cloc; equiv = reuse-adjusted grant-burst SLOC)
Reports A, E with bootstrap CIs, log R^2, MMRE, PRED(25/30), gold-6 sensitivity, E:=1 variant, top residuals.
numpy only; no winsorising / outlier dropping beyond already-adjudicated repo fixes."""
import csv, re, sys
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PILOTS = ROOT / "data/calibration/VERIFIED_PILOTS.md"
MODE = sys.argv[1] if len(sys.argv) > 1 else "raw"
if MODE == "equiv":
    SIZES = ROOT / "data/calibration/pilot_equiv_sloc.csv"
    KSCOL = "equiv_ksloc"
else:
    SIZES = ROOT / "data/calibration/pilot_sizes.csv"
    KSCOL = "ksloc"
GOLD = {"1", "4", "10", "11", "12", "13"}


def pm_by_id():
    d = {}
    for ln in open(PILOTS, encoding="utf-8"):
        if not re.match(r"^\|\s*\d+\s*\|", ln):
            continue
        c = [x.strip() for x in ln.split("|")]
        if len(c) < 9:
            continue
        m = re.search(r"([0-9]+\.?[0-9]*)", c[7].replace("*", ""))
        if m:
            try:
                d[c[1]] = float(m.group(1))
            except ValueError:
                pass
    return d


def fit(x, y):
    E, b0 = np.polyfit(x, y, 1)
    return np.exp(b0), E


def main():
    pm = pm_by_id()
    ids, P, K = [], [], []
    for r in csv.DictReader(open(SIZES, encoding="utf-8")):
        if r.get("status") != "ok" or not r.get(KSCOL):
            continue
        if r["id"] not in pm:
            continue
        try:
            ks = float(r[KSCOL])
        except ValueError:
            continue
        if ks <= 0:
            continue
        ids.append(r["id"])
        P.append(pm[r["id"]])
        K.append(ks)
    P = np.array(P)
    K = np.array(K)
    n = len(ids)
    x = np.log(K)
    y = np.log(P)

    A, E = fit(x, y)
    pred = A * K ** E
    mre = np.abs(pred - P) / P
    ss_res = np.sum((y - (np.log(A) + E * x)) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot
    pear = np.corrcoef(x, y)[0, 1]

    rng = np.random.default_rng(42)
    As, Es = [], []
    for _ in range(5000):
        idx = rng.integers(0, n, n)
        a, e = fit(x[idx], y[idx])
        As.append(a)
        Es.append(e)
    Aci = np.percentile(As, [2.5, 97.5])
    Eci = np.percentile(Es, [2.5, 97.5])

    print("=== Effort = A * KSLOC^E   mode=%s   n=%d ===" % (MODE, n))
    print("  A = %.3f   95%% CI [%.3f, %.3f]" % (A, Aci[0], Aci[1]))
    print("  E = %.3f   95%% CI [%.3f, %.3f]" % (E, Eci[0], Eci[1]))
    print("  log-log R^2 = %.3f   Pearson = %.3f" % (r2, pear))
    print("  MMRE %.2f  MdMRE %.2f  PRED25 %.0f%%  PRED30 %.0f%%"
          % (mre.mean(), np.median(mre), 100 * np.mean(mre <= .25), 100 * np.mean(mre <= .30)))

    A1 = np.exp(np.mean(y - x))
    mre1 = np.abs(A1 * K - P) / P
    print("  [E:=1]  A=%.3f PM/KSLOC (%.0f SLOC/PM)  MMRE %.2f PRED30 %.0f%%"
          % (A1, 1000 / A1, mre1.mean(), 100 * np.mean(mre1 <= .30)))

    gi = [i for i, idn in enumerate(ids) if idn in GOLD]
    if gi:
        Kg = K[gi]
        Pg = P[gi]
        Ag = np.exp(np.mean(np.log(Pg) - E * np.log(Kg)))
        print("  [gold-6 n=%d]  A@E=%.2f = %.3f  (full A %.3f, shift %+.0f%%)"
              % (len(gi), E, Ag, A, 100 * (Ag - A) / A))

    resid = y - (np.log(A) + E * x)
    order = np.argsort(-np.abs(resid))[:8]
    tags = []
    for i in order:
        d = "over" if resid[i] < 0 else "under"
        tags.append("%s(%s x%.1f)" % (ids[i], d, np.exp(abs(resid[i]))))
    print("  top residuals: " + ", ".join(tags))


if __name__ == "__main__":
    main()
