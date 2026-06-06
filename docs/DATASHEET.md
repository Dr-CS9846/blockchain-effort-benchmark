# Datasheet — Blockchain Software Effort Benchmark (W3F pilot)

Structured on *Datasheets for Datasets* (Gebru et al., CACM 2021) — the recognised
standard for documenting a dataset's motivation, composition, collection, processing,
uses, distribution, and maintenance. This datasheet is versioned with the dataset;
**cite a tagged release** (e.g. `v0.1`) and its Zenodo DOI, never `main`.

_Dataset version: pre-release (pending v0.1 tag) · Last updated: 2026-05-30_

---

## 1. Motivation

- **Why was the dataset created?** Standard software-cost datasets (ISBSG, PROMISE, Desharnais) contain no blockchain projects, so blockchain effort estimators have no public ground truth to calibrate or test against. This dataset fills that gap with verifiable, reproducible effort data.
- **For what task?** Constructive software effort estimation (COCOMO-style): predict development effort (person-months) from independently-measured software size. The financial dimension (cost) is documented but kept separate from the constructive core.
- **Who created it / who funds it?** Created for the PhD research *"Proof of Effort"* (Dr, PhD candidate). Underlying grant data originates from the Web3 Foundation (W3F) Grants Program (public, MIT/Apache-licensed).

## 2. Composition

- **What does an instance represent?** One funded, delivery-verified W3F grant project.
- **How many instances?** Pilot: **n = 13** (verified-delivery subset). Designed to scale to n ≥ 30 → 150 via same-schema sources (no schema change).
- **Fields per instance:**
  - *Declared (from the application):* FTE, duration (months), cost (USD), milestone count; derived planned PM = FTE × duration.
  - *Measured (added by the pipeline, per pinned commit):* size (KSLOC via `cloc`), effort (active person-months via `git log`), repository URL, resolved commit SHA, language breakdown.
  - *Provenance:* application URL, milestone-delivery record, parse-quality flags.
- **Known structural caveat (critical):** declared PM is **definitionally** FTE × duration — it is a derived planned quantity, not an independent measurement. The pipeline therefore adds an *independently measured* effort signal (git active person-months) and an *independent* size signal (cloc KSLOC); the planned value is retained only as a labelled cross-check.
- **Missing data?** Some delivered repositories/commits are still being resolved from milestone-delivery records; rows without a confirmed repo are marked and excluded from measurement until resolved.
- **Confidential/sensitive data?** None. All sources are public; no personal data beyond public GitHub author handles (used only in aggregate counts; bots excluded).
- **Splits?** Calibration set (`data/calibration/`) vs external hold-out (`data/external_holdout/`, non-calibration). No train/test split is claimed at n = 13; a true hold-out is introduced at n ≥ 30.

## 3. Collection Process

- **How was the data acquired?** Declared fields parsed from public W3F application markdown; delivered repo + commit resolved from public milestone-delivery records; size and effort measured directly from the public repositories at the pinned commit.
- **Sampling strategy?** Verified-delivery filter: only projects whose milestones were independently accepted by W3F evaluators are included — this is the mechanism that makes the effort data trustworthy.
- **Who/what collected it?** Automated, deterministic scripts (`scripts/extract/`); no manual data entry. Every value is re-derivable from a commit + named tool version.
- **Timeframe?** W3F grants span the program's history; each measurement is pinned to the project's milestone-delivery commit (recorded per row).

## 4. Preprocessing / Cleaning / Labeling

- **What preprocessing?** Cost normalised to USD ($k); KSLOC counts code languages only (Solidity, Rust, TS/JS, Go, etc.), excluding vendored/build/test directories; effort counts distinct (author, month) pairs excluding merge commits and bot accounts (`.mailmap` respected).
- **Is raw data kept?** Yes — application/delivery sources are public and linked; regenerable intermediates are git-ignored, never treated as evidence.
- **Labeling?** Parse-quality and source flags per row; the source map (`provenance/source_map.md`) classifies every artifact as evidence, pipeline, or context.

## 5. Uses

- **Intended use:** calibrating and benchmarking constructive effort-estimation models for blockchain software; reproducibility and methods research.
- **What it should NOT be used for:** (a) as a *performance* benchmark — it measures development effort, not system throughput/latency (see exclusion of Blockbench/TrustedBench); (b) over-broad generalisation — the pilot is single-ecosystem (Polkadot/W3F) until external validation completes; (c) treating planned PM as measured effort.
- **Honest current result:** on the real verified set, the naive effort-driver model fails the Conte (1986) criteria (LOOCV MMRE 41.1%, PRED(25) 30.8%); the measured size→effort core is the corrected approach and its result will be reported as-is when CI measurement completes.

## 6. Distribution

- **How distributed?** Public GitHub repository (MIT-licensed code; data derived from public W3F repos). Versioned releases deposited on **Zenodo with a DOI** per tag.
- **License/terms?** Code: MIT. Data: subject to the source repositories' open licenses (MIT/Apache).
- **When?** From the first tagged release (`v0.1`) onward.

## 7. Maintenance

- **Who maintains it?** The PhD candidate; assisted by an automated nightly verification routine and periodic supervisor audits.
- **How is it updated?** A *gated* living benchmark: GitHub Actions re-measures from public commits and publishes to a **non-authoritative `rolling` branch**; the published dataset changes only via a reviewed, **tagged** release (see `provenance/release_policy.md`). This keeps freshness without ever silently changing a published claim.
- **Versioning / citation:** every claim cites a tag + Zenodo DOI version. The change log (`provenance/change_log.md`) is the append-only audit trail.
- **How to contribute / extend?** Append rows to `data/calibration/projects_manifest.csv` (same schema); CI resolves, measures, and snapshots automatically; a human promotes to a new tagged release.

---

### Reference
Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021). *Datasheets for Datasets.* Communications of the ACM, 64(12), 86–92. (arXiv:1803.09010)
