# Source Map — every artifact classified by the decision rule

**Decision rule.** *Effort → calibration. Pipeline → provenance. Context/system behaviour → benchmark/holdout. None of these → archive.*
This map is the panel-facing answer to "what is evidence, and what is illustration?"

_Last updated: 2026-05-30_

## A. Inside this repository (the reproducibility backbone)

| Artifact | Role | Classification | Evidence of |
|----------|------|----------------|-------------|
| `data/calibration/w3f_benchmark_dataset.csv` | Real, delivery-verified W3F effort data (n=13, real costs) | **CALIBRATION (evidence)** | effort ground truth |
| `data/calibration/projects_manifest.csv` | Scalable input defining the calibration set (13 → 150) | **CALIBRATION (evidence)** | dataset definition |
| `data/calibration/measurements.csv` | CI-produced measured size + git-effort, per pinned commit | **CALIBRATION (evidence)** | measured effort & size |
| `scripts/extract/measure_repos.py` | clone → cloc → git person-months | **PROVENANCE (pipeline)** | how measurements are produced |
| `scripts/extract/resolve_repos_online.py` | resolve delivered repos from public records | **PROVENANCE (pipeline)** | source resolution |
| `scripts/extract/resolve_repos.py` | local-stub resolver (helper) | **PROVENANCE (pipeline)** | source resolution |
| `scripts/validate/calibrate_size_effort.py` | `PM = A·KSLOC^E`, LOOCV, Conte verdict | **PROVENANCE (pipeline)** | how the model is fit & tested |
| `scripts/validate/calibrate_bc_cocomo.py` | honest ESF baseline on the real set | **PROVENANCE (pipeline)** | reproducible baseline |
| `scripts/validate/00_check_environment.py` | environment / tool check | **PROVENANCE (pipeline)** | runnability |
| `.github/workflows/measure.yml` | cloud CI that reruns everything | **PROVENANCE (pipeline)** | reproducibility engine |
| `reports/bc_cocomo_results.json` | locked honest baseline (LOOCV MMRE 41.1%, PRED25 30.8%) | **CALIBRATION result** | the actual, reproducible result |
| `reports/bc_cocomo_params.json` | locked baseline parameters | **CALIBRATION result** | the fitted model |
| `data/external_holdout/` | ESP / audit-mined sources (when added) | **HOLDOUT (context)** | generalisation, NOT calibration |
| `docs/method/WORKFLOW.md`, `docs/BOOTSTRAP.md` | how to run / publish | **DOCS** | method |
| `provenance/*` | this map, fact sheet, change log | **PROVENANCE (audit)** | governance |

## B. Broader thesis corpus (mapped, not all imported)

| Artifact (in 5. Pipeline / sibling folders) | Classification | Disposition |
|---|---|---|
| `04_cocomo_dataset/` real CSV + scripts + results | **CALIBRATION + PROVENANCE** | mirrored into this repo (source of truth) |
| Ethereum pilot (`4. Ethereum/`, n=5, proxy effort) | **ILLUSTRATION (not calibration)** | keep as illustrative only; never feed calibration |
| QI-GAN docs / claimed augmentation results | **UNBACKED** | archive until code + data make them reproducible (see Provenance Trace) |
| Strategy / feasibility / provenance / foundation memos | **PROVENANCE (audit trail)** | keep in thesis docs; summarised here |
| Blockbench / TrustedBench (external suites) | **CONTEXT only** | `docs/related_work/` citation — NOT a data layer |

## C. Excluded by the rule
- Performance-benchmark workloads as calibration data — excluded (measure system speed, not effort).
- Regenerable intermediates (`repo_candidates*.csv`, `*.suggested*.csv`, caches) — git-ignored, never evidence.
- Any figure or demo that proves neither effort, nor the pipeline, nor context — archive.
