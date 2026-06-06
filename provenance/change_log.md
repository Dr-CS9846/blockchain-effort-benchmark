# Change Log — append-only audit trail

Newest first. Each entry records what changed and why, for reproducibility and review.

## 2026-05-30 (robust repo/commit resolution)
- Rebuilt `scripts/extract/resolve_repos_online.py` to be robust: it CLONES the W3F delivery + grants repos (reliable in CI; no rate limits / no fragile filename guessing), fuzzy-matches each project to its milestone-delivery file(s), and extracts the delivered repo URL + commit (/tree|/commit/<sha>); application repo links as fallback. Writes `reports/resolved_repos.csv` for human review; `--fill` writes `projects_manifest.online.csv`. Matcher + parsers unit-tested offline.
- Reason for rebuild: live delivery filenames are irregular (e.g. AgriDot's is NOT `AgriDot-milestone_1.md` — that path 404s), so URL-guessing missed most projects. Cloning + directory fuzzy-match fixes this and scales to 150.
- CI (`measure.yml`): resolve now runs with `--fill`; the rolling snapshot adopts the resolved repos+commits and measures at the PINNED commit. `main`'s manifest changes only after human review of `reports/resolved_repos.csv`.
- `.gitignore`: added `resolve_cache/`, `projects_manifest.online.csv`.

## 2026-05-30 (accuracy rigor — Stage 1)
- Added `scripts/validate/metrics.py`: canonical metric suite — MMRE, MdMRE, PRED(25/30), MAE, and **Standardized Accuracy (SA) vs a random baseline (MARP0)**, plus Cliff's delta. Unit-tested (SA=1 on perfect, ~0.39 on mean-guess, negative when worse than random).
- Wired the suite into `calibrate_size_effort.py` (now reports MAE + SA alongside MMRE/PRED). Verified on synthetic measured data.
- Added `docs/method/accuracy_validity_plan.md`: agreed "both, staged" approach — methodological rigor first, honest accuracy second; grounded realistic target bands; anti-leakage red lines. Rationale: MMRE alone is biased (Shepperd & MacDonell); near-perfect accuracy on real effort data signals leakage, not excellence.
- Wired SA/MAE into `calibrate_bc_cocomo.py` too (both models now report on equal modern footing). Verified on real data: LOOCV MMRE 41.1%, PRED25 30.8%, MAE 2.70, **SA 0.463** (baseline is ~46% better than random — informative even though it fails the strict Conte bars).
- Added `scripts/validate/nested_cv.py`: reusable leakage-proof nested-LOOCV tuning harness, demonstrated on an Analogy-Based Estimation (k-NN) baseline whose k is tuned by inner CV. Passed a behavioural leakage test (corrupting a held-out point does not change its own prediction). Note: the OLS calibrators have no tuned hyperparameters, so plain LOOCV is already unbiased for them; nested CV is the guardrail that activates for any Stage-2 tuned model.

## 2026-05-30 (source→claim chain)
- Added `provenance/claims_ledger.md`: every published number traced to script → data → raw source, with reproduced?/frozen? status. Names the open lineage gaps explicitly.
- Added `scripts/extract/freeze_raw.py`: snapshots verbatim raw W3F application + delivery sources into `data/raw/` with `RAW_MANIFEST.csv` (sha256, captured_at). Logic unit-tested offline. Wired into Makefile (`make freeze`, in `all`) and CI (freezes + commits `data/raw/` to rolling).
- `data/raw/` declared as committed evidence (not git-ignored).
- Assessment recorded: baseline chain (C1–C4) is reproduced (make verify MATCH) but not yet frozen at raw source; measured size→effort (C6) awaits CI. Audit-grade reached when data/raw frozen + C6 produced + promoted to a tag.

## 2026-05-30 (Phase 2 + datasheet)
- Added one-command pipeline: `Makefile` (targets: setup/baseline/resolve/measure/calibrate/figures/quickcheck/all/verify/clean) + portable `run_all.sh`. `.RECIPEPREFIX` used for portability.
- Added `scripts/validate/make_figures.py` (deterministic; matplotlib guarded). Tested: `make quickcheck` reproduces the baseline + writes reports/figures/baseline_actual_vs_pred.png; `make verify` → MATCH (MMRE 0.4109, PRED25 0.3077, bit-stable).
- Added `docs/DATASHEET.md` on the Gebru et al. *Datasheets for Datasets* (CACM 2021) 7-section standard.
- Switched all forced pushes to `--force-with-lease` (with prior fetch); plain `--force` banned. Codified in release_policy.md.
- Fixed 00_check_environment.py to find the manifest under data/calibration/; `setup` made non-gating.

## 2026-05-30 (later) — governance + Action 2 start
- Added `provenance/release_policy.md`: the living benchmark is gated — CI publishes only to a non-authoritative `rolling` branch; published claims live in reviewed, **tagged** releases (cite tags + Zenodo DOI versions, never `main`).
- Updated `.github/workflows/measure.yml` so CI commits to `rolling`, never `main`.
- Extended `scripts/extract/resolve_repos_online.py` to parse W3F **milestone-delivery records** (authoritative source for the delivered repo AND the pinned commit); delivery sources outrank application sections. Unit-tested.
- Manifest: confirmed `Societal -> sctllabs/societal-node` (from its delivery record); cleared the prior wrong `bright_treasury` auto-suggestion (tutorial repo). Remaining repos+commits to be resolved authoritatively by the CI resolver run.

## 2026-05-30
- Restructured the repository into the **trimmed layered architecture** (calibration / provenance / docs / reports + external_holdout), declaring its role as a **reproducibility backbone (Option B)**.
- Applied the **decision rule** to every artifact → `provenance/source_map.md`.
- Excluded blockchain *performance* benchmark suites (Blockbench/TrustedBench) from the data layers; they remain related-work context only.
- Mirrored the real verified dataset and the honest baseline calibration into the repo so results are reproducible from within it.
- Updated `.github/workflows/measure.yml` to the layered paths; outputs routed to `data/calibration/` and `reports/`.
- Established `canonical_factsheet.md` as the single source of truth.

## Earlier (recorded in thesis docs)
- Reproducible honest baseline established: LOOCV MMRE 41.1%, PRED(25) 30.8% (FAILS Conte) — `calibrate_bc_cocomo.py`.
- Structural finding: PM ≡ FTE × Duration (effort defined, not measured).
- Provenance trace: headline A=2.1143 / QI-GAN / 22.9% results not reproducible from the folder (no code, no data, harness unrun).
- Measurement toolkit built + unit-tested; GitHub repo + Actions engine created.
