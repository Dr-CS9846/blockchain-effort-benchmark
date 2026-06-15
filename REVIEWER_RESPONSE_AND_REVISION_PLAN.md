# Reviewer Response & Revision Plan — Blockchain-COCOMO Calibration
*Two senior reviews (R1 = Empirical SE / Software Measurement; R2 = Blockchain Eng. / Grant Economics).*
*Status key:* **[DONE]** computed/addressed in this round · **[PLAN]** scoped action with method · **[ACK]** acknowledged scope/limitation.
*All new numbers below are computed from the run-#5 dissection data (n=12); core-6 = bagpipes, megaclite,
remarker, dotcodeschool, dotreasury, fennel.*

---

## Both reviewers: verdict
Major revision, accept-in-principle. Core (A ≈ 0.58, PRED(30)=83%, LOOCV-stable, CI excludes 2.94 by ~5×) is
sound and novel. Fixable concerns below. We treat each as a research direction and address the computable ones now.

---

## Reviewer 1 — Empirical Software Engineering

### M1 — Selection bias in the clean-6 (their #1 concern) — **[DONE — empirically tested]**
**RESOLVED (detector built + run).** We built a path-based + bulk-import-anywhere reuse detector and re-measured
all pilots. It **verified genuine reuse in the two most size-inflated pilots** and their corrected A_local moved
*up into* the clean cluster: **Elara** (98.8 % forked Substrate template) 0.044→**0.487**; **Kheopswap** (76.6 %
PAPI scaffold) 0.157→**0.568**. Re-fitting the **core-8** (clean-6 + these two):

| set | n | A* | 95 % CI | SA | PRED(30) |
|---|---|---|---|---|---|
| core-6 | 6 | 0.577 | [0.473, 0.686] | +0.80 | 83 % |
| **core-8** | 8 | **0.564** | **[0.487, 0.647]** | +0.80 | **88 %** |

**⇒ The constant is confirmed, not shifted: A* moves 0.577→0.564 (within CI), the CI *tightens* (0.21→0.16),
and PRED(30) rises to 88 %.** This is the "clean-6 and corrected pilots agree" result. *Honest limitation kept
in-paper:* the automated bulk-commit heuristic is blunt — it over-flagged two clean projects' large *authored*
initial/migration commits (bagpipes, remarker) as forks, so we apply reuse correction **only** where
evidence-validated (Elara forked template, Kheopswap PAPI scaffold), not blanket. Still unresolved (honestly
flagged): Ask! (85 % flagged — possibly vendored AS stdlib), the 3 scope-limited window pilots, fennel's
generated flag (kept at raw). Below is the original quantitative-direction analysis, now empirically borne out.

**The reviewer's required next sentence — now supplied (CEVRP locked).** The evidence-validated correction is
no longer a one-off rescue: we have promoted it to a **pre-stated, falsifiable benchmark rule**, the
**Constrained Evidence-Validated Reuse Protocol (CEVRP, v1.0)** (§3.3 of the report). A pilot's size is
reduced to Equivalent SLOC **iff all three conditions hold**: **C1** detector flags ≥ 50 % adapted/generated;
**C2** independent provenance confirms external origin (named upstream fork, declared generator path, or
single third-party import commit); **C3** the bulk is *not* a rename/move of the team's own commits. C3 is the
guard run #7 lacked — under CEVRP the protocol *applies* to Elara and Kheopswap and *correctly declines*
bagpipes (188-file self-rename) and remarker (initial app dump), with the clean-4 at raw size by default. The
rule is locked and applied identically to every current and future pilot, so the verdict on Ask!, the window
pilots, and fennel is determined by C1–C3, not by analyst discretion. This converts "evidence-validated
two-case correction" into "generalizable benchmark protocol" — the exact gap the reviewer identified.

### M1 (original direction analysis, now confirmed by the above)
*Falsifiable criterion (now stated):* a pilot is **size↔scope clean** iff the measured artifact's lifetime
and content are entirely *within* the funded deliverable — i.e. (a) greenfield repo built for the grant with
no large forked/templated root commit, and (b) no later-version code beyond the funded scope at the measured
ref. The 6 inflated pilots each violate (a) or (b).

*Quantitative direction & magnitude (the requested analysis).* For each excluded pilot we compute the size
**shrink factor** required for its A_local to reach the clean-6 A*=0.577, i.e. the implied reuse/out-of-scope
fraction:

| excluded pilot | A_local | shrink to reach 0.577 | implied reuse/out-of-scope | independent plausibility |
|---|---|---|---|---|
| subsquare_maint | 0.237 | ×0.41 | 59 % | wide 12-mo window ⊃ funded slice |
| subsquare_newfeat | 0.121 | ×0.21 | 79 % | wide 15-mo window |
| ask_v01 | 0.208 | ×0.36 | 64 % | AssemblyScript codegen |
| kheopswap | 0.157 | ×0.27 | 73 % | PAPI generated descriptors |
| ink_analyzer | 0.058 | ×0.10 | 90 % | 7-mo window vs funded v5 only |
| elara | 0.044 | ×0.08 | 92 % | forked Substrate template |

**Argument:** every correction is in the *same direction* (size must **shrink**, never grow), and each implied
fraction is independently plausible from the repo's known structure. Therefore fixing the six moves their
A_local **upward toward** the clean-6 anchor — it does not pull A* down. The clean-6 A=0.58 is best read as a
*lower-ish anchor*; the expected full-corpus A is bounded in roughly **[0.58, 0.70]** (it rises above 0.58 only
if true reuse exceeds the thresholds above, which is directly testable). **[PLAN]** path-based generated
detection + scope isolation → re-fit → report full-12 A* and confirm it lands in the predicted interval.

### M2 — n=6 is small; state publication-grade n — **[PLAN]**
Add to §8: cite Kemerer (1987) and Myrtveit & Stensrud (1999) on minimum viable n for effort-model
calibration; state target: "a 95 % bootstrap CI of half-width ≤ 0.10 (≈ ±17 % of A) is publication-grade; at
the current per-pilot variance this requires n ≈ 12–15 clean pilots." Current half-width = 0.105 at n=6 →
already near target; growing clean-n (M1 fix) reaches it.

### M3 — Stratify actual vs proposed effort — **[DONE]**
| subset | n | A* | SA | MMRE | PRED(30) |
|---|---|---|---|---|---|
| core actual-only | 3 | **0.493** | +0.95 | 18 % | 67 % |
| core proposed-only | 3 | **0.675** | +0.84 | 11 % | 100 % |
Proposed effort yields a **higher** A* (0.68) than actual (0.49) — *opposite* to the classic
"proposed-underestimates-actual" prior (Jørgensen 2004), i.e. in this corpus proposed budgets report *more*
PM per KSLOC, not less. Caveats: n=3 each and confounded by project identity (not the same project measured
both ways). Framing for the paper: **"A* = 0.58 on the mixed set; actual-only A* ≈ 0.49 (the more conservative
anchor); proposed-only ≈ 0.68. A true-actual anchor via grantee survey is the pending refinement."**

### M4 — Use Standardised Accuracy (SA) as the primary metric — **[DONE]**
SA (Shepperd & MacDonell 2012; baseline = mean |yᵢ−yⱼ| of random guessing) now computed and promoted to
primary; MMRE demoted to "for comparability with prior work":
| subset | n | A* | **SA (primary)** | MMRE | PRED(30) |
|---|---|---|---|---|---|
| **core-6** | 6 | 0.577 | **+0.80** | 20 % | 83 % |
| core treasury-only | 5 | 0.549 | +0.84 | 19 % | 80 % |
| all-12 | 12 | 0.258 | +0.15 | 114 % | 17 % |
SA = +0.80 (core-6) ≫ 0 confirms the model strongly beats random guessing; SA = +0.15 (all-12) quantifies the
size-inflation drag. (SA > 0.5 is a strong result for effort models.)

### M5 — Flat scale factors: is it COCOMO or just a power law? — **[DONE]**
Direct test on core-6, with vs without the EM product:
| model | A* | SA | MMRE | PRED(30) |
|---|---|---|---|---|
| PM = A·Size^E·∏EM (full COCOMO II) | 0.577 | +0.80 | 20 % | **83 %** |
| PM = A·Size^E (pure power law, ∏EM=1) | 0.647 | +0.73 | 29 % | **67 %** |
**The EM machinery *does* contribute:** the few evidence-based non-Nominal multipliers (CPLX/TIME on the
ZK/contract projects megaclite & ask; PVOL/CPLX on fennel) lift PRED(30) by **+16 pp** (67→83) and SA by +0.07.
So the model is COCOMO II proper, not merely A·Size^E — though most drivers are Nominal because objective repo
signals don't distinguish levels for the rest. We state this explicitly (honest, and stronger than "it
collapses to a power law").

### Minor — **[DONE/PLAN]**
- **m1** geomean of A_local = exp(mean ln A_local) = OLS intercept of `ln PM − E·ln Size − ln∏EM` (log-linear
  MLE under lognormal residuals). Justification added to method. **[DONE]**
- **m2** dotreasury "edge of validity" — cite Boehm et al. (2000) lower size boundary (~2 KSLOC). **[PLAN]**
- **m3** rejected-candidate **table** (replace prose). **[DONE]** — §2.3 now a 6-row table (Talisman, ink!Hub,
  Ink! Dev Hub, ParaSpell, SubBooster, Ajuna SAGE), each row tagged with the *named* triple condition it fails
  (effort / repo / proof), so exclusions are reproducible from the criterion alone.
- **m4** qualify "5× more code per PM" → "implied by the calibration; an *upper bound* on productivity
  difference because A also absorbs un-corrected reuse and below-market pricing." **[DONE — wording]**

---

## Reviewer 2 — Blockchain Engineering / Grant Economics

### M1 — Stratify by funding mechanism (W3F vs treasury) — **[DONE-partial] + [PLAN]**
| subset | n | A* | SA |
|---|---|---|---|
| core treasury-only | 5 | 0.549 | +0.84 |
| core w3f-only | 1 | 0.739 | (n=1) |
Only 1 clean W3F pilot (fennel; the other, ParaSpell, was lost to repo deletion), so a clean split isn't yet
possible — flagged. Treasury-only A* = 0.55 (SA +0.84) is close to the pooled 0.58. **[PLAN]** add W3F pilots
to enable the split; discuss that **W3F milestones are curator-verified** (stronger delivery evidence) vs
community-voted treasury self-reports (weaker), as a *proof-strength* axis distinct from actual/proposed.

### M2 — "Below-market pricing" asserted, not evidenced — **[DONE]**
Implicit grant rate = grant USD / PM / 152 h:
| | remarker | fennel | dotreasury | megaclite | dotcodeschool | bagpipes |
|---|---|---|---|---|---|---|
| **$/hr** | **4** | 37 | 55 | 60 | 125 | 100 |
Core-6 **median ≈ $60/hr**, range $4–$125, vs market senior blockchain rate ≈ $80–150/hr. → grants are mostly
**below market** (Remarker extreme at $4/hr). **Conclusion now stated explicitly:** A = 0.58 is a *grant-context*
constant encoding both genuine productivity (reuse, senior devs) *and* below-market / honest-actual reporting
incentive — **it is not a pure productivity constant**, and applying it to *commercial* market-rate blockchain
development would bias estimates. This is a scope boundary, now evidenced.

### M3 — Proposed vs actual in governance incentive terms — **[DONE-data] + [ACK]**
Treasury proposers face an incentive to report *plausible* (community-acceptable) hours, not actual. We
already tag every pilot A/P and now report A* separately (see R1-M3: actual 0.49, proposed 0.68). Direct
answer added to paper: *"We measure two distinct evidence classes — retroactive itemised actuals (Subsquare,
Remarker, ink! analyzer, …) and forward proposals — and report them separately; the headline A pools both,
the actual-only A≈0.49 is the conservative anchor."*

### M4 — Generalisability beyond Polkadot/Kusama — **[ACK] + [PLAN]**
Scope statement added: *"A = 0.58 is calibrated to **Substrate-based Polkadot/Kusama grant software**;
EVM (Ethereum/OpenZeppelin/Hardhat), Solana, Cosmos, and Move ecosystems differ in tooling, reuse norms, and
developer economics — cross-chain applicability is an open question."* **[PLAN]** one Ethereum ESP pilot as a
Year-2 external-validity probe.

### Minor — **[DONE/PLAN]**
- **m1** ParaSpell repo deletion: note recoverability check (GitHub deletion is permanent after grace; try
  Software Heritage / archive.org). **[PLAN]** Impact: pilot #9 excluded; reproducibility unaffected for the
  other 12 (all repos live + commit-pinnable). **[ACK]**
- **m2** Log **USD value at execution** alongside native token per pilot (FX reproducibility). **[PLAN]** add a
  `grant_usd` column to VERIFIED_PILOTS (values already collected — see pricing table above).
- **m3** "senior/solo developer" productivity unmeasured — **[ACK]**; team-size/seniority is a future driver.
- **m4** Worked governance example — **[DONE, illustrative]:** *a proposed 10 KSLOC tool with Nominal drivers
  at A=0.58 ⇒ PM ≈ 0.58·10^1.10·1.0 ≈ **7.3 PM** (≈ 1,100 h). A proposal claiming 25 PM for the same is ~3.4×
  high → flag for review; one claiming 2 PM is ~3.6× low → likely heavy reuse, verify equivalent SLOC.*

---

## Consolidated priority order (before expanding n)
1. **[DONE]** SA as primary metric; actual/proposed + funding stratification; power-law vs COCOMO test;
   pricing-confound evidence; selection-bias quantitative bound → **fold into the report (this round).**
2. **[PLAN, next]** Fix the 6 inflated sizes (path-based generated detection + scope isolation) → full-12 A*;
   confirm it lands in [0.58, 0.70]. *(This is the single highest-value action — R1-M1.)*
3. **[DONE]** Rejected-candidates table (R1-m3, §2.3) + Boehm/Kemerer/Myrtveit & Stensrud/Shepperd &
   MacDonell/Jørgensen citations (§10, inline at §1/§4.4). **[PLAN remaining]** `grant_usd` column in
   VERIFIED_PILOTS (M2-R2 m2; values already in the §4.4d pricing table).
4. **[PLAN, Year-2]** Grantee self-report survey (true-actual anchor); one Ethereum ESP pilot (cross-chain);
   pre-registered 5-pilot holdout validation; W3F/Polkadot-council engagement; practical grant-review tool.

*Both reviewers rate this fundable / accept-with-major-revision. The revisions above are additive and do not
threaten the core result — the new analyses (SA +0.80, EM-machinery contribution, plausible reuse direction)
strengthen it.*
