# Change Log — append-only audit trail

Newest first. Each entry records what changed and why, for reproducibility and review.

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
