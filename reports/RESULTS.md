# Results — Blockchain-COCOMO

*Calibrating COCOMO II to actual blockchain-grant development effort. Corpus: n = 17 matched triples,
7 ecosystems. Repository: `Dr-CS9846/blockchain-effort-benchmark`.*

---

## 1. Research question

Can software effort for blockchain-domain development be estimated from code size, in the COCOMO II
tradition, using *actual reported effort* as ground truth?

This project builds (to our knowledge) the first actual-effort blockchain size→effort benchmark: a corpus
where each data point is a matched triple — {reported actual development effort, the single delivery
repository that produced it, a measured code size of that same artifact} — assembled with strict provenance
and calibrated with COCOMO II.

## 2. Methodology

### 2.1 The admission gate

Every calibration point must satisfy all of:
1. **Retroactive / delivered** — work is completed, not proposed or forward-funded.
2. **Actual reported effort in hours** — itemised in a source (final report, treasury/governance report), or
   cleanly derivable (stated hourly rate on separable dev labour). Not dollar-only figures, not FTE×duration
   budgets, not proposed grants.
3. **Software construction** — not audits, governance/ops, business development, or research datasets.
4. **A single, measurable delivery repository** — not PRs into an external monorepo, not closed source.

This gate is applied consistently and is the reason many candidate rows are rejected (§7).

### 2.2 Effort ground truth
Actual reported delivery effort (person-months, at Boehm's 152 h/PM convention). Git-reconstructed effort
and planned grant FTE are both explicitly rejected as ground truth (§4.1).

### 2.3 Size measurement
- **Whole-repo `cloc`** at the delivery commit for greenfield deliveries (pre-registered primary).
- **Window churn** (git added-lines over the funded period) for incremental work on long-lived repos
  (avoids counting years of prior code).
- **Reuse-adjusted equivalent SLOC** (CEVRP protocol) as a declared sensitivity, applied only to
  evidence-validated forks.

All sizes are measured in GitHub Actions CI (clone + `cloc`). Results are published to a `census` branch and
consolidated locally.

### 2.4 Reproducibility
Per-project drivers, sizes, churn and A_local are emitted to `reports/dissect_all.json` by a versioned CI
workflow (`dissect_pilot.yml`) driven by a plain-text spec (`data/calibration/pilots_cocomo.csv`). Every
effort figure traces to a live `source_url`.

## 3. Dataset

### 3.1 Cross-project calibration set — n = 17 distinct projects, 7 ecosystems

Ecosystems: Polkadot, Kusama, Moonbeam, Astar, Ethereum, Cosmos, æternity. Effort range 0.13 → 24.7 PM.

| # | project | ecosystem | PM (actual) | size basis |
|---|---|---|---|---|
| 1 | Subsquare (gov app) | Polkadot | 24.70 | window (12-mo funded slice) |
| 2 | DoDAO | Moonbeam | 18.95 | whole-repo |
| 3 | Ideal Network | Polkadot | 13.29 | whole-repo |
| 4 | Polkascan Explorer (3 repos summed) | Kusama | 11.63 | whole-repo |
| 5 | æternity JS SDK (aggregate, single dev) | æternity | 13.50 | window (Σ 7 quarters) |
| 6 | Octopus IBC bridge | Astar | 7.37 | whole-repo |
| 7 | Remarker | Polkadot | 7.24 | whole-repo |
| 8 | Kheopswap | Polkadot | 3.16 | whole-repo |
| 9 | ink! analyzer | Polkadot | 2.79 | whole-repo |
| 10 | dotreasury | Kusama | 0.95 | window (funded quarter) |
| 11 | DotCodeSchool | Polkadot | 0.95 | whole-repo |
| 12 | AEKnow (.org authored) | æternity | 1.00 | window |
| 13 | Gitorial | Polkadot | 0.55 | whole-repo |
| 14 | Referendum Alert | Kusama | 0.25 | whole-repo |
| 15 | RFC Bot | Polkadot | 0.21 | whole-repo |
| 16 | Kitdot | Polkadot | 0.13 | whole-repo |
| 17 | æternity Middleware `ae_mdw` (team of 2) | æternity | 20.08 | window (Σ 4 grant windows) |

**Notes on table composition:**
- **Point 17**: 3,052.5 h of per-person per-task weekly itemised hours across 4 consecutive grant windows
  (Dec 2022 – Oct 2023) on the single Elixir repo `aeternity/ae_mdw`; the 4 dependent windows collapse to
  one aggregate point and double as a second within-team longitudinal panel. Its LOOCV residual is mid-pack
  (≈57% MRE) — the pipeline generalises to a new team/language without special treatment. Sizing required a
  fix to the CI dissection tool: its source-file filter did not originally include Elixir (`.ex`/`.exs`),
  which silently zeroed the measured churn for this repo until corrected (verified against GitHub's own
  compare API; does not affect any other project in the spec).
- **æternity SDK aggregate**: all 7 quarters' churn measured. Σ = 2,052.6 h = 13.50 PM on 25.38 KSLOC summed
  window churn. The 7 dependent quarters collapse to this one independent point (no pseudo-replication).
- **TrueBlocks (Ethereum, 27.4 PM derived) is deliberately absent** from this table: held out as an
  out-of-domain external-validity check (`OOD_sensitivity` in the corpus ledger), not pooled into the
  Substrate-dominant primary set. Its hours are derived (2 FTE × duration), not itemised.
- **dotreasury and Subsquare are sized under the protocol-consistent (window) rule.** dotreasury's funded
  maintenance quarter (0.95 PM) is matched against CI-measured window churn (2.37 KSLOC), not the legacy
  72 KSLOC whole-repo figure; Subsquare's 12-month funded slice is matched against 76.9 KSLOC window churn,
  not the 235 KSLOC multi-year repo. At matched scope neither is an outlier. §4.2 quantifies the effect of
  this correction.
- **Kitdot remains the disclosed outlier** (20 h on a largely template-generated repo — a reuse/scaffold
  failure mode, not a scope mismatch; window-matching cannot fix it, the reuse-adjusted equivalent-SLOC
  track can). It is kept in the primary fit so reported accuracy is not curated upward.

### 3.2 Three within-project longitudinal panels
- **æternity JS SDK**: 7 quarterly reports, one developer (Denis Davidyuk), one repo — itemised hours.
- **æternity Middleware**: 4 grant windows of weekly per-person hours, one 2-dev team, one repo.
- **AEKnow**: weekly task-level reports, one developer (Liu Yang), two repos.

### 3.3 Broader tiered corpus
A 43-row reclassified corpus (`corpus_reclassified_offchain.csv`) records every candidate with a
source-verified `effort_type` (actual / cost-only / proposed / derived) and a `calib_eligible` flag, plus a
maintenance sub-corpus (Polkascan-PyAPI 21 quarters; Cosmos Hypha/Gaia) reserved for a hierarchical model,
and an infra/ops track (Stakeworld) held separate.

## 4. Results

### 4.1 Planned effort is size-decoupled; actual effort is not

On the large W3F planned-PM set (n=104), a size law degenerates: free-fit exponent E ≈ 0.10, SA 0.48,
PRED30 15% — grant FTE is set administratively, not by eventual code size. This is a clean negative result
and the reason the calibration rests on actual delivery effort rather than planned/budgeted effort.

### 4.2 Cross-project size→effort (actual effort, n=17) — the result of record

**PM = 0.28 · KSLOC^0.91, Pearson r = 0.73, LOOCV SA = +0.18, PRED(30) = 35%, MdMRE = 47%** (n = 17) — the
first positive-SA bare-law result on actual effort, under the protocol-consistent sizing rule: every point
sized at the scope its effort was reported for (whole-repo for greenfield deliveries; CI-measured window
churn for funded maintenance slices, exactly as each row's `sizing_mode` declares in `pilots_cocomo.csv`).
The free-fit exponent lands at E = 0.914 — consistent with COCOMO II's structural base exponent
(0.91 + 0.01·ΣSF) that this project had until now fixed by assumption; at n = 17 the CI on a free E is wide,
so this is convergence, not confirmation.

**Sensitivity (mixed-scope, disclosed):** the earlier tabulation carried two sizes that violated the spec's
own window rule (Subsquare's 12-month maintenance PM against the 235 KSLOC multi-year repo; dotreasury's
funded quarter against its 72 KSLOC whole repo). With those legacy whole-repo sizes the same n = 17 fit
gives A = 0.34, E = 0.76, r = 0.65, LOOCV SA = −0.12, PRED30 = 6% (and at n = 16, SA = −0.01, PRED30 = 12%).
The gap between the two fits — ≈0.30 of SA from scope-matching alone — is the quantified version of residual
cause (a) below and is itself a finding: *how you match effort-scope to code-scope dominates bare-law
accuracy at pilot n.*

The remaining residuals trace to three measurable causes: (a) effort-scope ≠ repo-scope (now the smallest,
post scope-matching), (b) template/generated repos vs tiny hours (Kitdot — still the worst residual,
retained and disclosed), (c) reuse/fork inflation (ink!-analyzer, Kheopswap — next in line for the
reuse-adjusted track). The size signal has strengthened monotonically as the clean set grew
(n=6 SA −0.05 → n=13 +0.12 → n=17 scope-matched +0.18), which is the empirical case for the dataset.

### 4.3 Full COCOMO II driver calibration — exploratory only

The full-driver COCOMO II calibration has not yet been re-run on the corrected n=17 set with pre-registered
sizes. There is therefore no current driver-calibrated accuracy claim; §4.2 is the result of record.

**Appendix — exploratory, retracted as a headline.** An earlier full-driver calibration on an n=8 "core"
reported A = 0.56 (95% CI [0.49, 0.65]), PRED(30) = 88%, MMRE 17%/20%. It was retracted as a headline for
two independent reasons: (i) **target contamination** — four of the eight points (megaclite, elara, fennel,
bagpipes) carried milestone/grant-reported or proposed PM with zero rows in the actual-effort master, the
exact planned-vs-actual error this project pivoted away from; and (ii) **provenance mismatch** — the
headline table used manually-chosen sizes that did not match the `equivalent_ksloc` produced by the cited
`dissect_all.json` pipeline run. The 88% figure survives only as the hypothesis that per-project driver and
reuse adjustment can absorb the §4.2 scatter; it requires re-validation at larger n with the pre-registered
size rule before any part of it is claimed.

### 4.4 Within-developer result — effort-per-line varies ~7× even under full control

On the æternity SDK panel (one developer, one repo, fixed language/toolchain), the same person ranges
28–201 h/KSLOC (≈7×) quarter to quarter — a controlled demonstration that effort-per-line is unstable even
when team, language, architecture and tooling are all fixed, the empirical argument for why effort
multipliers are necessary and a caution against git-churn-as-effort proxies.

With all 7 quarters measured, raw Pearson r(churn, hours) = +0.20 and ln–ln r = +0.64 — the sign is unstable
across subsamples of this panel (an earlier 5-quarter reading gave r = −0.25) and is not treated as a stable
claim in either direction. The 7× h/KSLOC swing is the robust result: it survives in every subsample. A
longer panel, or a second developer panel, is required before any churn↔hours correlation is asserted.

### 4.5 Statistical-rigor checks — scope disclosed per item

Computed on the exploratory n=8 core (§4.3 Appendix data) — not current claims: SA = 0.71 vs a
mean-predictor baseline; Wilcoxon vs classic A=2.94, p = 0.012. Both inherit the Appendix's target
contamination, and the A=2.94 comparison is additionally a weak strawman (any locally recalibrated constant
beats an uncalibrated 1990s constant). Superseded by the §4.2 result of record.

**Methodological findings that carry forward** (conclusions independent of the contaminated points):
- **Identifiability:** free-fit (A,E) are ~99% anti-correlated at pilot n — not separately identifiable —
  the rigorous justification for fixing E structurally (0.91 + 0.01·ΣSF) and calibrating only A
  (Boehm-faithful). Identifying E freely to ±0.1 needs ~100 matched triples.
- **Residual battery / sensitivity protocol** (heteroscedasticity, temporal-drift, Cook's-D influence, ±20%
  effort-perturbation): the procedures are established and scripted; they must be re-run on the n=17 set
  before their numeric outcomes are quoted.

## 5. Headline claims

1. First actual-effort blockchain size→effort benchmark: n = 17 projects, 7 ecosystems, every point
   source-cited.
2. Planned grant effort is size-decoupled (E≈0.10); actual effort is positively size-related (r≈0.65 in the
   mixed-scope reading, r=0.73 protocol-consistent) — the planned-vs-actual contrast is novel and defensible.
3. On the full actual-effort set (n=17) under the protocol-consistent sizing rule: PM = 0.28·KSLOC^0.91,
   r = 0.73, LOOCV SA = +0.18, PRED(30) = 35% — a real but still-modest bare-law baseline (Conte thresholds
   not yet met), with the mixed-scope sensitivity (SA = −0.12) disclosed alongside and the ≈0.30-SA gap
   between them quantifying the scope-matching effect (§4.2). The full-driver Blockchain-COCOMO remains an
   exploratory hypothesis only (§4.3) pending re-validation with pre-registered sizes.
4. A controlled within-developer result: the same developer's effort-per-KSLOC swings ~7× quarter-to-quarter
   under fixed team/language/toolchain, motivating multivariable models. (The churn↔hours correlation claim
   is withdrawn — sign-unstable at panel n; see §4.4.)

## 6. Limitations

- **Pilot scale.** The clean matched core is small (n≈6–17); this is a proof-of-concept, not a
  production-grade calibration. E cannot be freely estimated to ±0.1 at this n (needs ~100 matched triples);
  E is therefore fixed structurally and A is calibrated, per Boehm.
- **Size-measurement sensitivity is the dominant uncertainty**, not the model — reuse, generated/scaffold
  code, multi-repo projects, and effort-scope vs repo-scope mismatches drive the residual scatter.
- **Mixed size bases**: 14 greenfield points use whole-repo `cloc`; the remaining points (æternity SDK,
  æternity Middleware, AEKnow, dotreasury, Subsquare) use window churn (the matched scope). Consistent
  per-project.
- AEKnow.chain's repo is vendored-inflated (165.5 KSLOC for a 1-PM combined grant), so AEKnow is sized by
  its authored `.org` component only (7.19 KSLOC) — disclosed, not silently corrected.
- **Kitdot is a retained, disclosed outlier** (see §3.1 notes): kept in the fit so accuracy is not curated
  upward; the reuse-adjusted equivalent-SLOC track is the intended remedy.
- **Effort is self-reported** by grantees in final reports (mitigated by a ±20% sensitivity analysis).

## 7. Rejected candidates (gate integrity)

Consistently excluded, with reasons: dollar-only treasury proposals (SubWallet, Integritee, PolkaGate, SQD);
FTE-budget/forward proposals (Cosmos Prop-839, Hydro, Maker Core-Unit budget); audits (Trail-of-Bits Nitro —
that's auditor effort, not developer effort); PRs into external monorepos (CoW Swap, Polkadot-SDK Assets);
closed source (Subscan); research datasets (DAppSCAN); and fabricated "illustrative" rows with placeholder
URLs. This discipline is what makes the admitted n credible.

## 8. Roadmap

1. Grow the actual-effort matched set toward n≈30 (the single highest-value action; the æternity
   "[Completed]" grant vein and the broader gov2 referendum sweep are repeatable sources).
2. Reuse-corrected + full-driver fit on the current n=17 (upper-track vs the bare-law lower bound).
3. Data paper first (the corpus + provenance + planned-vs-actual finding), then the pilot calibration paper
   (A≈0.56, within-developer result), then multivariable driver estimation.
4. Housekeeping for citability: v0.1 tagged release/DOI; refresh datasheet/source-map; lock the size→effort
   claim in the provenance ledger.

## 9. Provenance / where to look

- Calibration set: `data/calibration/pilots_cocomo.csv`, `calibration_set_primary.csv`
- Reclassified corpus: `data/calibration/corpus_reclassified_offchain.csv`
- Per-project measurements: `reports/dissect_all.json`
- Figures: `reports/figures/` (parity plots, joint (A,E) region, within-project panel)
