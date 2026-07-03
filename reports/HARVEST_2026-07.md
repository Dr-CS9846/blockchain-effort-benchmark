# Actual-effort harvest, July 2026 — n=16 → n=17(+1 provisional)

**Goal:** grow the actual-effort matched-triple set toward n≈30 (roadmap item 1 of
`PROJECT_STATUS_FOR_REVIEWER.md` §8). **Gate applied** (§2.1): retroactive/delivered + itemised actual
hours + software construction + single measurable delivery repo.

**Coverage of this sweep:**
- Subsquare governance APIs (`<chain>-api.subsquare.io`) for 13 parachains — Hydration, Basilisk, Acala,
  Karura*, Bifrost, Interlay, Kintsugi, Crust*, Centrifuge*, Altair*, Phala*, Zeitgeist*, Darwinia*
  (\* = no hosted API / empty). Raw listings cached (session scratchpad `harvest/cache/`).
- All new Polkadot referenda #1840–1916 and Kusama #520–656 (post-dating the previous mining pass).
- The æternity forum grant corpus (Discourse JSON API): all `[Completed]`/`[Active]` grant series.

## New calibration point (pending CI size measurement)

**æternity Middleware (`aeternity/ae_mdw`) — 3,052.5 h = 20.08 PM, window 2022-12-01 → 2023-10-01.**
Four consecutive grant windows with **per-person, per-task weekly itemised hours** (the same reporting
culture as the JS SDK panel), one team (Sebastian Borrazas + Rogerio Pontual, + Philipp coordinating in
window 1), one delivery repo (Elixir indexing middleware, repo since 2020 → **window churn** is the
matched scope):

| window | forum topic | hours | PM |
|---|---|---|---|
| Dec 2022 – Mar 2023 | t/11073 `[Completed]` | 1,394.5 | 9.17 |
| Apr – Jun 2023 | t/11320 `[Active]`, reports complete | 898.0 | 5.91 |
| Jul 2023 | t/11635 `[Completed]` | 312.0 | 2.05 |
| Aug – Oct 1 2023 | t/11693 `[Active]`, reports end Oct 1 | 448.0 | 2.95 |

The 4 dependent windows collapse to **one aggregate point** (no pseudo-replication), and the weekly
per-person hours form a **second within-team longitudinal panel** (after the JS SDK) for the §4.4-class
within-project analysis. Spec rows added to `pilots_cocomo.csv` (4 windows); effort rows AE1–AE4 in
`real_reported_effort.csv`.

**Caveats (disclosed):** hour totals parsed programmatically from the forum posts (task lines ending
"…Nh") — re-verify by hand before the fit; a handful of task lines (e.g. one "Create P2P Marketplace,
16h") may not land in `ae_mdw` — bounded by <2 % of total; window 4 titled Aug–Oct but reports stop
Oct 1, so the churn window must cut at Oct 1.

## Panel extension (provisional)

**æternity JS SDK Q1-2025** (t/13203): 280.8 h itemised weekly vs 285 h approved budget, window
2025-01-01 → 2025-03-23, same developer (Denis Davidyuk). Extends the SDK panel 7 → 8 quarters. Held
**provisional** until the topic's closeout is confirmed (title still `[Active]`, unlike the 7
`[Completed]` quarters). No Q2-2025+ SDK grant exists — the series ended here.

## Gate rejections (all recorded in `corpus_reclassified_offchain.csv`, rows 44–59)

- **Flat-fee / dollar-only, no hours:** Subsquare parachain-deployment maintenance (Acala 2023/2024/2025,
  Karura, Bifrost 2024 — $500–700/mo), web3alert (Interlay + Kintsugi, €600/mo), Interlay dashboard RFP
  ($5k milestones), BigTipper RFP ($1.2k), Acuity Index (proposal site down, tip explicitly
  "recognition not valuation").
- **Forward/planned:** Kusama Forum MVP, PAPI #1874 (**804 h @ 95 €/h — excellent for the planned-track
  contrast set**, upgrade if actuals reported), DotPulse (timed out, repo never created).
- **Derived, not hours:** plaza.fun #1897 (retroactive + delivered, per-workstream table but in
  FTE-months ≈18, and the referendum was rejected → SENSITIVITY tier, TrueBlocks-class).
- **Mixed scope:** Encointer retros (org-level CHF lumps), Virto Connect (retro+forward in one lump).
- **Partial hours:** Sophia Q2-2023 (1 of 2 devs, 7 of 13 weeks); aeScan (5 quarters of reports, zero
  hours).
- **Deferred (Phase 2):** AE core-node maintenance — ~20+ windows of per-person weekly hours by an
  8-person team, but the work provably spans node + compiler + UI repos (per-task repo attribution
  needed) → the richest maintenance panel yet, wrong shape for a single matched triple.

## Bonus finding

The Bifrost-2024 Subsquare maintenance proposal states OpenSquare does **not** bill parachain treasuries
for common feature development ("funded by the polkadot/kusama treasury") → **the existing
`subsquare_maint` point (24.7 PM) is not double-funded across chains.** Noted in its ledger row.

## Next steps
1. Push `pilots_cocomo.csv` and trigger the `dissect_pilot.yml` CI workflow to measure the 4 `ae_mdw_*`
   windows + `aeternity_sdk_q1_2025` (window churn).
2. Hand-verify the parsed hour totals against the forum posts (extraction audit).
3. Re-run the n=17 bare-law fit; refresh §3.1/§4.2 of the status doc.
4. Remaining growth veins: MakerDAO Core-Unit transparency reports (Tier 2, likely org-level —
  screen before investing); æternity Superhero/DEX grants (final reports exist, hour formats unchecked);
  per-task repo attribution of the AE core-node panel (Phase 2).
