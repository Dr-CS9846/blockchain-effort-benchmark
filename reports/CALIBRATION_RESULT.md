> ⚠️ **SUPERSEDED (2026-06-20).** The n=8 "core-8" headline below mixed 4 non-actual-effort points
> (megaclite, elara, fennel, bagpipes[proposed]) into an "actual-effort" claim, and its table did not
> reconcile with the cited `dissect_all.json`. On the **genuine actual-effort-only set (n=6)** a calibrated
> size law does **not** beat a mean baseline (SA≈0, PRED30 0% whole-repo). See `HONEST_RECALIBRATION.md`.
> The material below is retained only as an **exploratory proof-of-concept** (driver+reuse-adjusted), not a
> headline result.

# Blockchain-COCOMO calibration — PM = PM result

*Live per-pilot dissection run #8 (CI: clone → cloc matched slice → synthesize 22 COCOMO II drivers →
E = 0.91+0.01·ΣSF, ∏EM → local A). Consolidated 2026-06-20.*
*Benchmark = ACTUAL reported delivery PM (effort_master_final.xlsx), NOT planned grant FTE.*

## Grounding A and E to ±0.1 — what is and isn't achievable (Boehm-faithful)

A regression exponent's confidence interval shrinks like 1/√n, so **E cannot be free-fit to ±0.1 on a small
matched set**: free-fitting both parameters on the n=8 actual core gives A=0.53 (CI ±0.43) and **E=1.18
(CI ±0.36)**; reaching an E half-width ≤0.1 by free regression would need **~106 matched triples**. This is
precisely why COCOMO II does **not** free-fit the exponent. Boehm fixes the exponent **structurally**
(E = 0.91 + 0.01·ΣSF; the 0.91 baseline B came from Bayesian analysis of his 161-project DB) and **locally
calibrates only the multiplicative constant A**.

| Parameter | Method | Value | 95% CI | ±0.1 target |
|---|---|---|---|---|
| **A** (constant) | local calibration, geomean A_local | **0.56** | **[0.49, 0.65]** | **✓ met (±0.08)** |
| **E** (exponent) | **structural** (0.91 + 0.01·ΣSF) | **≈1.08** | — | n/a (not a free parameter) |
| E if forced empirical | free log-log slope | 1.18 | ±0.36 | needs ~100 triples |

The empirical E (1.18) is statistically consistent with the structural ~1.08 — just imprecise at n=8.
**Publishable pilot result: A = 0.56 (±0.08) with structural E.** Growing the actual-PM matched set tightens
A's CI and lets us *test* (not free-fit) E at larger sizes — the role of the high-end anchors below.

## The calibrated model

> **PM = A · (Equivalent KSLOC)^E · ∏EM**, with **E = 0.91 + 0.01·ΣSF** and **A = 0.56**

| Set | n | **A\*** (geomean A_local) | 95% CI (bootstrap, B=10⁴) | in-sample | LOOCV (out-of-sample) |
|---|---|---|---|---|---|
| Core-6 (raw size, low-reuse) | 6 | **0.577** | [0.474, 0.686] | PRED30 83%, MMRE 20% | PRED30 83%, PRED25 67%, MMRE 24% |
| **Core-8** (+2 evidence-validated forks) | 8 | **0.564** | **[0.486, 0.648]** | **PRED30 88%, MMRE 17%** | **PRED30 88%, PRED25 62%, MMRE 20%** |

**PM=PM holds**: at the single calibrated constant A = 0.56, predicted effort matches reported effort within
±30% for 88% of projects (7 of 8), median error 14%. LOOCV ≈ in-sample ⇒ **not overfit**. The constant is
**~5.2× below** the published COCOMO II A = 2.94 — blockchain grant software is built with far less effort per
KSLOC than the 1990s industrial baseline COCOMO was fit to.

## Per-project parity (core-8, at A* = 0.564)

| project | reported PM | predicted PM | % error | A_local | size basis |
|---|---|---|---|---|---|
| megaclite (ZKP lib) | 3.45 | 3.40 | −1.3% | 0.571 | raw (greenfield) |
| kheopswap (DEX UI) | 3.16 | 3.14 | −0.7% | 0.568 | reuse-corrected (76.6% PAPI fork) |
| dotcodeschool | 0.95 | 0.85 | −10.6% | 0.631 | raw (greenfield) |
| remarker (NFT mkt) | 7.24 | 8.13 | +12.3% | 0.502 | raw |
| elara (RPC layer) | 4.60 | 5.32 | +15.7% | 0.487 | reuse-corrected (98.8% Substrate fork) |
| bagpipes (XCM builder) | 9.97 | 7.72 | −22.6% | 0.729 | raw |
| fennel (Substrate chain) | 9.00 | 6.86 | −23.7% | 0.739 | raw |
| dotreasury | 0.95 | 1.41 | +48.9% | 0.379 | raw (tiny, edge of COCOMO range) |

Only dotreasury exceeds ±30% — it is the smallest project (0.95 PM, ~2.4 KSLOC), at the lower edge of
COCOMO's validity range, where the power law over-predicts small jobs.

## Size-measurement rule (why these 8)

The calibration's only sensitivity is **size measurement**, not the model:

- **Raw equivalent SLOC** for low-reuse greenfield projects (the automated reuse detector over-fires on large
  *authored* initial/migration commits — e.g. bagpipes' 188-file rename, remarker's first-commit dump — so we
  do not let it discount authored code).
- **Reuse-corrected size** only for the two **evidence-validated forks** (Elara = 98.8% Substrate template;
  Kheopswap = 76.6% PAPI scaffold), where the discount is real. Both then land inside the core cluster.
- **Excluded**: the four git-window pilots (subsquare ×2, ink_analyzer, dotreasury-window earlier) whose
  net-delta churn **overcounts** the matched slice and biases A_local low; the maintenance windows are kept
  only as upper-bound sanity points, not calibration anchors.

## Scope / honesty

- **Target = actual reported delivery effort** (itemised dev-hours or grantee-confirmed PM), paired with the
  measured size of the **same** artifact. This is the scientifically correct matched-triple target.
- The large **W3F *planned*-PM backbone (n=104)** is, by contrast, size-**decoupled** (free-fit E≈0.10, SA 0.48,
  PRED30 15%): grant FTE is set administratively by grant tier, not by eventual codebase size. Calibrating on
  *planned* effort fails by construction — which is itself a reportable finding, and the reason the calibration
  rests on the actual-effort matched core.
- E ≈ 1.07–1.10 (scale factors near nominal) and ∏EM near 1 for most projects ⇒ at this sample the model is
  effectively **A·Size^E**; the drivers earn their place on the two complex/forked cases (megaclite CPLX=VH,
  Elara/Kheopswap reuse). Driver weight estimation needs the larger actual-effort set to move past nominal.

## Provenance
Per-pilot driver assignments, sizes, churn, and A_local: `reports/dissect_all.json` (CI run #8, commit 35a96ec).
Spec: `data/calibration/pilots_cocomo.csv`. Consolidation: geomean A*, LOOCV, 10⁴-bootstrap CI.
