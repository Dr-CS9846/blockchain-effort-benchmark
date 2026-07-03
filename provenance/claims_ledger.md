# Claims Ledger — every published number traced to its source

This is the strict source→claim chain. For each number we publish, it records:
the **claim**, the **script** that produced it, the **data file** it consumed, the
**raw source** that data came from, whether it is **reproduced** (re-run matches),
and whether it is **frozen** (in a tagged release). A claim is *audit-grade* only
when reproduced = yes AND raw source is frozen (see §Raw layer).

_Last updated: 2026-05-30 · cite a tagged release, not `main`._

## Published / publishable numeric claims

| # | Claim | Value | Produced by | Input data | Raw source | Reproduced? | Frozen? |
|---|-------|-------|-------------|-----------|-----------|-------------|---------|
| C1 | Honest baseline LOOCV | MMRE 41.1%, PRED(25) 30.8%, MdMRE 36.0% | `scripts/validate/calibrate_bc_cocomo.py` | `data/calibration/w3f_benchmark_dataset.csv` | W3F applications + milestone-delivery records (URLs in manifest) | **YES** — `make verify` → MATCH (±1e-9) | pending `v0.1` tag |
| C2 | Baseline in-sample fit | MMRE 26.7%, PRED(25) 53.8% | same as C1 | same as C1 | same as C1 | YES (same run) | pending `v0.1` |
| C3 | Baseline parameters | C=1.6133, b1=1.0632, b2=0.1835, b3=−0.1272, σ=0.3569 | same as C1 | same as C1 | same as C1 | YES | pending `v0.1` |
| C4 | Structural finding | PM ≡ FTE × Duration (exact, all 13) | check in `calibrate_bc_cocomo.py` notes / dataset | `data/calibration/w3f_benchmark_dataset.csv` | W3F applications | YES (arithmetic, machine-precision) | pending `v0.1` |
| C5 | Engine validation (synthetic) | E≈0.84, Conte PASS — *code-validation only, NOT a finding* | `scripts/validate/calibrate_size_effort.py` | synthetic fixture | n/a (synthetic) | YES (deterministic) | n/a |
| C6 | **Measured size→effort result** | — *not yet produced* | `calibrate_size_effort.py` | `data/calibration/measurements.csv` (CI) | delivered repos @ pinned commits | **NO — awaits CI run** | no |

## Open lineage gaps (to reach audit-grade)

1. **Raw layer not frozen (C1–C4).** Inputs trace to *URLs*, not to archived immutable copies. If W3F edits/removes a source, the chain breaks. → build `data/raw/` (below).
2. **Measured chain not run (C6).** The non-circular result requires the CI measurement run; until then the only reproducible effort number is the circular declared-PM baseline.
3. **Promotion pending.** No claim is in a tagged release yet; all are "pending `v0.1`". Promotion = review → update `canonical_factsheet.md` + this ledger → merge to `main` → tag.

## Raw layer specification (`data/raw/`)

To freeze the chain at the source:
- `data/raw/applications/<project>.md` — verbatim copy of each W3F application at capture time.
- `data/raw/deliveries/<project>-milestone_*.md` — verbatim copy of each delivery record.
- `data/raw/RAW_MANIFEST.csv` — for every raw file: `source_url`, `captured_at`, `sha256`.
- Captured by a `scripts/extract/freeze_raw.py` step (runs in CI where network is reliable); hashes let anyone confirm the parsed fields derive from exactly these bytes.

Once `data/raw/` + hashes exist and C6 is produced, C1–C6 each have an unbroken
**raw → extracted → script → frozen output → reproduced** chain — the definition of
a calibration corpus, not merely a reproducible engine.

---

## Addendum 2026-07-03 — actual-effort pivot claims (C7–C10) and one retraction

_The project's ground-truth pivoted (June 2026) from planned/git-proxy effort to **actual reported
delivery effort**. The claims below supersede C1–C4 as the publishable core; C1–C4 remain valid as
history of the planned-PM track._

| # | Claim | Value | Produced by | Input data | Reproduced? |
|---|-------|-------|-------------|-----------|-------------|
| C7 | Actual-effort bare size law (n=16, 7 ecosystems) | PM = 0.33·KSLOC^0.73; r=0.65; LOOCV SA≈0; PRED(30)=12% | `calibrate_AE.py` / dissect runs #9–#16 | `pilots_cocomo.csv` + per-project `dissect_*.json` (census) | **YES — independently recomputed 2026-07-03 (A=0.330, E=0.734, r=0.655, SA=−0.01, PRED30=12%)** |
| C8 | Planned grant FTE is size-decoupled | free-fit E≈0.10 (n=104); SA 0.48; PRED30 15% | `matched_pair_calibrate.py` | `matched_pair_pm.json` (census) | YES (census artifact) |
| C9 | Within-developer churn ⊥ hours (æternity panel) | Pearson r = −0.25 (5 quarters; now 7 measured) | `dissect_pilot.py` window mode | `dissect_aeternity_sdk_*.json` | **YES — independently recomputed (r=−0.251)** |
| C10 | æternity aggregate point complete | 13.50 PM / 25.38 KSLOC (7 quarters itemised) | CI dissect runs | same as C9 | YES |

**Retraction (R1).** The n=8 full-driver headline **A = 0.56, PRED(30) = 88 %** is retracted as a claim
(see `reports/HONEST_RECALIBRATION.md`): (i) target contamination — 4 of 8 points carried
milestone/proposed PM absent from the actual-effort master; (ii) provenance mismatch — headline sizes
did not match the cited `dissect_all.json`. Retained only as an exploratory hypothesis
(status doc §4.3 Appendix A). Ledger rows for megaclite/elara/fennel/ask!/bagpipes added to
`corpus_reclassified_offchain.csv` as DROPPED with reasons.
