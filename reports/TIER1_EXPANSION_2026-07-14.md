# Tier-1 expansion pass — 2026-07-14 (n=30 → n=40 actual-effort rows)

**Goal:** grow the Tier-1 (itemised/stated actual hours, completed work) corpus from 30 rows toward 60+,
matching the scale of Boehm's COCOMO'81 pilot set (n=63).

**Method:** systematic mining of the two proven veins — the æternity forum grant corpus (Discourse JSON
API, programmatic hour extraction + manual spot-validation) and the Polkadot/Kusama retroactive
treasury record.

---

## Result: +10 new Tier-1 windows admitted to the effort corpus (documentation tier)

**The æternity core-node maintenance panel** — the vein `HARVEST_2026-07.md` flagged as "the richest
maintenance panel yet" and deferred to Phase 2. Ten grant windows (2021 → 2023) with **per-person,
per-week itemised hour logs** ("Time spent: Xh" per developer per week), by the aeternity core team
(Dimitar Ivanov, Ulf Wiger, Sean Hinde, Hans Svensson, Dincho Todorov, Craig Everett, Metin Akat,
Rumiana Akat, + occasional others):

| window | forum thread | itemised hours | # entries | PM (÷152) |
|---|---|---|---|---|
| iris hard-fork RC, weeks 10–26 2021 | [t/7365](https://forum.aeternity.com/t/7365) `[Completed]` | 2,485.0 | 90 | 16.35 |
| Q2–Q4 2021, weeks 27–52 | [t/9328](https://forum.aeternity.com/t/9328) `[Completed]` | 2,993.8 | 118 | 19.70 |
| Q1-2022 | [t/10376](https://forum.aeternity.com/t/10376) `[Completed]` | 1,885.9 | 59 | 12.41 |
| Q2-2022 | [t/10560](https://forum.aeternity.com/t/10560) `[Completed]` | 1,873.2 | 55 | 12.32 |
| Q3-2022 | [t/10740](https://forum.aeternity.com/t/10740) `[Completed]` | 2,120.0 | 66 | 13.95 |
| Q4-2022 | [t/11047](https://forum.aeternity.com/t/11047) `[Completed]` | 1,778.5 | 67 | 11.70 |
| Q1-2023 | [t/11198](https://forum.aeternity.com/t/11198) `[Completed]` | 1,790.2 | 70 | 11.78 |
| Q2-2023 | [t/11354](https://forum.aeternity.com/t/11354) `[Completed]` | 1,723.3 | 68 | 11.34 |
| Q3-2023 | [t/11708](https://forum.aeternity.com/t/11708) `[Completed]` | 1,207.6 | 43 | 7.94 |
| Q4-2023 | [t/11778](https://forum.aeternity.com/t/11778) `[Active]` title, reports complete | 1,126.2 | 47 | 7.41 |
| **TOTAL** | | **18,983.7 h** | **683** | **124.9 PM** |

### Verification performed
- **Extraction validated by hand**: all 43 entries of Q3-2023 dumped with context and reviewed line-by-line —
  every match is a genuine per-person time log; all format variants (`40h`, `19.5 hrs`, `20:30 hrs`,
  `35.5 hours`, `3:15h`) parse correctly (HH:MM → decimal).
- **No window overlap**: iris thread covers weeks 10–26/2021, Q2–Q4-2021 covers weeks 27–52 —
  they tile exactly, zero double-count.
- **No team overlap with existing rows**: the core-node team is disjoint from Denis Davidyuk
  (aeternity_sdk_* rows) and from Sebastian Borrazas/Rogerio Pontual (ae_mdw_* rows). No hour is
  counted twice across panels.
- **Series boundary established**: from 2024 week 1 the reports switch to narrative-only biweeklies with
  **no hours** (all 33 threads of 2024–2025 checked: zero time entries; funding moved to
  "Maintenance Grant #2" flat arrangement) — the itemised panel is complete at 10 windows.

### Why these rows are NOT yet in `pilots_cocomo.csv` (the calibration spec)
The effort side is Tier-1 gold, but the matched-triple gate requires a **single measurable delivery
repo**. This team's hours provably span multiple repos (aeternity node, aesophia/compiler tooling,
Generalized-Accounts UI, plugins, FROST lib, websites). An automated keyword attribution pass (this
session) bucketed entries into NODE / SOPHIA / UI / OTHERDEV / NONDEV but is **not admission-grade**:
mixed entries mis-bucket wholesale, and clear node work ("beam sync", "tx pool") escaped the keywords.
**Path to calibration admission:** hand-attribute the 683 entries by task description (each names its
component), then admit per-component matched triples (node hours ↔ `aeternity/aeternity` window churn,
etc.). Until then these rows live in the effort-documentation tier — same `Y_after_size` status as
ideal_network/dodao in `corpus_reclassified_offchain.csv`.

---

## Vein-exhaustion notes (what was checked and yielded nothing new)

- **æternity forum, all other `[Completed]` grants**: Superhero DEX (€20,000 volume, **no hours** →
  cost_no_rate class, drop); WeTrue ×2, Aeasy/Aens, Box aepp, Cash-Flag, Aepp Store, OTC-domain,
  SuperHero Vegas (money/AE-denominated or no usable hour reports); AeCanary ("we expect 90 man hours"
  = forward estimate → Tier-3 candidate at best, small); Sophia Q4-2023 (application only, no hour
  reports in thread); Sophia Q2-2023 (partial: 1 of 2 devs, 7 of 13 weeks — already rejected in
  HARVEST_2026-07.md).
- **Polkadot/Kusama retroactives**: the 2026-07-03 harvest pass swept 13 parachain subsquare APIs +
  all referenda through Polkadot #1916 / Kusama #656, eleven days before this pass — re-mining now
  would duplicate fresh work for ~zero yield. Its rejection log stands (flat-fee, forward, derived,
  mixed-scope classes).

## Remaining growth veins toward n≥60 (ranked, for the next pass)
1. **MakerDAO Core-Unit transparency reports** (monthly per-contributor billing, public, multi-year;
   Protocol Engineering CU is construction-heavy) — flagged in HARVEST next-steps, still unscreened.
2. **Hand-attribution of this AE panel** — converts 10 documentation rows into calibration-grade
   matched triples and potentially splits per-component (node/sophia) into more rows.
3. **Superhero Wallet / aepp grant threads** on the æternity forum under non-`[Completed]` titles.
4. **Author outreach** (AUTHOR_VERIFICATION_EMAILS.md machinery) — convert existing Tier-3 FTE×duration
   rows to Tier-1 by asking teams for logged actuals.

**Sign-off:** extraction scripts + raw JSON results cached in session scratchpad
(`mine_aeforum.py`, `attribute_ae_maint.py`, `mine_ae_maint_full.py`, `*_results.json`).
