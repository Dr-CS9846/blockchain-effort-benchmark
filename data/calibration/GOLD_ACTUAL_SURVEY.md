# Gold-Actuals Survey — convert Extended (planned) pilots → Gold (actual)
*The only sanctioned way to grow the GOLD core: ask each delivered team for the **hours actually logged** on the
funded work. A confirmed actual figure promotes the pilot Extended→GOLD. Draft + queued — nothing sent without
per-batch PI approval. Date: 2026-06-15.*

## Why
The GOLD core (actual logged effort) = 6 pilots; that is enough to calibrate ("even 5 would work"), but more
gold tightens the constant. We will NOT add more planned pilots. Instead we convert the 80 Extended (delivered)
pilots to gold one author-reply at a time. This is standard practice (Boehm calibrated on surveyed effort).

## Survey email (T-ACTUAL)
**Subject:** One number for an academic study — actual dev hours on {{project}}?

Hi {{name}},

I'm a PhD researcher building an open, auditable dataset that calibrates software cost models (COCOMO II) to
real blockchain development. **{{project}}** is in it, and it was delivered/accepted — congratulations.

Our record currently uses the **budgeted** figure from the grant ({{planned_effort}}). For the study I need the
**actual effort** — roughly **how many person-hours (or person-months) your team actually spent** building the
funded deliverable ({{repo}})? A single honest number (even ±20%) is perfect; an itemised breakdown is a bonus.

I'll attribute or anonymise as you prefer, and I'm glad to share your entry and the final results. Thank you.

{{researcher}} · {{affiliation}}

## Status fields (per pilot)
`survey_status: unsent → emailed → actual-confirmed(→GOLD) → no-response`  ·  `actual_hours` · `actual_pm`

## Priority targets (Extended pilots with a contact already captured — email these first)
| pilot | planned PM | contact | likelihood |
|---|---|---|---|
| #7 Fennel | 9.0 | info@fennellabs.com | active team |
| #14 Pontem | 13.3 | boris@dfinance.co | active (Pontem/Aptos) |
| #15 SkyeKiwi | 8.0 | song.zhou@skye.kiwi | solo, reachable |
| #16 Stable Asset | 2.0 | terry@nuts.finance | active (NUTS) |
| #17 Subcoin | 3.0 | xuliuchengxlc@gmail.com | solo (Liu-Cheng Xu), very reachable |
| #22 NewOmega | 4.0 | celrisen@gmail.com | solo (Wiktor) |
| #29 Decentralized Threshold Signing | 3.0 | ruipedromorais11@gmail.com (GitHub fiono11) | solo academic, reachable |
| #30 Aisland DocSig | 3.0 | admin@aisland.io | active team |
| #3 Bagpipes | 9.97 | via Decentration/Medium + GitHub | reachable |
| #2/#5/#8 Patract (Ask!/Megaclite/Elara) | — | GitHub patractlabs | low (org inactive) |

**Next-wave targets:** the #32–87 teams — capture each `contact` from its W3F application (the application lists
a Contact Email) before emailing. ~1 lookup per pilot; batch via GitHub-issue where no email is public (same
channel pattern as the earlier verification outreach).

## Sending rules
- Email everyone we want to convert; one follow-up (+10 days) to non-responders, then leave Extended.
- `actual-confirmed` → set actual_hours/actual_pm, **promote pilot to GOLD**, log the change + correspondence.
- Draft + queue only — PI approves each batch before send.
