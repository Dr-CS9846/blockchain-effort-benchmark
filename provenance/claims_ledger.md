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
