#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pilot_measure.py  —  Steps 2-3: COCOMO II PM on the cleanly-reported pilots; verify PM=PM
==========================================================================================
For each pilot (human-REPORTED PM + a code repo), measure delivered size and compare COCOMO II's
predicted PM against the reported PM. This is the first PM=PM test on cleanly-reported data - the
whole point of the curated-calibration plan.

v1 (size-based, leak-free, self-contained): clone the pilot's primary code repo, count logical SLOC
(cloc, generated-excluded - reusing measure_repos), then fit the COCOMO power law to the REPORTED
PMs:  ln PM = ln A + E * ln(KSLOC).  Two calibrations:
  - fixed Boehm exponent E=0.91, A fit by MLE
  - free (A,E) fit
LOOCV predicted-vs-reported (SA / MMRE / PRED25 / PRED30) + a per-pilot PM=PM table.
(Drivers/effort-multipliers can be layered next; size-only is the honest first baseline.)

Repo pick per pilot: first own-org SUBSTANTIVE repo (drop dependency/meta orgs + grants/template repos).
Reads data/calibration/pilot_cases.csv. Output: reports/pilot_pm_compare.json
"""
import argparse, csv, json, math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "extract"))
import numpy as np
import measure_repos as M     # ensure_clone, count_sloc, resolve_commit, _run

DEP_ORGS = {"paritytech", "use-ink", "w3f", "type-metadata", "scale-info", "ibp-network",
            "layerzero-labs", "user-attachments", "slickup", "polkadot-fellows", "substrate-developer-hub"}
META = ("grants-program", "grants-pro", "grant-milestone", "template", "node-template", "spec", "config",
        "playground", "repro", "monorepo-spec")

def pick_repo(repos_field):
    cands = [x.strip() for x in (repos_field or "").split(";") if "/" in x]
    own = [c for c in cands if c.split("/")[0].lower() not in DEP_ORGS
           and not any(m in c.split("/")[1].lower() for m in META)]
    pool = own or cands
    return pool[0] if pool else ""

def main():
    ap = argparse.ArgumentParser()
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--inp", default=os.path.join(root, "data/calibration/pilot_cases.csv"))
    ap.add_argument("--out", default=os.path.join(root, "reports/pilot_pm_compare.json"))
    ap.add_argument("--min-conf", default="HIGH", choices=["HIGH", "MED", "LOW"])
    a = ap.parse_args()
    rank = {"HIGH": 0, "MED": 1, "LOW": 2}; lim = rank[a.min_conf]

    rows = [r for r in csv.DictReader(open(a.inp, encoding="utf-8"))
            if rank.get(r.get("confidence", "LOW"), 2) <= lim and (r.get("github_repos") or "").strip()]
    measured = []
    for r in rows:
        repo = pick_repo(r.get("github_repos", ""))
        if not repo: continue
        url = "https://github.com/" + repo
        pid = f"{r['network']}-{r['proposal_type']}-{r['index']}"
        try:
            d = M.ensure_clone(pid, url)
            sha, _src = M.resolve_commit(d, "", "")
            M._run(["git", "checkout", "--quiet", "-f", sha], cwd=d)
            kc, ka, top, kc_raw, gen, genf = M.count_sloc(d)
        except Exception as e:
            print(f"  ERR {pid} {repo}: {str(e)[:90]}"); continue
        try: pm = float(r["stated_pm"])
        except (ValueError, TypeError): continue
        if kc <= 0 or pm <= 0: continue
        measured.append(dict(pid=pid, index=r["index"], title=r["title"][:60], repo=repo,
                             reported_pm=round(pm, 2), ksloc=round(kc, 3), basis=r.get("pm_basis", "")))
        print(f"  OK {pid} {repo}: ksloc={kc:.2f} reported_pm={pm}")

    n = len(measured)
    out = dict(n=n, min_confidence=a.min_conf, pilots=measured)
    if n >= 4:
        y = np.array([math.log(m["reported_pm"]) for m in measured])
        lnK = np.array([math.log(m["ksloc"]) for m in measured])
        def loocv(fixedE=None):
            preds = np.zeros(n)
            for i in range(n):
                idx = [j for j in range(n) if j != i]
                if fixedE is None:
                    X = np.column_stack([np.ones(n - 1), lnK[idx]])
                    b, *_ = np.linalg.lstsq(X, y[idx], rcond=None)
                    res = y[idx] - X @ b; lnA, E = b[0], b[1]
                else:
                    E = fixedE; resid = y[idx] - E * lnK[idx]; lnA = np.mean(resid); res = resid - lnA
                preds[i] = math.exp(lnA + E * lnK[i]) * math.exp(np.var(res) / 2)
            act = np.exp(y); mre = np.abs(act - preds) / act
            marp0 = np.mean(np.abs(act[:, None] - act[None, :]))
            return dict(SA=round(float(1 - np.mean(np.abs(act - preds)) / marp0), 3),
                        MMRE=round(float(np.mean(mre)), 3), PRED25=round(float(np.mean(mre <= .25)), 3),
                        PRED30=round(float(np.mean(mre <= .30)), 3)), preds
        free, pf = loocv(None); fixed, pxf = loocv(0.91)
        Xall = np.column_stack([np.ones(n), lnK]); ball, *_ = np.linalg.lstsq(Xall, y, rcond=None)
        out["calibration_free"] = dict(A=round(math.exp(ball[0]), 3), E=round(float(ball[1]), 3), loocv=free)
        out["calibration_fixedE0.91"] = dict(loocv=fixed)
        for i, m in enumerate(measured):
            m["pred_pm_free"] = round(float(pf[i]), 2)
            m["abs_pct_err_free"] = round(abs(m["reported_pm"] - pf[i]) / m["reported_pm"] * 100, 1)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=2)
    print("=" * 70)
    print(f"PILOT PM=PM  n={n}")
    if n >= 4:
        print(f"  free (A={out['calibration_free']['A']}, E={out['calibration_free']['E']}): "
              f"LOOCV SA {free['SA']}  PRED30 {free['PRED30']*100:.0f}%  MMRE {free['MMRE']*100:.0f}%")
        print(f"  fixed E=0.91: LOOCV SA {fixed['SA']}  PRED30 {fixed['PRED30']*100:.0f}%")
        print("  reported vs predicted:")
        for m in measured:
            print(f"    {m['index']:>5} rep={m['reported_pm']:>6} pred={m.get('pred_pm_free','?'):>6} "
                  f"({m.get('abs_pct_err_free','?')}%) ksloc={m['ksloc']:.1f} {m['title'][:38]}")
    print(f"Wrote {a.out}")

if __name__ == "__main__":
    main()
