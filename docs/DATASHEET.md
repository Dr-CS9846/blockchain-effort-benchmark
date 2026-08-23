# Datasheet: Blockchain Software Effort Benchmark

Structured on *Datasheets for Datasets* (Gebru et al., CACM 2021), the standard reference for
documenting a dataset's motivation, composition, collection, processing, uses, distribution, and
maintenance. This datasheet is versioned with the dataset. Cite a tagged release and its Zenodo
DOI, not a moving branch.

_This datasheet has been through several composition updates as the corpus grew. The current,
authoritative composition is in the Addendum dated 2026-08-18, below. Sections 1 through 7 are
kept as the original document structure and reference the dataset as it stood in its earliest
form; the addenda after them record what changed and why, in the order it happened, rather than
silently rewriting the numbers in place._

---

## 1. Motivation

- **Why was the dataset created?** Standard software cost datasets (ISBSG, PROMISE, Desharnais)
  contain no blockchain projects, so blockchain effort estimators have no public ground truth to
  calibrate or test against. This dataset fills that gap with verifiable, reproducible effort
  data.
- **For what task?** Constructive software effort estimation, in the COCOMO style: predict
  development effort in person-months from independently measured software size. The financial
  dimension (cost) is documented but kept separate from the constructive core.
- **Who created it, and who funds it?** Created by Chaudhry Hamza Rashid for the PhD research
  "Proof of Effort." Underlying grant data originates from the Web3 Foundation (W3F) Grants
  Program, which is public and MIT/Apache licensed.

## 2. Composition (original, pilot-stage figures; superseded, see the addenda below)

- **What does an instance represent?** One funded, delivery-verified W3F grant project.
- **How many instances, at this early stage?** n = 13 (verified-delivery subset). Designed to
  scale through the same schema without a schema change.
- **Fields per instance:**
  - Declared, from the application: FTE, duration in months, cost in USD, milestone count;
    derived planned PM equals FTE times duration.
  - Measured, added by the pipeline, per pinned commit: size in KSLOC via `cloc`, effort in
    active person-months via `git log`, repository URL, resolved commit SHA, language breakdown.
  - Provenance: application URL, milestone-delivery record, parse-quality flags.
- **Known structural caveat, and it is a real one:** declared PM is, by definition, FTE times
  duration. It is a derived planned quantity, not an independent measurement. The pipeline
  therefore adds an independently measured effort signal (active person-months from git) and an
  independent size signal (KSLOC from cloc); the planned value is retained only as a labelled
  cross-check, never as the dataset's actual effort figure.
- **Missing data?** Some delivered repositories and commits are still being resolved from
  milestone-delivery records; rows without a confirmed repository are marked and excluded from
  measurement until resolved.
- **Confidential or sensitive data?** None. All sources are public. No personal data beyond
  public GitHub author handles, used only in aggregate counts, with bots excluded.
- **Splits?** Calibration set (`data/calibration/`) versus an external hold-out
  (`data/external_holdout/`, not used for calibration). No train and test split is claimed at
  this early stage; a true hold-out is introduced once the corpus is larger.

## 3. Collection process (original description)

- **How was the data acquired?** Declared fields were parsed from public W3F application
  documents. Delivered repository and commit were resolved from public milestone-delivery
  records. Size and effort were measured directly from the public repositories at the pinned
  commit.
- **Sampling strategy?** A verified-delivery filter: only projects whose milestones were
  independently accepted by W3F evaluators are included. This is what makes the effort data
  trustworthy rather than self-reported.
- **Who or what collected it?** Automated, deterministic scripts in `scripts/extract/`. No
  manual data entry. Every value can be re-derived from a commit plus a named tool version.
- **Timeframe?** W3F grants span the program's whole history; each measurement is pinned to the
  project's own milestone-delivery commit, recorded per row.

## 4. Preprocessing, cleaning, and labeling

- **What preprocessing?** Cost normalised to thousands of USD. KSLOC counts source-code
  languages only (Solidity, Rust, TypeScript and JavaScript, Go, and so on), excluding vendored,
  build, and test directories. Effort counts distinct author-month pairs, excluding merge commits
  and bot accounts (`.mailmap` respected).
- **Is raw data kept?** Yes. Application and delivery sources are public and linked.
  Regenerable intermediates are git-ignored and never treated as evidence.
- **Labeling?** Parse-quality and source flags are recorded per row. The source map
  (`provenance/source_map.md`) classifies every artifact as evidence, pipeline output, or
  context.

## 5. Uses

- **Intended use:** calibrating and benchmarking constructive effort-estimation models for
  blockchain software, and reproducibility or methods research built on top of it.
- **What it should not be used for:** as a performance benchmark, since it measures development
  effort, not system throughput or latency (Blockbench and TrustedBench are cited as related work
  for that reason, never as data here); for over-broad generalisation while the corpus remains
  Polkadot and Substrate dominant; or for treating a planned PM figure as if it were measured
  effort.
- **Honest early result:** on the original, smaller verified set, a naive effort-driver model
  failed the standard Conte (1986) accuracy criteria. The measured size-to-effort core was the
  corrected approach, and its result is reported as it stands, not adjusted to look better.

## 6. Distribution

- **How distributed?** Public GitHub repository, MIT-licensed code, with data derived from
  public W3F repositories. Versioned releases are deposited on Zenodo with a DOI, per tag.
- **License and terms?** Code: MIT. Data: subject to the source repositories' own open licenses
  (MIT or Apache).
- **When?** From the first tagged release onward.

## 7. Maintenance

- **Who maintains it?** The PhD candidate, assisted by an automated verification routine and
  periodic supervisor review.
- **How is it updated?** As a gated, living benchmark: automation re-measures from public
  commits and publishes to a non-authoritative rolling branch; the published dataset changes only
  through a reviewed, tagged release (see `provenance/release_policy.md`). This keeps the corpus
  current without ever silently changing a claim that has already been published.
- **Versioning and citation:** every claim cites a tag and a Zenodo DOI version. The change log
  (`provenance/change_log.md`) is the append-only audit trail.
- **How to contribute or extend?** Append rows to the calibration manifest in the same schema.
  The pipeline resolves, measures, and snapshots automatically; a human still has to promote the
  result to a new tagged release.

---

### Reference

Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daume III, H., and
Crawford, K. (2021). Datasheets for Datasets. Communications of the ACM, 64(12), 86 to 92.
(arXiv:1803.09010)

---

## Addendum 2026-07-03: composition change, actual-effort corpus (supersedes section 2's counts)

The dataset's ground truth pivoted from planned effort (FTE times duration) to actual reported
delivery effort (itemised hours divided by 152 hours per person-month). Composition at this
point:

- **Primary calibration set:** 16 distinct projects across 7 ecosystems (Polkadot, Kusama,
  Moonbeam, Astar, Ethereum-adjacent tooling, Cosmos-adjacent, and aeternity), each a matched
  triple of actual reported PM, delivery repository, and independently measured size.
- **Candidate ledger:** a 43-row ledger recording, for every candidate considered, its effort
  type (actual, proposed, milestone-reported, cost-without-rate, or derived) and its eligibility
  verdict, including the reason for every rejection.
- **Longitudinal panels, kept as single points to avoid double-counting:** the aeternity JS SDK,
  itemised across 7 quarters by one developer, collapsed to one aggregate point; and AEKnow,
  where only the `.org` component of its two repositories is sized, since the second repository's
  size is inflated by vendored code, a limitation disclosed rather than hidden.
- **Planned-PM track**, kept as a contrast dataset: a much larger set of 104 rows where effort is
  only the planned grant FTE figure, which turns out to be decoupled from code size. That
  negative finding is one of the project's headline results.

Known limitation, disclosed at this stage: two projects, `dotreasury` and `Kitdot`, were kept in
as flagged scope-mismatch outliers rather than quietly dropped.

## Addendum 2026-08-18: composition change, full corpus, n equals 44 (supersedes section 2 and the 2026-07-03 addendum)

The corpus grew substantially after the 2026-07-03 addendum, and one further correction was made:
a project called `polkascan` had been counted three times by mistake, split across three
repositories that were actually one funded scope. This was caught and fixed on 2026-08-08. The
current, authoritative composition is:

- **73 hand-verified, source-cited rows** in the dataset's master specification
  (`data/calibration/pilots_cocomo.csv`). Each row is a matched triple of actual reported PM,
  delivery repository with an exact commit or measurement window, and independently measured
  equivalent KSLOC.
- **Screened against four contributing public sources:** the Web3 Foundation Grants Program
  (a script-audited census: 805 raw delivery records, grouped into 439 projects, 423 of them
  eligible, re-verified live against the real source repository on 2026-08-18), the aeternity
  community forum (23 of the 73 rows), Polkadot OpenGov and treasury governance records, and
  Zcash Community Grants (4 of the 73 rows).
- **Two further sources were fully screened and correctly produced zero eligible rows:** Crust
  Grants (15 applications, 7 delivered, 6 reaching an intermediate admit-ready check) and the
  Polkadot Open Source Developer Grants program (10 applications, 7 delivered, 1 reaching the
  same check). Every one of those candidates reports only planned, forward-grant effort rather
  than the retroactive actual effort this dataset requires, so none of them pass the final
  admission gate. This is recorded here as a deliberate, checked screening outcome, not an
  oversight. See `docs/PRISMA_FLOW.md` for the complete path with every count.
- **Dependent-window and shared-scope collapse**, applied by one documented rule, the same way
  for every project, not as separate per-project judgement calls: nine aeternity node quarterly
  windows, eight aeternity SDK quarterly windows, and a four-window aeternity middleware panel
  each collapse into one aggregate point; six reactive-dot releases collapse the same way; and
  three ZGO repositories, one of the two AEKnow repositories, two ink-analyzer repositories, and
  the three Polkascan repositories (corrected 2026-08-08) each share one funded-scope effort
  figure, with their code sizes added together. Two rows are excluded as provisional, because
  their measurement is not yet complete; this is a measurement gap, not a judgement about the
  project itself.
  This step is fully reproducible by running `scripts/extract/build_calibration_points.py`, which
  reads the 73 rows and writes the 44 collapsed points. Its output has been checked, row for row,
  against the project's independently maintained calibration script, and the two match exactly.
- **Final dataset: 44 independent calibration points.**

This addendum is the current, authoritative composition statement. Section 2 above and the
2026-07-03 addendum are kept as a dated historical record, following this project's practice of
recording corrections openly rather than rewriting earlier numbers out of the document (see
`provenance/change_log.md`).
