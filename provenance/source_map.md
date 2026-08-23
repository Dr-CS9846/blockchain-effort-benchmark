# Source map: every artifact in this repository, classified

**Decision rule.** Effort and size measurements are evidence. Scripts that produce those
measurements are pipeline. Everything else is either documentation or a governance record.

_Last updated: 2026-08-18, to match the current 73-row, 44-point corpus. Earlier versions of this
map described an earlier, smaller pilot corpus; see `provenance/change_log.md` for that history._

## Evidence

| Artifact | Role | Evidence of |
|---|---|---|
| `data/calibration/pilots_cocomo.csv` | The 73-row master specification: reported effort, repository, sizing mode, and driver flags for every admitted project | effort ground truth and project attributes |
| `data/calibration/calibration_points_n44.csv` | The 44 independent points after collapsing repeated measurements of the same project | the dataset's final calibration points |
| `reports/dissect_<project_id>.json`, one per spec row | Per-project measured size, reuse split, and driver ratings | measured size and driver evidence, traceable to a specific repository state |
| `data/raw/` | Frozen copies of the original public grant and delivery documents, with checksums | the original source record, independent of this pipeline |

## Pipeline

| Artifact | Role |
|---|---|
| `scripts/extract/harvest_deliveries.py` | Scans the Web3 Foundation delivery repository and groups files into candidate projects |
| `scripts/extract/crust_prescreen.py`, `scripts/extract/posg_prescreen.py` | Screen the Crust Grants and Polkadot Open Source Developer Grants programs |
| `scripts/validate/dissect_pilot.py` | Measures one project's code size and assigns its COCOMO drivers from repository signals |
| `scripts/extract/build_calibration_points.py` | Collapses the 73 spec rows into the 44 final points, deterministically |
| `scripts/validate/effort_truth.py` | Reconciles independent effort signals into the ground truth figure used in the spec |
| `scripts/validate/validate_pm.py` | Records validity and reliability evidence for the measured effort figures |
| `scripts/validate/00_check_environment.py` | Checks that the tools needed to run the pipeline are present |

## Documentation and governance

| Artifact | Role |
|---|---|
| `docs/DATASHEET.md` | The full dataset description, in the standard datasheet format |
| `docs/PRISMA_FLOW.md` | The identification-to-inclusion path, with the real count at every step |
| `provenance/change_log.md` | The append-only record of what changed in this dataset, and why |
| `provenance/release_policy.md` | How a measurement becomes part of a citable, tagged release |
| `provenance/claims_ledger.md` | What is currently an established result versus what is still open |

## Excluded from this repository

- The model-calibration and estimation work built on top of this dataset. It lives in the larger
  development repository linked from the main README and will be released on its own once it is
  finished.
- Regenerable intermediates, such as repository clone caches. These are never evidence and are
  not committed anywhere in this project.
