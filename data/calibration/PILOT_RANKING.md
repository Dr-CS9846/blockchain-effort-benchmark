# Verified-pilot authenticity ranking — order for one-by-one COCOMO II dissection

Goal: make **PM(COCOMO II) = PM(reported)** hold for each pilot, dissected one at a time, most
authentic first. "Authenticity" here = how trustworthy the matched triple is for calibration, scored on:

- **Effort actuality** — ACTUAL (retroactive, completed-work) > mixed > PROPOSED (forward estimate).
- **Effort granularity** — itemised multi-workstream hours > FTE+rate+hours / dev-weeks > single lump.
- **Size measurability** — the cleaner the matched artifact, the more trustworthy the COCOMO size:
  exact developer-provided diff ≈ greenfield whole-repo > windowed slice > multi-component.
- **On-chain proof** — Executed/Awarded on-chain (10) vs W3F milestone delivery (2).

Both axes matter for PM=PM: authentic *effort* AND measurable *size*. The order below sorts by effort
authenticity first, then breaks ties by size measurability (so the first specimens also have the
cleanest, least-disputable size).

| Order | # | Pilot | Reported PM | Effort | Granularity | Size mode (measurability) | Proof |
|---|---|---|---|---|---|---|---|
| **1** | 12 | **ink! analyzer** | 2.79 | **ACTUAL** | **itemised (8 tasks)** | windowed slice — v5 diff, defined window + release boundary | on-chain |
| 2 | 1 | Subsquare (maint.) | 24.7 | ACTUAL | itemised (8 tasks) | windowed slice — 12-mo window of a large repo (hardest) | on-chain |
| 3 | 4 | dotreasury | 0.95 | ACTUAL | itemised (small) | **exact diff `e8f09bf…release-2.3.1`** (zero ambiguity) | on-chain |
| 4 | 11 | Kheopswap | 3.16 | ACTUAL | single figure (480 h) | **greenfield whole-repo** (clean) | on-chain |
| 5 | 13 | Dot Code School | 0.95 | ACTUAL | FTE+rate+hours (144 h) | greenfield whole-repo (small) | on-chain |
| 6 | 10 | Remarker | 7.24 | ACTUAL | single figure (1100 h) | single-repo dApp at date (reuse risk) | on-chain |
| 7 | 6 | Subsquare (new-feat.) | 11.4 | mixed (mostly proposed) | itemised | windowed slice (same repo as #1) | on-chain |
| 8 | 8 | Elara | 4.6 | PROPOSED | itemised dev-weeks | greenfield whole-repo | on-chain |
| 9 | 2 | Ask! v0.1 | 6.9 | PROPOSED | dev-weeks | greenfield whole-repo | on-chain |
| 10 | 5 | Megaclite | 3.45 | PROPOSED | dev-weeks | greenfield whole-repo | on-chain |
| 11 | 3 | Bagpipes | 9.97 | PROPOSED | itemised (4 milestones) | single-repo dApp | on-chain |
| 12 | 9 | ParaSpell | 2.0 | PROPOSED | FTE×duration | greenfield whole-repo | W3F |
| 13 | 7 | Fennel Protocol | 9.0 | PROPOSED | FTE×duration | multi-repo (chain+lib+cli) | W3F |

## First specimen — Pilot 12, ink! analyzer

Chosen first because it is the **most authentic effort report in the set**: the developer's own
**itemised actual hours** (8 workstreams, ~424 h) for completed, retroactively-funded work, on a single
primary repo, independent author, Executed on-chain. Its size is a **windowed slice** (the ink! v5
support increment, ~Sep 2023 → Mar 2024 release) — tractable via `git log` over the window.

Per-project method (what "find its exact PM through COCOMO II" means here):
1. **Measure size** of the matched slice → KSLOC, then reuse-adjusted **equivalent SLOC**.
2. **Assign the 22 COCOMO II drivers** (5 SF + 17 EM) from objective repo signals, **hand-correcting
   from proposal/domain evidence** where the auto-signal is blind (e.g. ink! analyzer is a
   compiler-frontend/LSP — high CPLX from parser/IR/semantic-analysis, but it is *not* on-chain, so the
   blockchain EMs are Nominal). Every non-Nominal rating must cite evidence.
3. **Compute** E = 0.91 + 0.01·ΣSF, ∏EM, and PM_pred = A·Size^E·∏EM with the published **A = 2.94**.
4. **Reconcile to PM=PM**: report the **local A** that makes PM_pred = reported PM exactly, i.e.
   A_local = reported_PM / (Size^E·∏EM). PM=PM holds by construction *per project*; the scientific
   result is whether A_local lands near 2.94 (and near the other pilots' A_local) — a tight cluster of
   A_local across this clean curated set is what justifies one calibrated Blockchain-COCOMO constant.

Honest note: for any single project PM=PM is achievable exactly by the local A. The rigor — and the PhD
contribution — is that with **honest size** and **evidence-justified drivers** on a **clean matched
triple**, the per-project A_locals form a tight, defensible cluster. We do them one at a time so each
A_local is trustworthy before it joins the cluster.
