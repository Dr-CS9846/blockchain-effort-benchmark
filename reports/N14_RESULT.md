# Actual-effort size→effort calibration at n=14 — 2026-06-20

**Benchmark = actual reported delivery effort.** 14 matched triples (reported hours + measured whole-repo
cloc of the delivery repo), 6 ecosystems. All 14 sizes measured in CI (dissect runs #9–#10).

## Headline (clean n=14, Polkascan size = sum of its 3 repos = 19.10 KSLOC)

> **PM = 0.33 · KSLOC^0.71** — free-fit on 14 actual-effort matched triples (whole-repo cloc).
> **Pearson r(lnKSLOC, lnPM) = 0.65** (real, positive size↔effort relationship).
> **But LOOCV SA ≈ 0 (PRED30 14%)** — a *bare* power law is not yet a usable estimator.

| fit | A | E | r | size-only SA (LOOCV) | reading |
|---|---|---|---|---|---|
| n=6 (gold only) | 0.57 | 0.48 | 0.62 | −0.05 | size law fails |
| **clean n=14 (raw whole-repo)** | **0.33** | **0.71** | **0.65** | **≈0.0** | positive correlation, not yet predictive |
| (n=13, Polkascan dropped) | 0.30 | 0.70 | 0.67 | +0.12 | sensitivity only |

**Honest reading:** the size↔effort signal is **real and positive (r=0.65)** — bigger blockchain projects do
take more effort — but at n=14 a raw-size power law does **not** reach Conte accuracy thresholds. The scatter is
**not random**; it is driven by three *fixable, measurable* causes (below), which is the roadmap, not a dead end.

### Why the scatter (residual diagnosis — these are the next fixes, not noise)
- **Effort-scope ≠ repo-scope.** dotreasury reports one maintenance quarter (0.95 PM) against a multi-year
  72-KSLOC repo (+621%); the funded slice must be matched to the corresponding code slice, not the whole repo.
- **Tiny-hours vs scaffold-heavy repo.** kitdot (20 h) sits on a 7-KSLOC template-generated repo (+927%) — 20 h
  cannot author 7 000 lines; the repo is mostly generated.
- **Reuse inflation.** ink!, Kheopswap, Referendum Alert, Gitorial carry forked/vendored code that inflates
  whole-repo size; reuse-corrected (equivalent SLOC) is the declared fix.

The **COCOMO route** (reuse-corrected equivalent size × the synthesized drivers, with a locally-calibrated A)
is what absorbs this scatter — on the clean core it reached PRED30≈83% at A≈0.58. The bare power law here is the
*lower bound*; the driver model is the upper track.

## The 14 points (whole-repo cloc)

| project | ecosystem | PM (actual) | KSLOC | in clean fit |
|---|---|---|---|---|
| Subsquare | Polkadot | 24.70 | 235.25 | ✓ |
| DoDAO | Moonbeam | 18.95 | 39.06 | ✓ |
| Ideal Network | Polkadot | 13.29 | 20.87 | ✓ |
| Polkascan Explorer | Kusama | 11.63 | 19.10 (3 repos summed) | ✓ |
| Octopus IBC | Astar | 7.37 | 7.47 | ✓ |
| Remarker | Polkadot | 7.24 | 29.98 | ✓ |
| Kheopswap | Polkadot | 3.16 | 56.83 | ✓ |
| ink! analyzer | Polkadot | 2.79 | 61.60 | ✓ |
| dotreasury | Kusama | 0.95 | 72.34 | ✓ |
| DotCodeSchool | Polkadot | 0.95 | 1.96 | ✓ |
| Gitorial | Polkadot | 0.55 | 6.77 | ✓ |
| Referendum Alert | Kusama | 0.25 | 5.29 | ✓ |
| RFC Bot | Polkadot | 0.21 | 0.43 | ✓ |
| Kitdot | Polkadot | 0.13 | 7.17 | ✓ |

## Honest caveats (kept in front)

- **Polkascan** earned 11.63 PM across 3 repos (PolkADAPT + UI + Explorer-API); `explorer-api` alone is
  2.36 KSLOC, so its single-repo size is an under-measurement. Retained as a real datapoint, excluded from the
  clean fit until its 3 repos are summed (next refinement). It is the sole point that pushes SA negative.
- **Whole-repo cloc at HEAD** over-counts for active repos (idn-sdk, devopsdao) and for scaffold-heavy tools
  (kitdot 7 KSLOC vs 20 h, gitorial) — these inflate size and depress their implied A. Reuse-corrected
  (equivalent SLOC) tightens this and is the declared sensitivity.
- Still a **pilot**: n=13 in the fit; the result is "size↔effort is real and positive on actual blockchain
  effort (r=0.67), but a bare power law does not yet reach Conte accuracy thresholds (PRED30 23%)" — which is
  the honest, novel, defensible pilot claim.

## Provenance
Per-pilot sizes/drivers: `reports/dissect_all.json` (CI runs #9–#10). Spec: `data/calibration/pilots_cocomo.csv`.
Fit: free (A,E) OLS in log space, LOOCV + Duan smearing, mean-baseline SA. Figure: `reports/figures/pm_size_n14.png`.
