# COCOMO II Conformance Audit — are we doing it "in the classical sense"?

**Purpose.** Map every element of the canonical COCOMO II Post-Architecture model (constants,
scale factors, effort multipliers, size model, exponent, calibration procedure, schedule
equation) to its exact status in this project, so that *nothing* canonical is silently missed.
Reference: Boehm, Abts, Brown, Chulani, Clark, Horowitz, Madachy, Reifer, Steece,
*Software Cost Estimation with COCOMO II* (2000); *Model Definition Manual v2.1*.

> Bottom line up front: the canonical machinery is implemented and **verified exact**
> (`scripts/validate/cocomo2_tables.py`). The full fixed-weight model has been **run and reported**
> (`cocomo_fit.py`) — it does not fit blockchain effort out of the box (SA<0). Our PM=PM results
> come from **local calibration**, which is *prescribed by COCOMO II*, not a departure from it.
> The one thing still pending — a full 22-driver local calibration — is blocked only by sample
> size (n=52; Boehm used 161) and is the precise reason for the W3F data expansion.

---

## 1. The canonical equations (what "classical COCOMO II" means)

**Effort (Post-Architecture):**
&nbsp;&nbsp;**PM = A · Size^E · ∏ᵢ EMᵢ**
**Exponent:**
&nbsp;&nbsp;**E = B + 0.01 · Σⱼ SFⱼ**   (j = 1..5 scale factors)
**Schedule:**
&nbsp;&nbsp;**TDEV = C · PM^(D + 0.2·(E − B))**,  C = 3.67, D = 0.28
**Constants (COCOMO II.2000):** A = 2.94, B = 0.91.

---

## 2. Element-by-element conformance

| # | Canonical element | Manual ref | Status here | Notes / justification |
|---|---|---|---|---|
| 1 | Effort form PM = A·Size^E·∏EM | §2 | **Implemented & honoured** | `cocomo_fit.py` computes exactly this; local-cal uses its log-linearisation ln PM = ln A + E·ln Size + Σ ln EM. |
| 2 | A = 2.94 | "COCOMO II.2000" | **Verified exact** (`cocomo2_tables.py`) | Used as-is in fixed-weight run; **re-estimated as local A** in calibration — *sanctioned by Boehm Ch.4*. |
| 3 | B = 0.91 | §2 | **Verified exact** | Fixed-weight uses B+0.01ΣSF; local-cal **fits the exponent** (e.g. on-chain 0.92 — within Boehm's empirical 0.91–1.23 envelope). |
| 4 | 5 Scale Factors PREC, FLEX, RESL, TEAM, PMAT | Table 10 | **Values verified exact**; **applied** in fixed-weight run | In local-cal the SF are candidate drivers; data did not retain them — reported, not hidden. |
| 5 | 17 Effort Multipliers (RELY…SCED) | Tables 17–34 | **All 17 values verified exact**; **applied** in fixed-weight run | Fixed-weight: EMs as published. Local-cal: forward-selected subset with fitted weights (redundancy of several EMs *proven* via VIF). |
| 6 | Nominal EM = 1.00 | Tables | **Verified** (self-check asserts) | Nominal is the default where a driver cannot be objectively synthesised. |
| 7 | Exponent assembly E = B+0.01ΣSF | §2 | **Implemented** (`exponent_E`) | Used in fixed-weight; local-cal estimates E directly. |
| 8 | Size = KSLOC (new code) | §2 | **Implemented** | `ksloc_code` = hand-authored logical SLOC; generated/large files excluded (evidence-based). |
| 9 | **Reuse / equivalent SLOC** (AAF, SU, AA, UNFM) | §2.2 | **NOT yet implemented** | We use authored-code KSLOC and exclude generated code, but do **not** compute reuse-adjusted equivalent SLOC. *Gap to close* (see §4). |
| 10 | Local calibration of A (and weights) | **Ch. 4** | **Implemented** (`cocomo_localcal.py`) | OLS in log space = lognormal MLE of A; this IS the documented procedure. |
| 11 | Bayesian weight calibration | Ch. 4 | **NOT yet** (needs n) | Planned for the full-driver calibration once n≥~100. |
| 12 | Schedule equation TDEV | §2 | **Out of scope (effort-only)** | We estimate effort (PM); TDEV is downstream and not claimed. State explicitly in writeup. |
| 13 | Accuracy standard PRED(.30) ≥ 0.70, MMRE | Ch. 5 | **Adopted as target** | Reported every run (PRED25/PRED30/MMRE) + SA (Shepperd & MacDonell 2012) which is bias-robust. |
| 13b | Validation by cross-validation | Ch. 4–5 | **Implemented** (LOOCV) | Every SA/PRED is leave-one-out, not in-sample. |
| 14 | Blockchain EM extension (COCOBLOCK) | (our contribution) | **Specified & tested** | 7 blockchain EMs; on current data proven non-identifiable/redundant — reported honestly, re-tested after expansion. |

---

## 3. The honest distinction: classical fixed-weight vs locally-calibrated

- **Classical fixed-weight COCOMO II** (A=2.94, B=0.91, Boehm's 22 published weights): implemented in
  `cocomo_fit.py`, **run**, result LOOCV SA < 0 on blockchain effort. This is a *finding*, not PM=PM.
- **Locally-calibrated COCOMO II** (Boehm Ch. 4 procedure — fit A and, with enough data, the weights to
  the local environment): implemented in `cocomo_localcal.py`; yields the PM=PM results
  (on-chain size law SA 0.77). **This is still COCOMO II** — calibration to environment is the method's
  own prescription, exactly as Boehm calibrated A to TRW's 161 projects.

We must phrase claims accordingly: *"a locally-calibrated COCOMO II model for blockchain"* — never imply
the out-of-the-box constants reproduce blockchain effort (they don't, and we say so).

## 4. What to close before the full canonical claim (gated on W3F expansion)

1. **Reuse-adjusted equivalent SLOC** (#9): implement AAF/SU/AA/UNFM so Size is canonical, not raw KSLOC.
2. **Full 22-driver local calibration** (#5, #11): with n≥~100, calibrate the complete A·Size^E·∏EM
   (5 SF + 17 EM + blockchain EMs) by Boehm's documented regression/Bayesian procedure — the
   Boehm-faithful, classical-sense result.
3. **Re-test the blockchain EMs** for identifiability on the expanded set.
4. Keep reporting fixed-weight vs locally-calibrated side by side (intellectual honesty).

**Conclusion.** The maths is secure in the sense that every canonical constant/table is verified and the
canonical equation is implemented and run; we are *transparent* that PM=PM comes from COCOMO II's own
local-calibration path, and we have a concrete, gated plan (reuse model + full-driver calibration on the
expanded W3F set) to deliver the full classical-sense result without overfitting.
