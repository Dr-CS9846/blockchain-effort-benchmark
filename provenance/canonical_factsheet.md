# Canonical Fact Sheet — single source of truth for locked numbers

Any document disagreeing with this table is wrong by definition and must be corrected to match it.
Every number here is produced by an executed script in this repo, cited by path.

_Last updated: 2026-05-30_

| Item | Locked value | Produced by |
|------|--------------|-------------|
| Canonical title | Proof of Effort — A Blockchain-Aware Extension of COCOMO II with Generative Data Augmentation | — |
| Calibration set | W3F verified-delivery grants, n = 13, real costs $10k–$50k | `data/calibration/w3f_benchmark_dataset.csv` |
| Effort definition | Person-Months ≡ FTE × Duration (declared) | verified structural finding |
| Honest baseline — in-sample | MMRE 26.7%, PRED(25) 53.8% | `scripts/validate/calibrate_bc_cocomo.py` |
| Honest baseline — LOOCV (unbiased) | **MMRE 41.1%, PRED(25) 30.8%, PRED(30) 46.2%** — FAILS Conte | `reports/bc_cocomo_results.json` |
| Reproducibility | identical on re-run (deterministic, closed-form MLE) | re-run verified 2026-05-30 |
| SLOC infeasibility (old proxy) | r(SLOC, PM) = −0.23 — a measurement artifact (repo-KB/10), to be re-tested with cloc | to re-measure |
| Corrected model | PM = A · KSLOC^E · Duan, size & effort measured independently | `scripts/validate/calibrate_size_effort.py` |
| Engine validation (synthetic dry-run) | recovers E ≈ 0.84, passes Conte, deterministic — code-validation only, NOT a finding | `scripts/validate/calibrate_size_effort.py` |
| Acceptance criteria | Conte et al. (1986): MMRE < 25% AND PRED(25) ≥ 75% | — |
| Repo role | Reproducibility backbone (Option B) | this repo |

## Explicitly NOT yet established (do not claim)
- A measured size→effort result on real data (awaits CI measurement run).
- Any QI-GAN augmentation result (currently unbacked — see Provenance Trace).
- n ≥ 30 statistical results (awaits dataset expansion).
