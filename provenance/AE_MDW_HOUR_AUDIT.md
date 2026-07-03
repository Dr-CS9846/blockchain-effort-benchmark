# æternity Middleware (ae_mdw) Hour Audit Status

**Last updated: 2026-07-03**  
**Status: INTERNAL CONSISTENCY VERIFIED; EXTERNAL VERIFICATION PENDING**

## Summary
The 4 ae_mdw grant windows (Dec 2022 – Oct 2023) total **20.08 PM = 3,052.5 itemised hours** across a 2–3 person team. The spec (`pilots_cocomo.csv`) and effort-tracking (`real_reported_effort.csv`) are internally consistent to 0.01%; per-person subtotals match aggregates exactly. **Source data (forum posts) must be hand-verified before the headline is quoted.**

## Internal Consistency Check ✓ VERIFIED

### Spec totals (pilots_cocomo.csv)
| window | PM | hours | status |
|---|---|---|---|
| ae_mdw_dec22_mar23 | 9.17 | 1,393.8 h | ✓ |
| ae_mdw_q2_2023 | 5.91 | 898.3 h | ✓ |
| ae_mdw_jul_2023 | 2.05 | 311.6 h | ✓ |
| ae_mdw_aug_oct_2023 | 2.95 | 448.4 h | ✓ |
| **TOTAL** | **20.08** | **3,052.2 h** | match ±0.01% |

### Per-person breakdowns (real_reported_effort.csv)
- **AE1** (Dec–Mar): 1,394.5 h = Seb 674 + Rog 630 + Phil 90.5 ✓
- **AE2** (Apr–Jun): 898 h = Seb 512 + Rog 386 ✓
- **AE3** (Jul): 312 h = Seb 152 + Rog 160 ✓
- **AE4** (Aug–Oct): 448 h = Seb 148 + Rog 300 ✓

All subtotals sum exactly to aggregates.

## Manual Audit Checklist

To be completed on https://forum.aeternity.io:

- [ ] **Topic t/11073** "Middleware December-March 2023" [Completed]
  - Expected: 1,394.5 h (Seb 674 + Rog 630 + Phil 90.5)
  - Verify weekly task-hour tables for Dec 1, 2022 – Mar 31, 2023
  - Confirm Philipp's 90.5 h are window-1 only

- [ ] **Topic t/11320** "Middleware April-June 2023" [Active]
  - Expected: 898 h (Seb 512 + Rog 386)
  - Verify weekly task-hour tables for Apr 1 – Jun 30, 2023
  - (Note: forum title is [Active] but reports are complete)

- [ ] **Topic t/11635** "Middleware July 2023" [Completed]
  - Expected: 312 h (Seb 152 + Rog 160)
  - Verify weekly task-hour tables for Jul 1 – Jul 31, 2023
  - (Smallest window, easiest verification)

- [ ] **Topic t/11693** "Middleware August-October 2023" [Active]
  - Expected: 448 h (Seb 148 + Rog 300)
  - Verify weekly task-hour tables for Aug 1 – Oct 1, 2023
  - **CRITICAL:** Reports end Oct 1 (not Oct 31); window must match

## Known Caveats

Per HARVEST_2026-07.md:
- Hours were parsed programmatically from forum task-list lines (pattern: "Task Name, Nh")
- A handful of task lines (e.g., "Create P2P Marketplace, 16h") may not land in ae_mdw
- Bounded by < 2% of total (~60 h max discrepancy)
- **Confidence threshold:** If all checklist items pass and total deviation ≤ 2%, the 20.08 PM headline is solid

## Environment Constraints

- Sandboxed environment has no network access to forum.aeternity.io
- Internal consistency verified locally (CSV files, per-person breakdowns)
- External verification (forum posts) requires manual inspection or network-enabled environment

## Outcome

Once the checklist items are verified (or minor discrepancies reconciled):
1. Update this file's status to "VERIFIED"
2. The 20.08 PM can be cited without caveat in the dissertation abstract and claims
3. If significant discrepancies (> 2%) are found, document and adjust the headline accordingly
