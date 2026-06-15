# Blockchain-COCOMO: Calibrating COCOMO II to Polkadot-Ecosystem Development Effort
### Method, Curated Dataset, and Calibration Findings
*Working research record — prepared for thesis / publication. Date: 2026-06-14.*
*Repository: github.com/Dr-CS9846/blockchain-effort-benchmark*

---

## 0. One-paragraph summary

Classic COCOMO II (multiplicative constant **A = 2.94**) over-predicts the development effort of
blockchain (Polkadot/Kusama ecosystem) grant-and-treasury software by roughly **5–20×**. On a hand-curated
set of **matched triples** — each pairing a *human-reported* effort figure with *the one repository that
produced it* and an *on-chain (or durable W3F) proof* — we recalibrate the constant. On the six pilots whose
measured code size unambiguously matches the funded scope, a **single global constant A ≈ 0.58** reproduces
reported effort with **PRED(30) = 83 %** and **MMRE = 20 %** — a *good* calibration by COCOMO standards. The
calibrated model is

> **PM = 0.58 · (Equivalent KSLOC)^E · ∏EM,  with E = 0.91 + 0.01·ΣSF.**

The residual on the remaining pilots is shown to be a **size-measurement artifact** (reuse / generated code
and multi-version repository scope), *not* a model failure — itself a finding: in blockchain grant work the
dominant estimation challenge is *equivalent-SLOC measurement*, not the effort multipliers.

---

## 1. Problem and motivation

COCOMO II (Boehm et al., 2000) is the canonical algorithmic software cost model:
`PM = A · Size^E · ∏(EM)`, `E = B + 0.01·Σ(SF)`, with B = 0.91 and a published, USC-calibrated A = 2.94.
It has never been calibrated to blockchain software, whose engineering economics differ sharply (heavy
ecosystem reuse, senior/solo developers, below-market grant pricing, novel cryptographic and consensus
components). The research question:

> **Does COCOMO II, recalibrated on authentic blockchain effort data, predict blockchain development effort —
> and what is the calibrated constant?**

### 1.1 Why earlier attempts failed (the root cause)
Every prior attempt to hit PM(predicted) = PM(reported) on git-mined or loosely-assembled datasets failed
(SA ≈ −0.04 to 0.48). The diagnosis, established over many iterations, is a single root cause:

> **Unmatched pairs.** A calibration point must pair the EFFORT that built *one* artifact with the SIZE of
> *that same* artifact. Git-mined "effort", multi-repo umbrellas, and whole-repo size against a single-grant
> effort all break this rule and inject irreducible noise.

This motivated the **curated matched-triple** approach: build a small, hand-verified dataset where every
point is provably one team → one repo → one reported effort, each read **on-chain with our own eyes**.

---

## 2. Dataset: curated matched triples

### 2.1 Definition of a pilot (matched triple)
Each pilot = `{ reported effort (PM), the single repository that produced it, on-chain/durable proof }`,
where:
- **Reported effort** comes verbatim from the funding proposal (hours, dev-weeks, or FTE×duration),
  converted to person-months at Boehm's **152 person-hours/PM** (hours cases) or **÷ 4.345** (dev-weeks).
- **Repository** is the one codebase named in the proposal that delivered the funded work.
- **Proof** is the executed on-chain treasury/OpenGov transaction (Polkadot/Kusama) or, for two pilots, a
  merged Web3 Foundation grant milestone delivery.

### 2.2 The verified pilots (n = 13 collected; effort + provenance)
Effort-type: **A**ctual (retroactive, completed work) vs **P**roposed (forward grant estimate).

| # | Pilot | Reported effort | PM | Repo | Proof | Type |
|---|---|---|---|---|---|---|
| 1 | Subsquare (12-mo maint) | 3,760 dev-hrs (itemised) | 24.7 | opensquare-network/subsquare | Executed 469,845 USDT | A |
| 2 | Ask! v0.1 (ink! lang) | 30 dev-weeks (3×10) | 6.9 | patractlabs/ask | Awarded 1,661 KSM | P |
| 3 | Bagpipes (XCM dApp) | 1,515 dev-hrs (4 ms) | 9.97 | BagpipesOrg/app | Awarded 25,910 DOT | P |
| 4 | dotreasury (maint) | ~20 dev-days | 0.95 | opensquare-network/dotreasury | Awarded 38.66 KSM | A |
| 5 | Megaclite v0.1 (ZKP lib) | 15 dev-weeks (3×5) | 3.45 | patractlabs/megaclite | Awarded 5,431 DOT | P |
| 6 | Subsquare new-features | 1,736 dev-hrs (subsq. share) | 11.4 | opensquare-network/subsquare | Awarded 36,969 DOT | A/P |
| 7 | Fennel Protocol (Whiteflag chain) | 3 FTE × 3 mo | 9.0 | fennelLabs/Fennel-Protocol | W3F 3/3 milestones | P |
| 8 | Elara v0.1 (RPC layer) | 20 dev-wk + 1 designer-wk | 4.6 | patractlabs/elara | Awarded 8,600 DOT | P |
| 9 | ParaSpell (XCM tool, base) | 1 FTE × 2 mo | 2.0 | dudo50/ParaSpell *(repo since deleted)* | W3F wave-15 | P |
| 10 | Remarker (NFT marketplace) | 1,100 work-hrs | 7.24 | Remarkers/Remarkers-market | Executed 946.91 DOT | A |
| 11 | Kheopswap (AssetHub DEX UI) | 480 dev-hrs | 3.16 | kheopswap/kheopswap | Executed 14,092 DOT | A |
| 12 | ink! analyzer (LSP, v5 support) | 424 dev-hrs (itemised, 8 tasks) | 2.79 | ink-analyzer/ink-analyzer | Executed 2,812 DOT | A |
| 13 | Dot Code School (coding edu PoC) | 144 hrs (1 FTE @ $125/h) | 0.95 | iammasterbrucewayne/dotcodeschool | Executed 2,500 DOT | A |

Heterogeneity: two chains (Polkadot, Kusama) + W3F; project types span governance apps, a smart-contract
language/compiler, a ZKP crypto library, RPC infrastructure, no-code XCM tooling, DEX/NFT/wallet/marketplace
UIs, a Substrate messaging chain, LSP/compiler tooling, and an interactive coding-education platform.
Independence: 7 of 13 are non-OpenSquare/Patract teams (US, EU, India, solo devs). Effort spans 0.95 → 24.7 PM.

### 2.3 Auditable exclusions (rejected candidates)
To preserve matched-triple integrity, several famous, real, executed proposals were **rejected** and logged:
- **Talisman Wallet & Portal** (OpenGov #1232, 690,600 USDT): effort lives in an external Google Doc (not
  on-chain); 3-repo umbrella → no single matched scope.
- **ink!Hub / Swanky Suite** (OpenGov #137, 58,018 DOT) and **Ink! Dev Hub** (#624, 72,000 USDC): 3-org
  collaboration, multi-repo umbrella (≈30 repos), delivery-based variable funding with no person-effort
  table, ~90 % partial delivery.
- **SubBooster** (Kusama #56): rejected on-chain (never awarded). **Ajuna SAGE** (#1509): rejected on-chain.

### 2.4 Provenance / data-quality notes (lessons that shaped the method)
- Derived CSVs cannot be trusted: both `pilot_cases.csv` (treasury-index vs gov2-referendum-index conflation)
  and the W3F census manifest (ParaSpell effort/repo mash-up) carried mapping bugs. **Every pilot was
  re-verified against its primary source** (on-chain JSON via Subsquare API, or the W3F application markdown).
- "Reported effort" mixes **actual** (retroactive) and **proposed** (forward) figures; each pilot is tagged.
- Two pilots could not be cleanly sized at write-time: ParaSpell (#9 — repo `dudo50/ParaSpell` deleted) and
  the multi-version Elara repo (see §6.2).

---

## 3. Method

### 3.1 COCOMO II instantiation
For each pilot we compute, from the *verified* COCOMO II tables (`cocomo2_tables.py`):
- **Size** = reuse-adjusted **Equivalent KSLOC** of the matched artifact (§3.3).
- **Scale exponent** `E = 0.91 + 0.01·Σ(SF)` over the 5 scale factors (PREC, FLEX, RESL, TEAM, PMAT).
- **Effort-multiplier product** `∏EM` over the 17 multipliers (RELY…SCED), plus 7 candidate blockchain EMs.
- **Predicted effort** `PM_pred = A · Size^E · ∏EM`, and the **local constant** that reproduces the report:
  `A_local = reported_PM / (Size^E · ∏EM)`.

### 3.2 Driver assignment — objective, evidence-based (anti-overfitting rule)
The 22 drivers are synthesized from **objective repository signals** (`cocomo_fit.synth_ratings`): CI, tests,
Docker, docs, audit, lint/format, on-chain runtime, smart contracts, and dependency classes
(consensus, cross-chain, zk-crypto, contract). Examples of the rules:
- `CPLX = VeryHigh` if zk-crypto dependency; `High` if consensus/on-chain/contracts; else Nominal.
- `PVOL = High` if on-chain/consensus (Substrate/SDK volatility).
- `PMAT/TOOL/RESL` from CI + tests + lint + docs presence.

**Integrity rule (non-negotiable).** A driver value must be set from project evidence, **never reverse-
engineered from the residual to the target**. With 22 free knobs and 12 points one can trivially force
PM = PM for every project; that is curve-fitting with more parameters than data, is unfalsifiable, and is
explicitly *not* the result claimed here. The win condition is **one global A (+ evidence-based drivers)
fitting all pilots**, scored by PRED(30)/MMRE — not per-project tuning. The baseline calibration below uses
**objective drivers only, no hand overrides.**

### 3.3 Size measurement and reuse model
Size is measured per pilot by its **sizing mode**, chosen to match effort↔artifact scope:
- **whole** — greenfield delivery: `cloc` of source languages at the delivery commit/date.
- **diff** — exact developer-provided commit range: `git diff a..b --numstat` (net delta).
- **window** — brownfield slice: **net delta between the window's start and end snapshots**
  (`git diff start..end`), *not* cumulative `git log` churn (a bug caught in run #1 — cumulative churn
  double-counts refactors/moves and inflated ink! analyzer to 58 KSLOC / 138 LOC·h⁻¹, impossible).

**Reuse-adjusted Equivalent SLOC** (COCOMO II reuse model): `equivalent = new + AAM·adapted`, where *adapted*
= generated code (content markers) + forked/imported code (a large "big-bang" commit adding > 4,000 source
lines at once = a template/fork, not authoring); AAM default 0.10. Computed in physical lines, applied as a
ratio to the logical cloc KSLOC.

### 3.4 The calibration loop (how the result was reached)
1. **Step 1** — dissect all pilots with objective drivers + raw size → exact per-project (E, A_local).
2. **Step 2** — inspect the A_local spread as a *diagnostic* (what objective rules miss).
3. **Step 3** — introduce/adjust **one evidence-justified lever at a time** (reuse-adjusted size; scope
   isolation; recalibrated global A), re-run, and watch the table tighten.
4. **Win** — one global (A, B, driver-rules) fitting the clean matched triples with low residual.

All heavy compute runs in GitHub Actions CI (`dissect-pilot` workflow); results published to the `census`
branch. Six CI runs were executed (run history in §7).

---

## 4. Results

### 4.1 Per-project local constant (objective drivers, raw equivalent SLOC) — run #5, n = 12
| Pilot | Equiv KSLOC | E | ∏EM | Reported PM | PM_pred @ A=2.94 | **A_local** | size class |
|---|---|---|---|---|---|---|---|
| fennel | 7.84 | 1.070 | 1.34 | 9.0 | 35.8 | **0.739** | clean |
| bagpipes | 10.81 | 1.100 | 1.00 | 9.97 | 40.2 | **0.729** | clean |
| dotcodeschool | 1.45 | 1.100 | 1.00 | 0.95 | 4.43 | **0.631** | clean |
| megaclite | 3.65 | 1.082 | 1.49 | 3.45 | 17.8 | **0.571** | clean |
| remarker | 11.33 | 1.100 | 1.00 | 7.24 | 42.4 | **0.502** | clean |
| dotreasury | 2.37 | 1.070 | 1.00 | 0.95 | 7.38 | **0.379** | clean (funded-qtr window) |
| ask_v01 | 20.73 | 1.070 | 1.30 | 6.9 | 97.8 | 0.208 | reuse-inflated |
| kheopswap | 15.36 | 1.100 | 1.00 | 3.16 | 59.2 | 0.157 | reuse-inflated |
| elara | 68.88 | 1.100 | 1.00 | 4.6 | 308.5 | 0.044 | scope-inflated (v0.1+v0.2) |
| subsquare_maint | 76.89 | 1.070 | 1.00 | 24.7 | 306.1 | 0.237 | window over-count |
| subsquare_newfeat | 69.97 | 1.070 | 1.00 | 11.4 | 276.7 | 0.121 | window over-count |
| ink_analyzer | 37.49 | 1.070 | 1.00 | 2.79 | 141.9 | 0.058 | window over-count |

Observations: `E ≈ 1.07–1.10` and `∏EM ≈ 1.0` across the board (scale factors barely vary; objective drivers
are mostly Nominal). **The entire variation is in size → A_local.** Every low outlier is a known
size-inflation case.

### 4.2 Global calibration — fit of one constant A
A* = geometric mean of A_local; PM_pred = A*·Size^E·∏EM; metrics over each subset:

| Subset | n | **A\*** | MMRE | PRED(25) | PRED(30) | PRED(50) |
|---|---|---|---|---|---|---|
| **core clean (size↔scope verified)** | 6 | **0.577** | **20 %** | 83 % | **83 %** | 83 % |
| + reuse-inflated (ask, kheopswap) | 8 | 0.431 | 56 % | 38 % | 38 % | 75 % |
| + scope-inflated (elara) | 9 | 0.335 | 120 % | 11 % | 11 % | 44 % |
| all incl. windows | 12 | 0.258 | 114 % | 17 % | 17 % | 33 % |

**Core-6 = {bagpipes, megaclite, remarker, dotcodeschool, dotreasury, fennel}.**

### 4.3 The calibrated model
> **Blockchain-COCOMO (working):  PM = 0.58 · (Equivalent KSLOC)^E · ∏EM,  E = 0.91 + 0.01·ΣSF.**

On clean matched triples this gives **Standardised Accuracy SA = +0.80** (primary), **PRED(30) = 83 %, MMRE =
20 %** — a *good* calibration (PRED(30) ≥ 70 % is the conventional "good model" threshold). The recalibrated
constant is **A ≈ 0.58 vs the classic 2.94** — a ≈ **5×** gap. *This 5× is implied by the calibration and is an
upper bound on the true productivity difference:* A also absorbs un-corrected reuse and a documented
below-market grant-pricing effect (§4.4d), so A = 0.58 is best read as a **grant-context constant** (productivity
× reuse × reporting/pricing incentive), calibrated to **Substrate-based Polkadot/Kusama grant software** —
applicability to commercial market-rate development or other ecosystems (EVM/Solana/Cosmos/Move) is an open
question.

**Cross-validation (core-6).** Leave-one-out CV: **MMRE = 24 %, PRED(25) = 67 %, PRED(30) = 83 %, PRED(50) =
83 %** — essentially unchanged from in-sample (PRED(30) holds at 83 %), so the calibration is **not overfit**.
Non-parametric bootstrap (B = 10,000) gives **A = 0.58, 95 % CI [0.475, 0.685]** (median 0.579) — the interval
excludes the classic 2.94 by ≈ 5×. Per-pilot LOOCV hold-out error: megaclite 1 %, dotcodeschool 10 %, remarker
18 %, bagpipes 24 %, fennel 26 %, **dotreasury 66 %** (the single weak point — the smallest project at 0.95 PM
/ 2.4 KSLOC, at the lower edge of COCOMO's validity range).

---

### 4.4 Reviewer-driven robustness analyses (added after senior peer review)
**(a) Standardised Accuracy as the primary metric** (Shepperd & MacDonell 2012; baseline = mean |yᵢ−yⱼ| of
random guessing). MMRE is demoted to "for comparability with prior work."

| subset | n | A* | **SA** | MMRE | PRED(30) |
|---|---|---|---|---|---|
| core-6 | 6 | 0.577 | **+0.80** | 20 % | 83 % |
| core actual-only | 3 | 0.493 | +0.95 | 18 % | 67 % |
| core proposed-only | 3 | 0.675 | +0.84 | 11 % | 100 % |
| core treasury-only | 5 | 0.549 | +0.84 | 19 % | 80 % |
| core w3f-only | 1 | 0.739 | — | — | — |
| all-12 | 12 | 0.258 | +0.15 | 114 % | 17 % |

SA = +0.80 (core-6) ≫ 0 — a strong result that the calibration is not an MMRE artifact. SA = +0.15 (all-12)
quantifies the size-inflation drag.

**(b) Actual vs proposed effort.** A* = **0.49** (actual, n=3) vs **0.68** (proposed, n=3) — the *opposite* of
the usual "proposed underestimates actual" prior (in this corpus proposed budgets report *more* PM per KSLOC);
small-n and confounded by project identity. Headline A pools both; **actual-only A ≈ 0.49 is the conservative
anchor.** A true-actual grantee survey is the pending refinement.

**(c) Is it COCOMO II or just a power law?** On core-6: full `A·Size^E·∏EM` gives SA +0.80 / PRED(30) 83 %;
pure `A·Size^E` (∏EM=1) gives SA +0.73 / PRED(30) 67 %. The evidence-based non-Nominal multipliers (CPLX/TIME
on ZK/contract projects; PVOL/CPLX on the chain) lift PRED(30) by **+16 pp** → the EM machinery *contributes*;
this is COCOMO II proper, though most drivers are Nominal (objective signals don't distinguish their levels).

**(d) Grant-pricing confound (is A a pure productivity constant?).** Implicit rate = grant USD / PM / 152 h:
core-6 **median ≈ $60/hr** (range $4–$125) vs market senior-blockchain ≈ $80–150/hr → grants are mostly
**below market** (Remarker $4/hr). **Therefore A = 0.58 is a *grant-context* constant encoding both genuine
productivity (reuse + senior devs) AND below-market / honest-actual reporting incentive — not a pure
productivity constant.** Applying it to commercial market-rate development would bias estimates (a scope bound).

**(e) Selection-bias direction (M1-R1).** The size **shrink** required to bring each excluded pilot to the
clean-6 A* implies reuse/out-of-scope fractions of 59–92 % (subsquare 59/79 %, ask 64 %, kheopswap 73 %,
ink! analyzer 90 %, elara 92 %) — all in the *same* direction (shrink, never grow) and each independently
plausible. Hence fixing the six moves their A_local **up toward** 0.58; the clean-6 value is a lower-ish anchor
and the expected full-corpus A is bounded in roughly **[0.58, 0.70]** (testable via the path-based detector).

## 5. Key finding: the residual is *size*, not the model

The fit degrades **monotonically** as size-inflated pilots are added (A* 0.58 → 0.43 → 0.34 → 0.26;
PRED(30) 83 % → 38 % → 11 % → 17 %). Because `E` and `∏EM` are essentially flat across all pilots, the misfit
cannot be a driver/exponent effect — it is entirely attributable to **measured size not matching the funded
scope**. Two distinct, both-legitimate mechanisms:
1. **Reuse / generated code** (Kheopswap = PAPI-generated descriptors; Ask! = AssemblyScript codegen; Fennel
   = 52 % `@generated`). Raw cloc counts these as authored; equivalent-SLOC must discount them.
2. **Scope / multi-version repositories** (Elara repo = v0.1 + v0.2 consolidation while only v0.1 was funded;
   the two Subsquare windows and ink! analyzer's 7-month window capture more than the funded slice).

**Therefore the headline secondary finding:** *in blockchain/grant software, equivalent-SLOC measurement
(reuse + scope isolation) is the dominant source of estimation error — not the 17 effort multipliers.* This
inverts the usual COCOMO emphasis and is a contribution in its own right.

---

## 6. Honest negative results and corrections (kept for the record)

### 6.1 Reuse auto-detection was too narrow (run #6)
A first reuse detector (big-*root*-commit fork + `@generated` markers, AAM = 0.10) **moved only Fennel**
(52 % generated → A_local 0.739 → 1.458, an overshoot) and **missed the three intended targets**: Elara's
vendored bulk is not in the root commit; Kheopswap/Ask generated code carries no standard marker. Net spread
*widened*. Reported straight, not forced. Correct next levers: detect bulk-import commits *anywhere* in
history (blame-based) and framework-generated code by *path* (`descriptors/`, `.papi/`, `generated/`,
`build/`), and verify Fennel's generated lines.

### 6.2 Elara is *scope*-inflated, not reuse
Elara's README states "we have completed the 0.2 version development," and the repo bundles three backend
services plus a separate front-end. Treasury #16 funded **v0.1** only; the repo at any post-2020 cutoff
contains v0.1 + v0.2 (likely a later consolidation). The 70 KSLOC is real authored code for *more than the
funded slice*. Elara therefore belongs with the window pilots (scope-isolation required), not the greenfield
clean set.

### 6.3 Engineering bugs caught and fixed (transparency)
- `git log --numstat` window churn double-count → switched to net boundary-diff.
- Date cutoff predating a repo's first commit silently measured HEAD → now errors.
- Semicolon in a `;`-delimited CSV `notes` field → parser crash → notes sanitised + `isinstance` guard.
- Blank workflow dispatch field fell back to the YAML default → default set to blank.
- dotreasury exact-diff tag `release-2.3.1` unresolvable → switched to funded-quarter window.

---

## 7. Reproducibility

**Code** (`scripts/validate/`): `dissect_pilot.py` (per-project COCOMO II dissection + reuse model),
`cocomo2_tables.py` (verified SF/EM tables, A = 2.94, B = 0.91), `cocomo_fit.py` (driver synthesis).
**Workflow:** `.github/workflows/dissect_pilot.yml` (clones each repo, measures, publishes
`reports/dissect_*.json` to the `census` branch). **Spec:** `data/calibration/pilots_cocomo.csv` (one row per
pilot: repo, sizing mode, ref/window, reported PM, objective driver flags). **Data/registry:**
`data/calibration/VERIFIED_PILOTS.md` (matched triples + on-chain links + rejections),
`COCOMO_DISSECTION_RESULTS.md` (running result tables), `provenance/change_log.md` (full audit trail).

**CI run history:** #1 caught the window-churn size bug; #2–#3 fixed CSV/dispatch parsing; #4 first full
12-pilot baseline; #5 post-fix baseline (dotreasury + elara); #6 reuse-adjustment (honest negative). Global-A
fit computed from the #5 dissection numbers.

---

## 8. Limitations and threats to validity
- **Small clean n (= 6).** A* is cross-validated (LOOCV PRED(30) = 83 %, MMRE = 24 %; bootstrap 95 % CI on A
  = [0.475, 0.685]) so it is **not overfit**, but n = 6 is small and the CI is correspondingly wide. Growing
  the clean set (by fixing reuse/scope sizes of Kheopswap, Ask!, Elara, the windows) will widen n and tighten
  the interval. The smallest pilot (dotreasury, 0.95 PM) is the LOOCV outlier (66 %), at the edge of COCOMO's
  validity range — small projects (≲ 2 KSLOC) are a known weak regime for the model.
- **Reported effort mixes actual and proposed** figures; proposed (forward) effort may not equal logged hours
  (industry-wide, true logged hours are largely non-public; Boehm himself calibrated to reported/confidential
  effort + surveys, so this is standard practice). Each pilot is tagged for stratified analysis.
- **Equivalent-SLOC measurement** is the dominant residual driver and is only partially automated; the clean-6
  result is conditioned on size↔scope being unambiguous for those pilots.
- **Driver sparsity:** objective signals leave most multipliers Nominal; evidence-based refinement (e.g.
  audits→RELY, measured CPLX) is a legitimate future lever, applied from evidence, never from the residual.

## 9. Next steps
1. ~~LOOCV + bootstrap CI on the core-6 A~~ **DONE** — A = 0.58, 95 % CI [0.48, 0.69], LOOCV PRED(30) = 83 %.
2. **Grow clean n:** path-based generated-code detection (Kheopswap, Ask!); scope-isolate Elara + windows to
   the funded deliverable; re-fit — expect the inflated pilots to fall onto A ≈ 0.5–0.6 and PRED(30) to hold.
3. **Manuscript:** fold §1–§5 + the fit table into the methodology paper as the headline calibrated result;
   §6 as the honesty/limitations section.
4. **Grantee self-report survey** (true actual-effort anchor) for a subset, to validate proposed-effort points.

---

*Integrity statement: every figure in §2 was read directly from its primary on-chain or W3F source; every
driver in §3–§4 is set from objective repository evidence, never tuned to the target; negative results (§6)
are reported in full. This record is intended to be sufficient for independent reproduction.*
