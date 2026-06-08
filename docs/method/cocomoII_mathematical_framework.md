# Mathematical framework for the blockchain COCOMO II model
### (identifiability, necessity, sufficiency, and calibration — everything proven, nothing asserted)

Goal: a COCOMO II model for blockchain in which **every constant and every variable is justified
mathematically/empirically**, so no decision must be revisited. We keep all COCOMO II variables;
the *role* of each (active driver, redundant, inert-Nominal, or a needed new factor) is decided by
provable properties of the model on our measured data, not by choice.

## 1. Model and log-linearisation
Multiplicative COCOMO II Post-Architecture:
```
PM = A · S^E · ∏_{i=1..17} EM_i · ∏_{k=1..K} BCEM_k ,    E = B + 0.01 · Σ_{j=1..5} SF_j
```
Taking logs (the natural estimation space; errors are lognormal — standard for effort models):
```
y = ln PM
y = ln A + (B + 0.01·Σ_j SF_j)·ln S + Σ_i ln EM_i + Σ_k ln BCEM_k          (1)
```
Define per project p:
- size term `s_p = ln S_p`
- scale contribution `g_p = (0.01·Σ_j SF_{j,p})·ln S_p`  (SFs act as an interaction with size)
- multiplier columns `x_{v,p} = ln(m_{v,p})` for every effort multiplier v (standard or blockchain)

Then (1) is **linear**:
```
y_p = ln A + B·s_p + g_p + Σ_v x_{v,p} + ε_p ,   ε ~ N(0, σ²)               (2)
```
Constants `A, B` and all multiplier magnitudes `m_v` are FIXED (verified COCOMO II.2000 tables in
`cocomo2_tables.py`); the only free scalar is `ln A` (calibration). This is the crucial structural
fact: COCOMO is **not** a free 22-coefficient regression — it is a fixed transform plus a single
calibrated constant. The mathematics below respects that.

## 2. Variable synthesis as measurable functions
Each variable's rating is a deterministic, reproducible function of repository/grant signals,
`rating_v(p) = f_v(signals_p)`, mapped to its published multiplier `m_{v,p}` (Nominal ⇒ 1.0 when
no defensible signal). `f_v` are pre-registered and unit-tested. This makes every `x_{v,p}` an
objective measured quantity — a prerequisite for any of the proofs below.

## 3. REDUNDANCY ("overdoing") — identifiability test
Form the design matrix `X = [s, g_SF-components, x_{v}...]` over the n=63 projects.
- **Pairwise:** redundancy between two variables u,v ⇔ `|corr(x_u, x_v)| → 1`.
- **Multivariate:** **Variance Inflation Factor** `VIF_v = 1/(1−R²_v)` (R²_v from regressing x_v on
  the others); `VIF_v ≳ 5–10` ⇒ x_v not separately identifiable.
- **Global:** rank and **condition number** κ(XᵀX); near-rank-deficiency ⇒ collinear block.
**Decision rule (proof of double-counting):** if a blockchain EM's synthesized column is collinear
with a standard EM's (e.g. BC_DC vs CPLX, both from the consensus signal), they are *mathematically
non-separable* — we then represent that effort **once** (keep the canonical COCOMO variable; the
blockchain EM is dropped or redefined to the orthogonal residual). This converts the
"map-onto-standard" intuition into a theorem about the data.

## 4. NECESSITY ("is it OK / does it earn its place") — ablation test
With A calibrated, compute out-of-sample accuracy under leave-one-out CV: Standardised Accuracy
`SA = 1 − MAE/MAE_{p0}` (vs random baseline; Shepperd & MacDonell — MMRE is biased), plus MMRE,
PRED(25/30). For each variable v, compare the full model to the model with v forced Nominal:
```
Δ_v = SA(full) − SA(without v)
```
- `Δ_v > 0` beyond noise (bootstrap CI / effect size) ⇒ v is **necessary** (active driver).
- `Δ_v ≈ 0` ⇒ v is **inert** on this data: retained at Nominal per the keep-all directive, but
  flagged "non-contributing (Δ_v = …)" — the claim is then quantified, not hand-waved.

## 5. SUFFICIENCY ("is anything missing") — residual-structure test
Residuals `r_p = y_p − ŷ_p`. If the variable set is sufficient, `r` is unstructured (white): no
candidate signal explains it. Test by regressing `r` on each candidate (and unused blockchain
signals: cross-chain, ZK, formal-verification, …) and on fitted values; significant structure
(e.g. corr, or a Ramsey/RESET-style check) ⇒ **insufficient** ⇒ a new driver is warranted —
this is the *only* admissible, evidence-based way a brand-new blockchain EM enters the model.

## 6. CALIBRATION of A (derived, not chosen)
Under (2) with fixed magnitudes, define the per-project COCOMO prediction without A:
`q_p = B·s_p + g_p + Σ_v x_{v,p}`. Then `y_p = ln A + q_p + ε_p`. The **MLE of ln A** under
`ε ~ N(0,σ²)` is the closed-form OLS intercept:
```
ln Â = mean_p ( y_p − q_p ) ,     σ̂² = var_p ( y_p − q_p )                  (3)
```
with a (1−α) CI `ln Â ± z_{α/2}·σ̂/√n`, and Duan smearing `exp(σ̂²/2)` for unbiased back-transform.
B may be promoted to a second free parameter and tested by a likelihood-ratio test against B=0.91;
we keep B=0.91 unless the LRT rejects it (documented). Thus A (and any B move) is *proven* by MLE,
not asserted.

## 7. What is already proven
- A=2.94, B=0.91, the 5 SF tables and the 17 EM tables: verified verbatim against the COCOMO II
  Model Definition Manual (Tables 10, 17–34) and pinned in `cocomo2_tables.py`.
- The estimator (3) is the exact lognormal MLE (deterministic, reproducible).

## 8. Execution order (each step outputs evidence, not opinion)
1. Implement variable synthesis `f_v` for all 22 + candidate blockchain EMs (objective, unit-tested).
2. Build X over n=63; run §3 (redundancy: corr/VIF/κ) ⇒ identifiable variable set; resolve every
   blockchain↔standard overlap by proof.
3. Calibrate A via (3); run §4 (necessity: per-variable ablation ΔSA + CI).
4. Run §5 (sufficiency: residual diagnostics) ⇒ add a new driver only if residuals demand it.
5. Report the final model with: each variable's role + the statistic that proves it; A with CI;
   LOOCV MMRE/PRED/SA; sensitivity across the PM bracket (PM_low/mid/high).

**Outcome:** the blockchain-EM question ("OK / insufficient / overdoing") is answered per variable
by §3–§5 with numbers, and A by §6 — so nothing is left to return and correct.
