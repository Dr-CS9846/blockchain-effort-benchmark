# Honest recalibration on actual-effort-only (supersedes the n=8 headline) — 2026-06-20

This document corrects two real problems an expert review found in `CALIBRATION_RESULT.md`, and reports the
result of the fix without curation. **The previous PRED(30)=88% / A=0.56 headline is retracted as a headline**
(kept below only as an exploratory proof-of-concept). Credit to the reviewer: both findings were valid.

## What was wrong

1. **Target contamination.** Of the 8 "core-8" points, only 4 are genuine actual reported effort
   (Subsquare, ink!analyzer, dotreasury, Kheopswap, Remarker, DotCodeSchool = the gold-6; of these the
   headline actually used Kheopswap/Remarker/DotCodeSchool/dotreasury). **megaclite, elara, fennel** carried
   milestone/grant-reported PM and **bagpipes is explicitly "proposed effort" (planned)** — verified: these
   four have **zero rows** in `effort_master_final.csv`. Mixing planned points into an "actual-effort"
   headline is the exact error we had just pivoted away from.
2. **Provenance mismatch.** The headline table applied a *manual raw-size* choice for bagpipes/remarker that
   differs from the `equivalent_ksloc` in the cited `dissect_all.json` (which, with the auto reuse detector,
   gives A_local 7.51 / 6.32). The cited file did not reproduce the headline numbers.

## The honest result — genuine actual-effort only (n=6), pre-registered whole-repo size

Size = deterministic whole-repo `cloc` of the delivery repo (primary); CEVRP equivalent size as sensitivity.
Baselines are **locally calibrated** (not the A=2.94 strawman). LOOCV, Duan smearing.

| size basis | model | SA | MMRE | MdMRE | PRED25 | PRED30 | PRED50 |
|---|---|---|---|---|---|---|---|
| whole-repo (primary) | mean baseline | +0.08 | 149% | 76% | 33% | 33% | 33% |
| whole-repo (primary) | **size-only / ATLM** | **−0.05** | 198% | 98% | 0% | **0%** | 0% |
| whole-repo (primary) | size-only, structural E | −0.01 | 299% | 149% | 0% | 0% | 33% |
| CEVRP equiv (sensitivity) | size-only / ATLM | +0.04 | 168% | 72% | 17% | 17% | 33% |

In-sample free fit (whole-repo): A=0.57, **E=0.48**, Pearson r(lnKSLOC, lnPM)=0.62.

**Reading:** on the clean actual-effort corpus, a calibrated size law **does not beat a naïve mean predictor**
(SA ≈ 0; size-only PRED30 = 0% vs mean 33%). This is a legitimate, citable result, consistent with Whigham
et al. (2015) and Shepperd & MacDonell (2012): on small, heterogeneous corpora a size-only model frequently
fails to outperform simple baselines. **At n=6, this is a proof-of-concept, not a calibrated estimator.**

## The two findings that DO survive any scrutiny (lead with these)

1. **First actual-effort blockchain size↔effort benchmark** — 52 source-cited rows of *actual reported
   delivery effort* (itemised dev-hours / treasury reports), each with a live source URL. This is the asset.
2. **Planned vs actual is the novel contrast.** Planned grant FTE is **size-decoupled** (matched-pair fit,
   n=104: free exponent E=0.10 — size has ~no relationship to budgeted FTE; model degenerates to a ~constant
   predictor). Actual effort shows a **positive but still-weak** size relationship (r≈0.6–0.7 at n=6). The
   planned→actual contrast is real, novel, and defensible regardless of the calibration's eventual accuracy.

## What this means for the plan (the reviewer is right: growth is the whole game)

- **n is the bottleneck, not modelling.** `pilot_sizes.csv` already has ~100 repos sized; the scarce resource
  is *actual reported effort* per project. Every additional genuine actual-effort triple is worth more than any
  modelling refinement. **Target: n≈30 actual-effort triples = the real headline; n=6 is the proof-of-concept.**
- **Pre-register the size rule, not just reuse (CEVRP).** One deterministic commit-selection + slice rule,
  applied blind: whole-repo `cloc` at the delivery tag/commit as primary, CEVRP as a declared sensitivity.
  Headline numbers and the dissection JSON must use identical sizes.
- **Baselines = locally-calibrated size-only + ATLM + mean** on the actual set. Drop the A=2.94 comparison as
  a headline claim (it only proves we recalibrated A, which every model does).
- **Exploratory dissection (driver + reuse adjusted, the old n=8) stays in the appendix** as a hypothesis:
  *with* per-project driver/reuse adjustment the model can reach PRED30≈88%, but those adjustments need
  pre-registration and a larger n to be validated rather than fitted.

## Immediate next actions

1. Grow actual-effort matched triples toward n≈30 (parallel data effort) — measure each new repo's whole-repo
   size in CI as it lands.
2. Add the already-resolvable actual-effort points (Ideal Network 2020 h, TrueBlocks, RFC-bot, SDK-Assets) to
   the dissection spec with the pre-registered size rule; re-run and re-report — honestly, even if n≈10 still
   sits near SA≈0.
3. Keep the planned-vs-actual decoupling result as the lead contribution for the pilot paper.
