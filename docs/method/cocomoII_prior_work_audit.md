# Audit of the previously-identified COCOMO II variables (deep re-verification)

Scope: re-verify every COCOMO II constant, table value, and variable definition used in the prior
work (`scripts/04_build_cocomo_dataset.py`, `04_cocomo_dataset/*`) against the **official COCOMO II
Model Definition Manual v2.1 (2000)**, and flag anything to redo before Phase-2 implementation.

## A. VERIFIED CORRECT (no errors) — against the Manual
- **Constants:** `A = 2.94`, `B = 0.91` — verbatim in the Manual (COCOMO II.2000). ✓
- **Formula:** `Effort = A·Size^E·∏EM`, `E = B + 0.01·ΣSF`. ✓
- **All 5 Scale-Factor value tables** (PREC/FLEX/RESL/TEAM/PMAT, VL→XH) — **exact** match to
  Manual Table 10 (e.g. PREC 6.20/4.96/3.72/2.48/1.24/0.00; PMAT 7.80/6.24/4.68/3.12/1.56/0.00). ✓
- The 17 Effort-Multiplier tables (RELY…SCED) — now extracted and verified from Manual Tables
  17–34 and stored in `scripts/validate/cocomo2_tables.py` (single source of truth). Nominal=1.00
  for every EM. ✓

➡ **The COCOMO numbers in the prior work contain no errors.** The issues below are in the prior
*implementation/methodology*, which Phase 2 redoes.

## B. FLAWS TO REDO in the prior implementation
1. **Ground-truth PM was the PLANNED figure** (`actual_effort_pm` = FTE × duration from the
   application). This is the central flaw — planned ≠ delivered effort. **FIXED** in Phase 1:
   measured PM bracket (PM_low/mid/high, Boehm 152h), validated.
2. **Size was ESTIMATED, not measured** (`estimate_size_ksloc` = base{level} + pm×0.5, "~0.5
   KSLOC/PM"). Crude and partly circular (uses PM to estimate size). **FIX:** use cloc-measured
   delivered source KSLOC (generated-excluded) from Phase 1.
3. **The 17 standard EMs were never applied** (`em_product = 1.0`, "not enough info"). The prior
   model used only 5 SF + 7 blockchain EMs. **FIX:** apply all 17 with the verified values +
   objective synthesis (Nominal default where no signal) — per the keep-all-22 directive.
4. **Rating heuristics used weak grant-METADATA proxies, not repo signals:** PREC←W3F level,
   RESL←milestone_count, TEAM←fte/team ratio, FLEX≡N, PMAT≡N. These are arbitrary and not
   objective. **FIX:** synthesize ratings from repository artifacts (CI/tests/Docker, deps,
   languages, audit files, consensus/XCM signals) per `cocomoII_synthesis_spec.md`.
5. **Blockchain EM values are unvalidated guesses** keyed to metadata (DC←level, EM_AUD←cost>$30k,
   EM_NODE←milestones≥4, EM_GAS≡0.95). **FIX:** derive from objective repo signals; ground/refit
   the magnitudes rather than assert them.

## C. NEW design issue found during the audit (must resolve before fitting)
**Double-counting between the 7 blockchain EMs and the 17 standard EMs.** Several blockchain EMs
overlap standard ones and would multiply the same effort twice:
- `BC_DC` (decentralization/consensus complexity) ⟷ standard **CPLX**
- `BC_EM_AUD` (audit/security) ⟷ standard **RELY**
- `BC_EM_NODE` (node infra) ⟷ **CPLX/PVOL**
- `BC_EM_GAS` (gas/exec) ⟷ **TIME**
**Resolution rule (to adopt):** each blockchain EM must capture only the effort NOT already
captured by its standard counterpart — i.e. define the blockchain EMs as **orthogonal increments**,
OR map the blockchain concept onto the standard EM's rating (the Manual's own approach: TIME→gas,
RELY→audit) and keep the blockchain EM only for genuinely new dimensions (e.g. cross-chain). We
will choose ONE representation per concept and document it, to avoid inflation.

## D. Minor
- `BEM` is described inconsistently ("Blockchain Effort" vs "Blockchain Experience" Multiplier) —
  fix the definition and name.

## Verdict
COCOMO II constants and tables: **verified correct, no minute errors** (now pinned in
`cocomo2_tables.py`). Phase-2 work is to (i) feed the **measured** PM and **measured** KSLOC,
(ii) apply **all 22** variables with **objective repo-based synthesis** and Nominal defaults,
(iii) **resolve blockchain↔standard EM double-counting**, and (iv) calibrate `A` so predicted PM
reproduces measured PM. The synthesis design is in `cocomoII_synthesis_spec.md`.
