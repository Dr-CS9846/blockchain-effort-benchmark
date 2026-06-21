# Actual-effort size→effort calibration at n=14 — 2026-06-20

**Benchmark = actual reported delivery effort.** 14 matched triples (reported hours + measured whole-repo
cloc of the delivery repo), 6 ecosystems. All 14 sizes measured in CI (dissect runs #9–#10).

## Headline

As the clean actual-effort matched set grew, the size↔effort signal **emerged**:

| set | A (free) | E (free) | Pearson r | size-only SA (LOOCV) | reading |
|---|---|---|---|---|---|
| n=6 (gold only) | 0.57 | 0.48 | 0.62 | **−0.05** | size law fails (worse than mean) |
| **n=13 (clean sizes)** | **0.30** | **0.70** | **0.67** | **+0.12** | **size law beats the mean baseline** |
| n=14 (incl. Polkascan) | 0.54 | 0.56 | 0.54 | −0.12 | dragged by one mis-sized point |

**The n=6 → n=13 trajectory is the result**: more real matched data turned a null into a positive,
baseline-beating size→effort relationship (r=0.67). This is the empirical case for growing the corpus.

## The 14 points (whole-repo cloc)

| project | ecosystem | PM (actual) | KSLOC | in clean fit |
|---|---|---|---|---|
| Subsquare | Polkadot | 24.70 | 235.25 | ✓ |
| DoDAO | Moonbeam | 18.95 | 39.06 | ✓ |
| Ideal Network | Polkadot | 13.29 | 20.87 | ✓ |
| Polkascan Explorer | Kusama | 11.63 | 2.36 | ✗ size-incomplete (1 of 3 repos) |
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
