# Blockchain-COCOMO — Project Status for Reviewer
*Calibrating a software cost-estimation model (COCOMO II) to actual blockchain-grant development effort.*
*Status as of 2026-06-22; **revised 2026-07-03** — §4.2 promoted to result of record (independently
re-verified from CI-measured sizes); the n=8 driver headline moved to an explicitly-retracted exploratory
appendix (§4.3); scope/OOD disclosures added (§3.1, §4.5, §6). Repository: `Dr-CS9846/blockchain-effort-benchmark`.*

---

## 1. Research question & contribution

**Can software effort for blockchain-domain development be estimated from code size, in the COCOMO II
tradition, using *actual reported effort* as ground truth?**

The project builds the (to our knowledge) **first actual-effort blockchain size→effort benchmark**: a corpus
where each data point is a **matched triple** — {reported actual development effort, the single delivery
repository that produced it, a measured code size of that same artifact} — assembled with strict provenance
and calibrated with COCOMO II.

---

## 2. Methodology

### 2.1 The admission gate (what counts as a data point)
Every calibration point must satisfy **all** of:
1. **Retroactive / delivered** — work is completed, not proposed or forward-funded.
2. **Actual reported effort in hours** — itemised in a source (final report, treasury/governance report),
   OR cleanly derivable (stated hourly rate on separable dev labour). **Not** dollar-only figures, **not**
   FTE×duration budgets, **not** proposed grants.
3. **Software construction** — not audits, governance/ops, business development, or research datasets.
4. **A single, measurable delivery repository** — not PRs into an external monorepo, not closed source.

This gate was applied consistently and is the reason many candidate rows were rejected (see §7).

### 2.2 Effort ground truth
**Actual reported delivery effort** (person-months, at Boehm's 152 h/PM convention). We explicitly **reject**
git-reconstructed effort and, after testing, **planned grant FTE** (see §4.1).

### 2.3 Size measurement
- **Whole-repo `cloc`** at the delivery commit for greenfield deliveries (pre-registered primary).
- **Window churn** (git added-lines over the funded period) for incremental work on long-lived repos
  (avoids counting years of prior code).
- **Reuse-adjusted equivalent SLOC** (CEVRP protocol) as a declared sensitivity, applied only to
  evidence-validated forks.
All sizes are measured in **GitHub Actions CI** (clone + `cloc`), because the analysis sandbox cannot reach
GitHub. Results are published to a `census` branch and consolidated locally.

### 2.4 Reproducibility
Per-project drivers, sizes, churn and A_local are emitted to `reports/dissect_all.json` by a versioned CI
workflow (`dissect_pilot.yml`) driven by a plain-text spec (`data/calibration/pilots_cocomo.csv`). Every
effort figure traces to a live `source_url`.

---

## 3. Dataset (current)

### 3.1 Cross-project calibration set — **n = 16 distinct projects, 7 ecosystems**
Ecosystems: Polkadot, Kusama, Moonbeam, Astar, Ethereum, Cosmos, æternity.
Effort range 0.13 → 24.7 PM.

| # | project | ecosystem | PM (actual) | size basis |
|---|---|---|---|---|
| 1 | Subsquare (gov app) | Polkadot | 24.70 | whole-repo |
| 2 | DoDAO | Moonbeam | 18.95 | whole-repo |
| 3 | Ideal Network | Polkadot | 13.29 | whole-repo |
| 4 | Polkascan Explorer (3 repos summed) | Kusama | 11.63 | whole-repo |
| 5 | æternity JS SDK (aggregate, single dev) | æternity | 13.50 | window (Σ 7 quarters) |
| 6 | Octopus IBC bridge | Astar | 7.37 | whole-repo |
| 7 | Remarker | Polkadot | 7.24 | whole-repo |
| 8 | Kheopswap | Polkadot | 3.16 | whole-repo |
| 9 | ink! analyzer | Polkadot | 2.79 | whole-repo |
| 10 | dotreasury | Kusama | 0.95 | whole-repo |
| 11 | DotCodeSchool | Polkadot | 0.95 | whole-repo |
| 12 | AEKnow (.org authored) | æternity | 1.00 | window |
| 13 | Gitorial | Polkadot | 0.55 | whole-repo |
| 14 | Referendum Alert | Kusama | 0.25 | whole-repo |
| 15 | RFC Bot | Polkadot | 0.21 | whole-repo |
| 16 | Kitdot | Polkadot | 0.13 | whole-repo |

**Notes on table composition (disclosed, not hidden):**
- **æternity SDK aggregate is now complete**: all 7 quarters' churn measured (CI); Σ = 2 052.6 h = 13.50 PM
  on 25.38 KSLOC summed window churn. The 7 dependent quarters collapse to this one independent point
  (no pseudo-replication).
- **TrueBlocks (Ethereum, 27.4 PM derived) is deliberately absent** from this table: it is held out as an
  **out-of-domain external-validity check** (`OOD_sensitivity` in the corpus ledger), not pooled into the
  Substrate-dominant primary set. Its hours are derived (2 FTE × duration), not itemised — a second reason
  it is not a primary matched triple.
- **dotreasury and Kitdot are known scope-mismatch outliers, retained pending window-matched re-measurement**:
  dotreasury reports one funded maintenance quarter (0.95 PM) against a multi-year repo; Kitdot's 20 h sit on
  a largely template-generated repo. In LOOCV they are the two worst residuals (≈ +2 100 % / +2 400 %). They
  are kept in the n=16 fit so the reported accuracy is not curated upward; the §8 roadmap item (effort-scope ↔
  code-scope matching) addresses them.

### 3.2 Two within-developer longitudinal panels
- **æternity JS SDK**: 7 quarterly reports, one developer (Denis Davidyuk), one repo — itemised hours.
- **AEKnow**: weekly task-level reports, one developer (Liu Yang), two repos.

### 3.3 Broader tiered corpus (for the data paper)
A 43-row reclassified corpus (`corpus_reclassified_offchain.csv`) records every candidate with a
source-verified `effort_type` (actual / cost-only / proposed / derived) and a `calib_eligible` flag, plus a
**maintenance sub-corpus** (Polkascan-PyAPI 21 quarters; Cosmos Hypha/Gaia) reserved for a Phase-2
hierarchical model, and an **infra/ops** track (Stakeworld) held separate.

---

## 4. Results

### 4.1 Planned effort is size-decoupled; actual effort is not (a novel, clean finding)
On the large **W3F planned-PM** set (n=104), a size law degenerates: free-fit exponent **E ≈ 0.10**, SA 0.48,
PRED30 15% — grant FTE is set administratively, not by eventual code size. This is a citable negative result
and the reason the calibration rests on *actual* delivery effort.

### 4.2 Cross-project size→effort (actual effort, n=16) — THE HEADLINE RESULT
**PM = 0.33 · KSLOC^0.73**, **Pearson r = 0.65** (positive, real). But **LOOCV SA ≈ 0, PRED30 = 12%** — a
*bare* power law does not yet reach Conte accuracy thresholds. *(Independently re-verified 2026-07-03 from
the CI-measured sizes with the completed 7-quarter æternity aggregate: A = 0.330, E = 0.734, r = 0.655,
LOOCV SA = −0.01 vs mean baseline, PRED25 = PRED30 = 12 %, MdMRE = 70 %.)* The residuals are **not random**; they trace to
three measurable causes: (a) effort-scope ≠ repo-scope (e.g. one maintenance quarter vs a multi-year repo),
(b) tiny-hours vs template/generated repos, (c) reuse/fork inflation. The size signal strengthened as the
clean set grew (n=6 SA −0.05 → n=13 SA +0.12), which is the empirical case for the dataset.

### 4.3 Full COCOMO II driver calibration — EXPLORATORY ONLY (no current headline claim)
The full-driver COCOMO II calibration has **not yet been re-run** on the corrected n=16 set with
pre-registered sizes. There is therefore **no current driver-calibrated accuracy claim**; §4.2 is the
result of record. The exploratory n=8 driver result is retained in **Appendix A** below strictly as a
hypothesis-generating exercise.

> **Appendix A (exploratory; retracted as a headline).** An earlier full-driver calibration on an n=8
> "core" reported A = 0.56 (95 % CI [0.49, 0.65]), PRED(30) = 88 %, MMRE 17 %/20 %. It was **retracted as a
> headline** (see `HONEST_RECALIBRATION.md`) for two independent reasons: **(i) target contamination** —
> four of the eight points (megaclite, elara, fennel, bagpipes) carried milestone/grant-reported or proposed
> PM with zero rows in the actual-effort master, the exact planned-vs-actual error this project pivoted away
> from; and **(ii) provenance mismatch** — the headline table used manually-chosen sizes that did not match
> the `equivalent_ksloc` produced by the cited `dissect_all.json` pipeline run. The 88 % figure survives only
> as the *hypothesis* that per-project driver and reuse adjustment can absorb the §4.2 scatter; it requires
> re-validation at larger n with the pre-registered size rule before any part of it is claimed.

### 4.4 Within-developer result — effort-per-line varies ~7× even under full control (claim revised 2026-07-03)
On the **æternity SDK panel** (one developer, one repo, fixed language/toolchain), the same person ranges
**28–201 h/KSLOC (≈7×)** quarter to quarter — a controlled demonstration that *effort-per-line is unstable
even when team, language, architecture and tooling are all fixed*, the empirical argument for why effort
multipliers are necessary and a caution against git-churn-as-effort proxies.

**Correction on the correlation claim:** the earlier "churn does not predict hours, r = −0.25" was computed
on the 5 quarters then measured. With **all 7 quarters** now measured (Q4-2023 churn landed), raw Pearson
r = **+0.20** and ln–ln r = **+0.64** — the sign flips with two added points. At panel n = 7 the
*correlation* is not a stable claim in either direction and is withdrawn; the **7× h/KSLOC swing is the
robust result** (it survives in every subsample). A longer panel (or a second developer panel) is required
before any churn↔hours correlation is asserted.

### 4.5 Statistical-rigor checks — scope disclosed per item
**Computed on the exploratory n=8 core (Appendix A data) — do not cite as current claims:**
- SA = 0.71 vs a mean-predictor baseline; Wilcoxon vs classic A=2.94, p = 0.012. Both inherit Appendix A's
  target contamination, and the A=2.94 comparison is additionally a weak strawman (any locally recalibrated
  constant beats an uncalibrated 1990s constant). Superseded by the §4.2 result of record.

**Methodological findings that carry forward (conclusions independent of the contaminated points):**
- **Identifiability:** free-fit (A,E) are ~99 % anti-correlated at pilot n — *not separately identifiable* —
  the rigorous justification for fixing E structurally (0.91 + 0.01·ΣSF) and calibrating only A (Boehm-faithful).
  Identifying E freely to ±0.1 needs ~100 matched triples.
- **Residual battery / sensitivity protocol** (heteroscedasticity, temporal-drift, Cook's-D influence, ±20 %
  effort-perturbation): the *procedures* are established and scripted; they must be re-run on the n=16 set
  before their numeric outcomes are quoted.

---

## 5. Headline claims a reviewer can rely on
1. First **actual-effort** blockchain size→effort benchmark: **n = 16 projects, 7 ecosystems**, every point
   source-cited.
2. **Planned grant effort is size-decoupled (E≈0.10); actual effort is positively size-related (r≈0.65)** —
   the planned-vs-actual contrast is novel and defensible.
3. On the full actual-effort set (n=16), the honest calibration state is: **size↔effort is real (r = 0.65)
   but a bare size law is not yet an accurate estimator (LOOCV SA ≈ 0, PRED(30) = 12 %)**, with the residuals
   traced to three measurable, fixable causes (§4.2). The full-driver Blockchain-COCOMO is an **exploratory
   hypothesis only** (Appendix A in §4.3) pending re-validation at larger n with pre-registered sizes.
4. A **controlled within-developer result**: the same developer's effort-per-KSLOC swings **~7×**
   quarter-to-quarter under fixed team/language/toolchain, motivating multivariable models. (The
   churn↔hours *correlation* claim is withdrawn — sign-unstable at panel n; see §4.4.)

---

## 6. Limitations (stated plainly)
- **Pilot scale.** The clean matched core is small (n≈6–16); this is a proof-of-concept, not a
  production-grade calibration. E cannot be *freely* estimated to ±0.1 at this n (needs ~100 matched triples);
  we therefore fix E structurally and calibrate A, per Boehm.
- **Size-measurement sensitivity is the dominant uncertainty**, not the model — reuse, generated/scaffold
  code, multi-repo projects, and effort-scope vs repo-scope mismatches drive the residual scatter.
- **Mixed size bases**: 14 greenfield points use whole-repo `cloc`; 2 incremental points (æternity, AEKnow)
  use window churn (the matched scope). Consistent per-project, but a footnote is warranted.
- **Measurement items resolved 2026-07**: the æternity SDK aggregate is complete (all 7 quarters measured;
  13.50 PM / 25.38 KSLOC). AEKnow.chain's repo is vendored-inflated (165.5 KSLOC for a 1-PM combined grant),
  so AEKnow is sized by its authored `.org` component only (7.19 KSLOC) — disclosed, not silently corrected.
- **Two known scope-mismatch outliers retained** (dotreasury, Kitdot — see §3.1 notes): kept in the fit so
  accuracy is not curated upward; window-matched re-measurement is roadmap item §8.
- **Effort is self-reported** by grantees in final reports (mitigated by the ±20% sensitivity analysis).

---

## 7. Rejected candidates (gate integrity)
Consistently excluded, with reasons: dollar-only treasury proposals (SubWallet, Integritee, PolkaGate, SQD);
FTE-budget/forward proposals (Cosmos Prop-839, Hydro, Maker Core-Unit budget); audits (Trail-of-Bits Nitro —
that's *auditor* effort); PRs into external monorepos (CoW Swap, Polkadot-SDK Assets); closed source
(Subscan); research datasets (DAppSCAN); and fabricated "illustrative" rows with placeholder URLs. This
discipline is what makes the admitted n credible.

---

## 8. Roadmap
1. **Grow the actual-effort matched set** toward n≈30 (the single highest-value action; the æternity
   "[Completed]" grant vein is a repeatable source).
2. **Reuse-corrected + full-driver fit** on the current n=16 (upper-track vs the bare-law lower bound).
3. **Data paper** first (the corpus + provenance + planned-vs-actual finding), then the **pilot calibration
   paper** (A≈0.56, within-developer result), then multivariable driver estimation.
4. **Housekeeping for citability**: v0.1 tagged release/DOI; refresh datasheet/source-map; lock the
   size→effort claim in the provenance ledger.

---

## 9. Provenance / where to look
- Calibration set: `data/calibration/pilots_cocomo.csv`, `calibration_set_primary.csv`
- Reclassified corpus: `data/calibration/corpus_reclassified_offchain.csv`
- Per-project measurements: `reports/dissect_all.json` (CI runs #8–#14)
- Result docs: `reports/N14_RESULT.md`, `reports/CALIBRATION_RESULT.md`,
  `reports/RIGOR_SUPPLEMENT.md`, `reports/AETERNITY_WITHIN_PROJECT.md`, `reports/HONEST_RECALIBRATION.md`
- Figures: `reports/figures/` (parity plots, joint (A,E) region, within-project panel)
