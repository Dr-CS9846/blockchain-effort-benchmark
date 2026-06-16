# Intake Register & Author-Contact Register
*Operational scaffolding for the Dataset Expansion Charter. Live board — updated every stage transition.*
*Status legend: `candidate → in-analysis → emailed → ADMITTED | rejected(gate)`.*

---

## A. Field dictionary (the per-pilot record)

**Identity & triple**
`pilot_id · name · ecosystem · funding_mechanism · project_type · stack · effort_type(A/P)`

**Provenance (Stage 3–4)**
`proof_type(onchain_tx/milestone) · ref(proposal#/grant) · proof_url · amount_native · amount_usd_at_exec ·
exec_date · repo_url · pinned_sha · sizing_mode`

**Effort (Stage 5)**
`reported_effort_verbatim · effort_unit · reported_PM · itemized(y/n)`

**Size + CEVRP (Stage 6)**
`equiv_ksloc · E · prod_EM · A_local · cevrp_verdict(raw/corrected) · cevrp_C1 · cevrp_C2 · cevrp_C3`

**Author contact (Stage 7 — REQUIRED before admission)**
`author_name · github_handle · primary_email · org · alt_channel · source_of_contact`

**Verification (Stage 8)**
`verification_status(unverified/emailed/author-confirmed/author-corrected/no-response) ·
email_sent_date · followup1_date · followup2_date · outcome_note`

**Diversity tags**
`size_class · effort_magnitude_band · team_size · geography`

---

## B. Admitted pilots — author contact + effort-proof link + verification status
*Contacts captured 2026-06-15 from primary sources (W3F applications, project sites, GitHub, on-chain proposal
threads). `email` = verified public address; `channel` = best reachable alternative where no public email
exists. The **effort-proof link** is the exact page showing the reported effort from which PM is computed.*

| id | project | author / owner | email | best channel | effort-proof link (PM source) | verify |
|----|---------|----------------|-------|--------------|-------------------------------|--------|
| P01 | Subsquare (maint) | OpenSquare Network (Hangzhou, CN) | yongfeng@opensquare.network | GitHub opensquare-network · X @opensquaren | [referenda/1225 — 3,760 dev-hrs table](https://polkadot.subsquare.io/referenda/1225) | unverified |
| P02 | Ask! v0.1 | Patract Labs | ⚠ org inactive (~2021) — none public | GitHub patractlabs (issue) | [kusama treasury/66 — 30 dev-wk](https://kusama.subsquare.io/treasury/proposals/66) | unverified |
| P03 | Bagpipes | Ramsey Ajram + Filip Kalebo (Decentration) | none public | Medium @decentration · Polkassembly thread · GitHub BagpipesOrg | [referenda/362 — 1,515 dev-hrs](https://polkadot.polkassembly.io/referenda/362) | unverified |
| P04 | dotreasury | OpenSquare Network | yongfeng@opensquare.network | GitHub opensquare-network | [kusama treasury/103 — ~20 dev-days](https://kusama.subsquare.io/treasury/proposals/103) | unverified |
| P05 | Megaclite v0.1 | Patract Labs | ⚠ org inactive — none public | GitHub patractlabs (issue) | [polkadot treasury/24 — 15 dev-wk](https://polkadot.subsquare.io/treasury/proposals/24) | unverified |
| P06 | Subsquare new-feat | OpenSquare Network | yongfeng@opensquare.network | GitHub opensquare-network | [referenda/13 — 1,736 h subsquare share](https://polkadot.subsquare.io/referenda/13) | unverified |
| P07 | Fennel Protocol | Sean Batzel / Fennel Labs LLC (Wyoming, US) | info@fennellabs.com | LinkedIn /in/seanbatzel · GitHub Romulus10 / fennelLabs | [W3F Fennel_Protocol.md — 3 FTE×3 mo](https://github.com/w3f/Grants-Program/blob/master/applications/Fennel_Protocol.md) | unverified |
| P08 | Elara v0.1 | Patract Labs | ⚠ org inactive — none public | GitHub patractlabs (issue) | [polkadot treasury/16 — 20 dev-wk](https://polkadot.subsquare.io/treasury/proposals/16) | unverified |
| P10 | Remarker | Ashutosh Singh (solo, India) | none public | remarkers.io · Subsquare proposal thread · GitHub Remarkers | [referenda/1170 — 1,100 work-hrs](https://polkadot.subsquare.io/referenda/1170) | unverified |
| P11 | Kheopswap | "Kheops" (solo, FR/KR; @Talisman) | none public | GitHub kheopswap · [Polkadot Forum #9489](https://forum.polkadot.network/t/kheopswap-xyz-dex-ui-for-asset-hub/9489) · proposal thread | [referenda/1102 — ~480 hrs](https://polkadot.subsquare.io/referenda/1102) | unverified |
| P12 | ink! analyzer | David Semakula (solo) | via davidsemakula.com contact | GitHub davidsemakula · X @davidsemakula · Forum | [referenda/619 — 424 h itemised](https://polkadot.subsquare.io/referenda/619) | unverified |
| P13 | Dot Code School | Saumya Karan (solo, India) | via LinkedIn /in/skrn | GitHub saumyakaran · Medium saumyakaran.medium.com | [referenda/364 — 144 h](https://polkadot.subsquare.io/referenda/364) | unverified |
| **P14** | **Pontem (Move VM pallet)** | Boris Povod / Dfinance (Zug, CH) | **boris@dfinance.co** | GitHub pontem-network · dfinance.co | [W3F pontem.md — M1+M2 252 person-days](https://github.com/w3f/Grants-Program/blob/master/applications/pontem.md) · [delivery PR#113](https://github.com/w3f/Grant-Milestone-Delivery/pull/113) | unverified (admitted, pending dissection) |
| **P15** | **SkyeKiwi Protocol** | Song Zhou / SkyeKiwi (@RoyTimes) | **song.zhou@skye.kiwi** | GitHub skyekiwi · cdocs.skye.kiwi | [W3F skyekiwi-protocol.md — 2 FTE×4 mo = 8.0 PM](https://github.com/w3f/Grants-Program/blob/master/applications/skyekiwi-protocol.md) | admitted; delivery = census **exact** commit (strong); pin PR at dissection |
| **P16** | **Stable Asset (DeFi)** | Terry Lam / NUTS Finance | **terry@nuts.finance** | GitHub nutsfinance · LinkedIn /in/terry-lam-80a71927 | [W3F stable-asset.md — 2 FTE×1 mo = 2.0 PM](https://github.com/w3f/Grants-Program/blob/master/applications/stable-asset.md) | admitted (provisional); confirm delivery + pin **exact** commit at dissection (census used cutoff) |
| **P17** | **Subcoin (BTC-on-Substrate node)** | subcoin-project (Liu-Cheng Xu) | TO-CAPTURE (GitHub subcoin-project) | GitHub subcoin-project | [pre-screen DELIVERED ×3; W3F app](https://github.com/subcoin-project/subcoin) | admitted (provisional); primary-FTE + CI dissection to finalize |
| **P18** | **Myriad Social (social parachain)** | Myriad Social | TO-CAPTURE (GitHub myriadsocial) | GitHub myriadsocial · myriad.social | [pre-screen DELIVERED ×3](https://github.com/myriadsocial/myriad-node-parachain) | admitted (provisional); primary-FTE + CI dissection to finalize |
| **P19** | **Melodot (data-availability layer)** | ZeroDAO | TO-CAPTURE (GitHub ZeroDAO) | GitHub ZeroDAO | [pre-screen DELIVERED ×4](https://github.com/ZeroDAO/melodot) | admitted (provisional); primary-FTE + CI dissection to finalize |
*(P09 ParaSpell — dropped (repo deleted); contact retained for a possible base-grant revisit: Dušan Morháč,
xmorhac@stuba.sk, GitHub dudo50.)*

**Admission standard for n-building (P17+):** with the quality machinery now in place (pre-screen =
DELIVERED + not-terminated + single-repo + scope-ratio-sane), candidates passing ALL automated gates are
admitted **provisional** on the scope-validated census PM, then **finalized** by (a) primary FTE×duration
re-read and (b) CI dissection computing A_local (which flags any effort grossly off-cluster). Contact capture +
verification email follow as part of finalization. This is the practical scaling the PI authorized — quality
enforced by the gates, not by a full hand-dive per candidate.

**Contact-capture notes:**
- **OpenSquare (P01/P04/P06)** share one team email → one combined message can verify all three (each proposal
  cited separately).
- **Patract Labs (P02/P05/P08)** wound down activity after ~2021; no current public contact found — lowest
  response odds. Route: GitHub issue on `patractlabs/*`; if silent, flag all three **"public-record only."**
  Their on-chain effort tables are fully itemised, so provenance stays strong even without a reply.
- **Solo devs (P10–P13)** have no public email but strong public channels; for P12/P13 the website/LinkedIn
  contact form is the route. Exact send address to be finalised at send time.
- **No contact was fabricated.** "none public" means a real address was not found in public sources, not that
  one was guessed.

**Outreach status (2026-06-15):**
- **EMAILED** (Group 1): **P01 / P04 / P06** (OpenSquare, one combined email) and **P07** (Fennel) — sent by PI.
- **GitHub-issue queued** (Groups 2 & 3): **P02, P03, P05, P08, P10, P11, P12, P13** — brief public verification
  issues drafted in `OUTBOX_github_comments_batch1.md`, one per repo. Channel chosen because GitHub has no
  inbox. Check-back cycle: **every 24 h** read the public thread, log replies. P13 repo is archived → fallback
  to an active `saumyakaran` repo or LinkedIn. P02/P05/P08 (Patract) low odds → after a few cycles flag
  "public-record only."

---

## C. Diversity coverage snapshot (current admitted corpus, n=12)
*Shows where the corpus is concentrated → drives the next discovery wave toward empty cells.*

| Axis | Current coverage | **Gap to fill (priority targets)** |
|---|---|---|
| Ecosystem | Polkadot ×10, Kusama ×1, W3F ×1 | **Ethereum, Solana, Cosmos, NEAR, Tezos, Move, Stellar — ALL empty** |
| Funding mechanism | treasury ×9, W3F grant ×2, Patract grant ×1 | **RetroPGF, Gitcoin, bounty, hackathon→grant — empty** |
| Project type | gov/data ×4, infra ×1, ZK-lib ×1, lang ×1, NFT ×1, DEX ×1, LSP ×1, edu ×1, L1 ×1 | bridge, oracle, indexer, wallet under/un-covered |
| Stack | TS/JS ×7, Rust ×5, AssemblyScript ×1, **Move ×1 (P14)** | **Solidity, Go/Cosmos-SDK, Anchor, Cairo, Vyper — still empty** |
| Size class | XS ×2, S ×5, M ×3, L ×2, XL ×0 | **XL (>100 KSLOC) empty; more XS for COCOMO low-end** |
| Effort type | Actual ×6, Proposed ×6 | balanced ✓ (maintain ≥50% Actual) |
| Effort magnitude | sub-PM ×0, 1–5 ×6, 5–20 ×5, 20–100 ×1, >100 ×0 | **>100 PM and sub-PM empty — need wider range to beat Boehm** |
| Team size | solo ×3, small ×?, team ×? | record team size during verification |
| Geography | China(Patract), EU, US, India, solo | broaden (LatAm, Africa, SEA) |

**Headline gap:** the corpus is currently **mono-ecosystem (Polkadot)**. The single highest-diversity-yield
move is cross-ecosystem expansion (Ethereum/Solana/Cosmos/Move) — which simultaneously discharges Reviewer 2's
generalizability concern.

---

## D. Candidate pipeline — Wave 1 status

**Discovery is largely solved:** earlier work harvested + measured a **439-row W3F grant census**
(`measurements_census.csv`) with pinned commits and reuse fractions → **146 pass basic cleanliness**. The
bottleneck is now hand-verification, not finding candidates.

**⚠ Census guardrail (learned 2026-06-15, hardened):** the census passes *basic* cleanliness only and has
**hidden defects** that only per-candidate primary verification catches. Each candidate MUST be checked against
its primary W3F application for ALL of:
1. **Effort accuracy** — census `planned_pm`/`planned_fte`/`cost_usd` are parse artifacts (Pontem: census 4 PM
   / $96 vs primary 252 person-days / 1.4658 BTC). Re-read explicit FTE×duration (or days/hours).
2. **Delivery status** — read the application **`Status` header** + milestone-delivery record. *Terminated /
   partial grants are in the census* (Spacewalk = `Status: Terminated`, census flagged it "clean"). Reject.
3. **FTE internal consistency** — overview FTE×duration must reconcile with the milestone sum (Spacewalk's did
   not: 0.5 FTE/3 mo vs ~5 person-months in milestones).
4. **Single matched repo** — not a multi-repo umbrella.
**Verified census overturns so far:** Pontem (effort wrong→corrected, admitted), Spacewalk (terminated→reject).
⇒ true clean-yield is **below** the raw 146 count; budget for ~1-in-2 rejection on cold census picks.

| cand_id | candidate | ecosystem / stack | status | note |
|---|---|---|---|---|
| **P14** | **Pontem (Move VM pallet)** | W3F / **Move** | **✅ ADMITTED** (pending CI dissection) | 252 person-days (M1+M2) → 13.3 PM; forked Libra Move VM → CEVRP applies |
| **P15** | **SkyeKiwi Protocol** | W3F / TS+ink!+Rust | **✅ ADMITTED** (pending dissection) | 2 FTE×4 mo = 8.0 PM; privacy/secret-sharing (new type); census agreed |
| **P16** | **Stable Asset** | W3F / Rust (Substrate) | **✅ ADMITTED** (pending dissection) | 2 FTE×1 mo = 2.0 PM; DeFi primitive (new type); ported from own acBTC Solidity (authored) |
| C-W1-galaxy | Galaxy (3D web/whiteboard) | W3F / TS+Rust | **⏸ HOLD** | effort clean (1 FTE×1 mo = 1 PM) BUT built on **Excalidraw** (heavy upstream) + **delivery not confirmed** + thematically light Polkadot → confirm delivery & CEVRP before admit |
| C-W1-Perun | Perun state channels | W3F / Rust+Go | **⏸ HOLD** | repo+proof+contact clean, but **effort lacks explicit FTE** (app gives duration+cost only) → email seb@perun.network / matthias@perun.network to confirm person-effort before admit |
| C-W1-pool | 144 clean W3F census candidates | W3F (Polkadot) | queue | triage each: primary-effort verify → dissect → admit one at a time |

**Cross-ecosystem finding (honest):** truly *non-Polkadot* clean person-effort is scarce — Ethereum ESP /
Gitcoin / RetroPGF rarely publish FTE; Filecoin devgrants give only vague FTE floors and weaker funding proof.
**Plan:** use the W3F + OpenGov clean veins as the **volume engine** to surpass Boehm (n≥165), and add
cross-ecosystem points **opportunistically + labeled** where a clean triple genuinely exists (Pontem's Move
stack is itself a diversity win). Ecosystem is recorded per-pilot so the constant can be tested across it.

**Next actions:** (1) dispatch CI dissection for P14 (pin M2 commit, apply CEVRP); (2) email Perun for effort;
(3) work the 144-candidate queue — primary-effort verify the next 3–5, admit the clean ones.

### Batch B — retroactive (OpenGov actual-effort) — *in progress*
Verification tool: the **Subsquare per-referendum API** (`https://polkadot-api.subsquare.io/gov2/referendums/{id}`)
returns content + on-chain state via direct fetch (no Chrome). Confirmed working.

**Finding (confirmed, n=3/3):** *recent (2025) retroactive proposals are poor matched-triple material* — high
on-chain **rejection** rate + effort hidden in **external Google Docs/Sheets** (no on-chain hours). All three
checked failed and are logged as exclusions:
- **#1762 RegionX Hub** — Rejected on-chain + effort in external Google Doc → reject (G3 + G4 fail).
- **#1799 Mimir** (multisig) — Rejected on-chain + budget in external Google Sheet → reject (G3 + G4 fail).
- **#1805 Kitdot** (Solidity/PolkaVM toolkit) — Rejected on-chain + 5-repo umbrella → reject (G3 + G1 fail).

**Corrected method:** the **scan returned 2025 referenda (wrong era)**. Our clean actuals are all **2024,
executed, single-repo, on-chain hours table** (Remarker #1170, Kheopswap #1102, ink!analyzer #619,
dotcodeschool #364). The right tool is the **`treasury_mine` CI harvester** (already built, task #38): it pages
the *full* treasury history server-side and emits a candidate manifest of EXECUTED proposals with parsed
effort — no inline reject-fetching, no context bloat. *(Local bash harvesting is disallowed — web fetches must
go through the sanctioned tools; CI is the sanctioned at-scale path.)* **Next:** dispatch `treasury_mine` for
the 2024 executed range → triage the manifest for retroactive + on-chain-table + single-repo → verify 3.
*No off-chain-effort or rejected proposal will be admitted.*

### Delivery pre-screen — DONE (CI run #1, 2026-06-15)
`prescreen-delivery` workflow ran clean (~17 s). It scanned the **whole** W3F Grants-Program + Grant-Milestone-
Delivery and ranked every census project: **~270 DELIVERED** (by milestone count) vs **~45 REJECT_terminated**.
**Spacewalk correctly landed in REJECT_terminated** — as did openbrush, tuxedo, polkadex, manta, deip, redstone,
polkamusic, etc. (all `Status: Terminated`). Full CSV on the `census` branch; abridged copy in
`census_prescreen.csv`. ⇒ cold-pick rejection now near-zero: **deep-verify only DELIVERED rows**.

**Batch C shortlist (DELIVERED + census-PM + new project type — deep-verify next, 3 at a time):**
| candidate | PM~ | deliv | type (diversity) | repo |
|---|---|---|---|---|
| hyperfridge | 9.0 | 5 | **FIAT/banking bridge (EBICS, RWA)** | element36-io/hyperfridge-r0 |
| melodot | 6.75 | 4 | **data-availability layer** | ZeroDAO/melodot |
| NewOmega | 4.0 | 4 | **on-chain game** (exact commit) | WiktorStarczewski/newomega.polkadot |
| fair_squares | 12.0 | 5 | real-estate DAO/DeFi | Fair-Squares/fair-squares |
| logion_wallet | 20.0 | 4 | legal/notary identity | logion-network/logion-wallet |
| PrivaDEX | 11.0 | 4 | cross-chain DEX aggregator | kapilsinha/privadex |
| subcoin | 3.0 | 3 | Bitcoin-on-Substrate | subcoin-project/subcoin |
Each still gets the 4-point primary check (effort accuracy · FTE consistency · single repo · not-terminated[pre-passed]).

**Batch C verification status (2026-06-15):**
- **hyperfridge → HOLD.** Effort clean (1.5 FTE × 6 mo = 9.0 PM, census agrees) BUT **multi-repo grant**: the
  9 PM spans `element36-io/hyperfridge-r0` (ZK circuit, M1) + `ocw-ebics` (pallet, M3) + `ebics-java-service`
  (backend, M2) + parachain (M4) + UI (M5). Census measured only the circuit (1.68 KSLOC) → 9 PM↔1 component
  fails single-scope (G1). *Salvage option:* milestone-isolate **M1 (1.5 FTE×2 mo = 3.0 PM) ↔ hyperfridge-r0**
  as a clean sub-pilot (needs M1-delivery confirm + size the circuit only). element36, Zug CH; walter.strametz@element36.io.
- **melodot / subcoin → app filename not resolved** (raw `melodot.md` / `subcoin.md` 404). Re-fetch with correct
  filenames next pass.
- **Lesson (efficiency):** prioritize **single-artifact** candidates (one pallet / one node / one library) — a
  full-stack grant (hyperfridge) is inherently multi-repo. *Pre-screen v2 idea:* have the CI script also emit the
  matched application filename + a **repo-count** per grant, so the shortlist is directly actionable (correct
  filename + single-vs-multi-repo flag) without per-candidate full-app fetches.

**GOLD actual-effort vein — DEPTH FINDING (treasury-mine #8, 40-page deep, 2026-06-15):** of ~40 retroactive
proposals harvested (Polkadot, back to early 2024), the vast majority are **tips/events/marketing/reimbursements**
(not dev-with-effort). Dev-with-repo ≈ 5, and most are disqualified: Remarker/Kheopswap/ink!analyzer (already
ours), SubWallet (3 repos), KAGOME (whole C++ host, multi-ms), Substrate-Python (4 repos). **None had a clean
on-chain hours figure except Kheopswap (ours).** ⇒ **the on-chain retroactive vein is nearly exhausted** — our
7 actuals captured essentially all the clean single-repo logged-hours dev proposals. Realistic NEW gold here:
~1–3 marginal (SubWallet-isolated, cyclops #673, Telenova #611) requiring per-body verification.
**Therefore the scalable gold path is the GRANTEE SELF-REPORT SURVEY (task #35):** ask the teams of our already-
DELIVERED pilots for ACTUAL logged hours → converts planned→actual at scale (Boehm used surveys too). This
turns the 19 W3F delivered pilots into gold without hunting for non-existent on-chain-hours proposals.

**Parallel track — `treasury-mine` run #7 READ (2026-06-15):** manifest reached the **2024 range** (idx
~1583→544; our actuals #1170/#1102/#619 present → data is sound). **Finding:** the retroactive treasury vein
is **largely exhausted** of clean matched triples — the overwhelming majority are **tips / events / marketing**
(no repo, no effort table), and the few dev proposals are **multi-repo** (SubWallet #1118 = 3 repos) or already
admitted. Thin remaining single-repo leads to verify per-candidate (Subsquare API → state + on-chain hours
table): **LiteScan #970** (indexer), **Telenova #611** (Telegram wallet), **Polkawatch #1132** (analytics).
⇒ retroactive = diminishing returns; **W3F pre-screen v2 is the primary n-growth engine.**

### Pre-screen v2 — DEPLOYED (CI run #2, 2026-06-15)
v2 dispatched + ran (14 s). Raw census branch was CDN-cached to v1 schema at read time; v2 columns
(matched_app_file/app_pm/n_app_repos/ks_per_pm) will surface on next fetch. **From the v1 DELIVERED data in
hand**, the admit-ready **single-artifact** shortlist (delivery-verified · single node/pallet/library repo ·
census PM present · NEW project type) — deep-verify effort next, 3 at a time:

| candidate | census PM | eq KSLOC | ks/PM | type (new) | repo |
|---|---|---|---|---|---|
| **subcoin** | 3.0 | 10.99 | 3.7 | **Bitcoin-on-Substrate full node** | subcoin-project/subcoin |
| **myriad_social** | 9.0 | 5.20 | 0.58 | **social parachain** | myriadsocial/myriad-node-parachain |
| **melodot** | 6.75 | 13.94 | 2.07 | **data-availability layer** | ZeroDAO/melodot |
| gafi | 13.8 | 15.40 | 1.12 | gaming infra parachain | cryptoviet/gafi |
| fair_squares | 12.0 | 17.01 | 1.42 | real-estate DAO | Fair-Squares/fair-squares |
| NewOmega | 4.0 | 0.98 | 0.25 | on-chain game (exact commit) | WiktorStarczewski/newomega.polkadot |
All DELIVERED (pre-screen), all single-repo, all scope-sane (ks/PM 0.25–3.7). Next: pull v2 (fresh, not cached)
to grab each `matched_app_file`, confirm primary FTE×duration, admit the clean ones as #16+.

### Pre-screen v2 — BUILT (history)
`prescreen_delivery.py` upgraded: now also emits per grant **matched_app_file** (kills 404 filename churn),
**app_fte / app_months / app_pm** (PRIMARY effort straight from the application), **n_app_repos** (multi-repo
signal), and **ks_per_pm** scope ratio (informational warning, not auto-reject — reuse-heavy clean pilots run
low: pontem 0.14, skyekiwi 0.21). Effort-regex + scope logic validated locally (skyekiwi 8.0, stable-asset
2.0, hyperfridge 9.0→ks/pm 0.19, spacewalk terminated). **Next:** push → dispatch prescreen v2 → admit
straight from the ranked admit-ready shortlist (correct filename + app_pm + single-repo in hand).
