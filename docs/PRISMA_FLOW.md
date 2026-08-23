# How this dataset was built

This document lays out the full identification-to-inclusion path for the dataset, in the order
it actually happened. Every number below was checked against the real source files on 2026-08-18
(the W3F count was re-checked by cloning the source repository fresh on that date). Nothing here
is estimated.

## Stage 1: identification

Four public grant and governance programs were searched. Two more (Crust Grants and the Polkadot
Open Source Developer Grants program) were also searched and are reported here because they were
fully screened, even though neither ended up contributing a row to the final dataset.

| Source | Raw records | Grouped into projects | Notes |
|---|---|---|---|
| Web3 Foundation Grants Program | 805 delivery documents | 439 projects | every file in the public delivery repository was scanned, not a hand-picked sample |
| Crust Grants | 15 applications | 15 | |
| Polkadot Open Source Developer Grants (POSG) | 10 applications | 10 | |
| aeternity community forum | itemised effort threads, mined by hand | 23 spec rows admitted | see note below |
| Polkadot OpenGov / treasury governance records | mined by hand | rows admitted, exact reject count not preserved | disclosed limitation, see docs/DATASHEET.md |
| Zcash Community Grants | mined by hand | 4 spec rows admitted | |

The 805 figure for the Web3 Foundation vein is the number of individual delivery documents in
the source repository, before any grouping. Once grouped by project (several documents can
belong to the same project, one per milestone), that becomes 439 distinct projects. The
aeternity, OpenGov, and Zcash veins were mined by hand rather than scanned by script, so unlike
the three script-audited veins above, a full count of candidates considered and rejected was not
kept for all three. This is stated plainly in docs/DATASHEET.md rather than hidden.

## Stage 2: eligibility screening

Each of the three script-audited veins applies its own eligibility check before candidates move
forward.

**Web3 Foundation**: a project is included if it has a separable primary repository under the
project's own account (not a shared or third-party monorepo) and at least one delivery file with
a resolvable submission date.

- 439 projects screened, 423 eligible, 16 excluded.

**Crust Grants**: a project is included if its milestones were marked delivered.

- 15 applications, 7 delivered, 8 had no delivery record.
- Of the 7 delivered, 6 had a stated effort figure and no more than two repositories, which is
  as far as this screening step checks. All 6 fail the next stage, the admission gate, because
  their stated effort figure is a planned estimate (FTE times duration), not the actual effort
  this dataset requires. This is checked directly against the final dataset in stage 3 below.

**Polkadot Open Source Developer Grants**: same delivered-milestone check.

- 10 applications, 7 delivered, 2 terminated, 1 evaluated with no delivery file.
- Of the 7 delivered, 1 had a stated effort figure and no more than two repositories. It fails
  the admission gate for the same reason as the Crust candidates: planned effort, not actual.

## Stage 3: the admission gate

Every surviving candidate, from every vein, is checked against the same four rules before it can
become a row in the dataset. These rules are applied the same way regardless of which vein a
candidate came from.

1. The project's effort must be retroactive and delivered, not a future plan.
2. The effort figure must be the actual reported effort, not a planned estimate (FTE times
   duration). This is the rule that removes Crust and POSG entirely: every delivered project in
   both veins reports only planned effort, not actual worked hours. Confirmed by checking the
   final dataset directly. Neither vein appears in it, not even once.
3. The work measured must be software construction, not infrastructure operation or a service.
4. The project must resolve to one repository whose size can be measured.

Applying this gate across all veins gives the 73 rows in `data/calibration/pilots_cocomo.csv`,
the dataset's master specification file.

## Stage 4: collapsing repeated measurements into independent points

Some projects appear more than once in the 73 rows: a project funded across several quarters, or
a single grant that spans more than one repository. Counting each of those rows as a separate,
independent data point would be wrong, because they are not independent: they are repeated looks
at the same underlying project.

The rule applied here, the same rule used throughout this project, is documented in
`scripts/extract/build_calibration_points.py`:

- Windows that belong to the same project (nine aeternity node quarters, eight aeternity SDK
  quarters, a four-window aeternity middleware panel, six reactive-dot releases) are added
  together into one point.
- Repositories that share one funding scope (three ZGO repositories, two of the AEKnow
  repositories, two ink-analyzer repositories, three Polkascan repositories) share one reported
  effort figure, with their code sizes added together.
- Two rows are held out as provisional, because their measurement is not yet complete. This is a
  measurement gap, not a judgement call about the project's quality.

This step is fully automated and produces the same 44 points every time it is run. The output
has been checked, row for row, against the independently maintained calibration script's own
numbers, and the two match exactly.

## Result

- 805 raw records looked at (Web3 Foundation vein alone; the other five veins add more, without
  a fully preserved raw count for the three manually-mined ones).
- 464 projects and applications identified across the three script-audited veins (439 + 15 + 10).
- 73 rows admitted into the dataset after every eligibility rule.
- 44 independent calibration points after collapsing repeated measurements of the same project.

Run `python scripts/extract/build_calibration_points.py` to reproduce the last step yourself. It
reads the 73 rows and writes the 44 points, in under a second, with no network access needed.
