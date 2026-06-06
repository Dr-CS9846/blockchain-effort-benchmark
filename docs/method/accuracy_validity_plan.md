# Accuracy & Validity Plan

How we pursue accuracy without fooling ourselves. Agreed approach: **both, staged** —
lock methodological rigor first (Stage 1), then squeeze the best *honest* accuracy the
data legitimately supports (Stage 2), inside leakage-proof limits.

## What "perfection" means here

Perfection lives in the **method**, not the metric. A near-perfect MMRE on real effort
data is a red flag for leakage, overfitting, or a circular target — not a triumph — and
reviewers read it that way. We therefore optimise rigor and report whatever honest
accuracy results.

### Realistic, grounded target bands
- Uncalibrated COCOMO on real data: MMRE ≈ 1.0–2.8, PRED(25) ≈ 0% (the floor).
- Calibrated / enhanced COCOMO in the literature: **MMRE ≈ 0.30–0.52, PRED(25) ≈ 50–70%**.
- Conte (1986) "good" bar: **MMRE < 25% AND PRED(25) ≥ 75%** — an excellent ceiling many papers miss.
- **Our aim:** treat the Conte bar as a ceiling we'd be glad to touch; treat **MMRE 25–40% / PRED 55–75% with SA clearly > 0** as a legitimate, publishable result if honestly obtained and beating baselines.

## Metric suite (implemented in `scripts/validate/metrics.py`)
Never MMRE alone — MMRE is biased toward underestimation (Shepperd & MacDonell 2012;
Port & Korte 2008). Every result reports:
- **MMRE, MdMRE, PRED(25), PRED(30)** — legacy comparability.
- **MAE** — unbiased absolute error.
- **SA = 1 − MAE/MARP0** — Standardized Accuracy vs a random-guess baseline (the field's
  recommended measure). SA > 0 = better than random; ~0 = no better than guessing.
- **Cliff's δ** — non-parametric effect size for model-vs-model comparison.

## Stage 1 — lock the rigor (must all hold before Stage 2)
1. **Correct target:** measured effort (git active person-months), not circular planned PM.
2. **Independent size signal:** measured KSLOC (and, as a refinement, logical SLOC / contract count) — not repo bytes.
3. **Adequate n:** expand verified data to **n ≥ 30** before drawing model conclusions.
4. **Leakage-proof validation:** LOOCV now; **nested CV** for any hyperparameter so tuning never touches the test fold; then an external hold-out.
5. **Full metric suite + baselines:** report the suite above against naive baselines (mean, FTE-only, analogy).
6. **Pre-registered thresholds:** success bands fixed *before* seeing results (this document).
7. **Provenance:** every number in `claims_ledger.md`, reproduced via `make verify`.

## Stage 2 — honest accuracy levers (only inside the guardrails)
Each lever yields *modest, legitimate* gains; none should produce near-perfect numbers.
- Better size measurement (logical SLOC, function-point proxy, contract count).
- Blockchain-specific effort multipliers / scale factors, added one at a time and justified.
- Domain segmentation (DeFi vs infra vs tooling) where n permits.
- Principled outlier diagnostics (Cook's distance) — *flagged and reported*, never silently dropped to lower MMRE.
- Local/analogy estimation as an alternative model, compared fairly.

## Red lines (never cross)
- No tuning, feature choice, or outlier removal informed by the test fold.
- No reporting a number that `make verify` can't reproduce.
- No dropping data points just because they raise MMRE.
- If accuracy suddenly looks near-perfect, **stop and hunt for leakage** — treat it as a bug until proven otherwise.

## Stop rule
A result is "done" when: the rigor checklist passes, the metric suite (incl. SA and effect
size vs baselines) is reported honestly, it reproduces, and the limitations are stated —
regardless of where MMRE lands. That is the standard that survives grant, publication, and defense.
