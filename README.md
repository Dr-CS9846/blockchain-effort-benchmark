# Blockchain Software Effort Benchmark — Reproducibility Backbone

A scientifically governed evidence repository for the PhD research
*"Proof of Effort — A Blockchain-Aware Extension of COCOMO II."*

**Declared role: a reproducibility backbone (Option B).** It stores the scripts,
datasets, locked outputs, and provenance needed to reproduce the calibration end to
end. Every data point traces to a public commit; nothing is hand-entered.

> Scope discipline: this repo is **not** the whole thesis. It is the infrastructure
> for the parts of the thesis it can genuinely support — effort calibration and its
> reproducibility. Blockchain *performance* benchmark suites (e.g. Blockbench,
> TrustedBench) measure system throughput/latency, **not** development effort, and are
> referenced only as related work — never imported as a calibration data layer.

## Layered architecture

```
data/
  calibration/        effort ground-truth: the verified W3F set + the manifest + measurements
  external_holdout/   independent sources (ESP / audit-mined) — labelled NON-calibration
scripts/
  extract/            produce measurements from public sources (resolve, clone, cloc, git-effort)
  validate/           environment check + calibration + Conte (1986) verdict
provenance/
  source_map.md       every artifact classified by the decision rule (evidence vs pipeline vs context)
  canonical_factsheet.md   the single source of truth for locked numbers
  change_log.md       dated, append-only audit trail
reports/              locked outputs (measurements-derived results, provenance stamps, figures)
docs/
  method/             how the pipeline works (WORKFLOW.md)
  limitations/        documented threats to validity
  related_work/       external context (incl. performance benchmarks, as citations only)
```

## The decision rule (governs every file)

- proves **effort** → `data/calibration/`
- proves the **pipeline** → `scripts/` + `provenance/`
- proves blockchain **context / system behaviour** → `external_holdout/` or `docs/related_work/`
- proves **none** of these → archive or remove

## Reproduce — one command

```bash
make quickcheck   # reproduces the honest baseline + figures (needs only python+numpy)
make all          # full pipeline: setup → resolve → measure → calibrate → figures (needs git + cloc)
make verify       # re-runs the baseline and confirms it matches the committed result (determinism gate)
```

No `make`? Use the portable equivalent: `bash run_all.sh`.

The same pipeline runs automatically on GitHub Actions (`.github/workflows/measure.yml`):
resolve → measure → calibrate → publish to the non-authoritative `rolling` branch
(never `main`; see `provenance/release_policy.md`).

## Documentation
- `docs/DATASHEET.md` — dataset datasheet (Gebru et al. *Datasheets for Datasets* structure).
- `docs/method/WORKFLOW.md` — detailed runbook.
- `provenance/` — fact sheet, source map, change log, release policy.

## What it measures
Size (KSLOC via `cloc` on the delivered commit) and effort (active person-months via
`git log`), measured **independently**, then fit as `PM = A · KSLOC^E` by deterministic
MLE and evaluated by LOOCV against Conte et al. (1986). Full detail in `docs/method/WORKFLOW.md`.

## License
Code: MIT. Data derived from public Web3 Foundation grant repositories.
