# Cleaned effort dataset — classified, not culled (2026-06-18)

**Philosophy: keep everything, give it scientific structure.** Every one of the 207 reported-effort
observations from the community list is retained. Nothing was deleted. Instead each row is *labelled* so it can
be used correctly — and so the dataset can keep growing without losing rigour. Real effort that someone took the
trouble to report deserves to be supported and built on, not thrown away.

## Columns added
`project_group` (collapses periodic reports of one project), `platform`, `tier`, `hours` (parsed),
`PM_152` (renormalised to Boehm's 152 h/PM), `PM_orig_160` (kept for traceability), `retroactive`, `quality`.

## Tiers (all kept; used differently downstream)
| tier | n | what it is | how to use |
|---|---|---|---|
| **T1_dev** | 92 | software development, itemised reported hours | primary calibration |
| **T2_maintenance_periodic** | 90 | monthly/quarterly maintenance reports of an ongoing codebase (Polkascan, Stakeworld) | **legitimate repeated measures** — keep; model per-period, or aggregate to project-level; do NOT treat as 90 independent projects |
| **T2b_category_component** | 6 | a report split into Tech/Comm/Bugs/Feature sub-rows | kept, flagged — sum to the parent month; don't double-count alongside it |
| **T3_infra_ops** | 15 | RPC/bootnode/snapshot/node ops (DevOps) | **separate category** — real reported effort, but ops not software construction; model on its own track |
| **T4_non_dev** | 2 | hackathons / business development | kept at the margin, flagged non-dev |
| **T5_planned_app** | 2 | W3F *application* (planned FTE, not a retrospective report) | flagged not-retroactive |
| quality: **181 strong_itemised / 26 weak_derived** | | weak = hours back-derived from FTE×duration or "typical", not itemised | keep; label weak — at least it's reported |

## Honest framing (so it survives review)
- **207 reported-effort observations across 44 distinct project-groups.** The Polkascan (119) and Stakeworld
  (20) rows are *periodic observations of two ongoing projects* — a strength for a **period-level effort model**
  (each month is a real, dated effort datapoint), but they must be modelled as repeated measures, not 139
  independent projects.
- For a **distinct-project** count toward the 161 target, the dataset currently stands at **~44 project-groups**
  (of which ~38 are clean software dev/maintenance after setting T3/T4/T5 aside) — and it is designed to grow:
  every new team simply adds rows under a new `project_group`.

## How it grows
Append (a) our 6 measured gold grants, (b) the governance-harvest finds (Ideal Network, DotBot, Gitorial,
Referendum Alert, Kitdot, and the deep-run batch), each as a new `project_group`. The structure absorbs them
cleanly and keeps the period-level richness of the maintenance reporters.
