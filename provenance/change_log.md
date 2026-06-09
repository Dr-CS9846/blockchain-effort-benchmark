# Change Log — append-only audit trail

Newest first. Each entry records what changed and why, for reproducibility and review.

## 2026-05-30 (PHASE 2 start: COCOMO II audit + verified tables + math framework + repo probe)
- User directive: keep ALL 22 COCOMO II variables + constants (no drops without strong reason); proceed MATHEMATICALLY (every constant/variable proven); build everything ON GitHub (reproducible).
- DEEP AUDIT of prior COCOMO work (scripts/04_build_cocomo_dataset.py): VERIFIED against the official COCOMO II Model Definition Manual v2.1 (2000) - A=2.94, B=0.91, all 5 scale-factor tables (Table 10) and all 17 effort-multiplier tables (Tables 17-34) are EXACT/correct. Flaws were in the prior IMPLEMENTATION, not the numbers: (a) ground-truth PM was PLANNED FTExduration [now measured], (b) size was ESTIMATED from level/PM heuristic [now measured cloc KSLOC], (c) the 17 standard EMs were never applied (em_product=1.0), (d) ratings used weak grant-metadata proxies not repo signals, (e) blockchain EM values were guesses. NEW issue found: blockchain EMs DOUBLE-COUNT with standard EMs (DC<->CPLX, AUD<->RELY, NODE<->CPLX/PVOL, GAS<->TIME). Docs: cocomoII_prior_work_audit.md.
- Pinned verified tables in scripts/validate/cocomo2_tables.py (single source of truth; self-checked: 5 SF + 17 EM, Nominal EM=1.00, A/B).
- MATHEMATICAL FRAMEWORK (cocomoII_mathematical_framework.md): log-linear model y=lnA+B*lnS+g_SF+Σln(EM)+ε; resolve double-counting/redundancy by IDENTIFIABILITY (corr/VIF/condition number), NECESSITY by ablation ΔSA, SUFFICIENCY by residual structure; calibrate A by closed-form log-OLS MLE (3). The blockchain-EM "ok/insufficient/overdoing" verdict comes OUT of this analysis, not by choice.
- SYNTHESIS SPEC (cocomoII_synthesis_spec.md): per-variable objective synthesis rules + Nominal defaults; earlier prune-note superseded.
- BUILT scripts/extract/cocomo_probe.py: objective per-repo signal extraction (CI/tests/docker/docs/audit/lint, on-chain runtime/pallets, contracts, dependency signals: consensus/cross-chain/zk-crypto/contract/frontend) -> data/calibration/repo_attributes.csv. Pure-function logic unit-tested (all signals correct on a synthetic substrate repo; path-normalisation bug fixed). Added .github/workflows/cocomo.yml (probe batch -> publish to census branch).
- Working manuscript PUBLICATION_blockchain_effort_benchmark.md kept LOCAL (gitignored) per user (polish later).
- Next: push -> dispatch cocomo-synthesis (probe) -> then build synthesizer (all 22 + BC EMs from attributes) + fit (redundancy/calibrate A/ablation/residuals) on GitHub.

## 2026-05-30 (strengthenings RAN: planned-PM revealed as a NOISY anchor; triangulation is the proof)
- Re-harvest (dual grant-repo matcher) + measure subset=all: planned-PM anchors 15->37; n_distinct 51->63.
- Triangulation HOLDS strong: Spearman low~mid 0.99, mid~high 0.87, low~high 0.85.
- Criterion (planned) on the fairer 37-anchor sample: coverage 59% (22/37), corr 0.15, measured/planned ratio Q1 0.13 / median 0.31 / Q3 0.70 / max 6.8 (misses BOTH directions). CONCLUSION: W3F planned PM is a NOISY forward total-FTE budget -> a LOOSE convergent check, NOT the primary validator; we must NOT force measured==planned. (Earlier 73%@n=15 was small-sample optimism.)
- Robust validity therefore rests on TRIANGULATION + REPRODUCIBILITY + peer-reviewed method precedent (Robles&GB), not the plan. Definitive remaining anchor = developer self-report (what Robles&GB used; plans are too loose). Updated pm_validation.md accordingly.
- Harvester fixes confirmed: ParaSpell case-variant merged; planned coverage tripled; societal still multi-repo-ambiguous (node vs front-end) - inherent, noted.
- Next: decision - (A) proceed to COCOMO II now (PMs validated by triangulation+method), with developer self-report as a parallel gold anchor; or (B) do self-report first. Continue subset=all batches to grow n in parallel.

## 2026-05-30 (W3F FTE scope resolved; 3 validation strengthenings; COCOMO scope answer)
- W3F FTE definition found (grants.web3.foundation): FTE = avg full-time employees over duration (0.5 FTE=20h/wk); planned PM = FTE x duration = TOTAL full-time effort, ALL activities. So our git PM (coding subset) being ~0.5x planned is EXPECTED (implementation ~ half of total effort), not an error. The 4 coverage misses (daos/nulink/societal/polkadart) are ALL plan>measured (plan over-states); polkadart plan=60 extreme; societal miss was our harvester picking the thin submission repo.
- COCOMO scope answer (recorded in pm_validation.md): no Phase-2 gap IF we calibrate COCOMO's coefficient A to OUR measured PM (local calibration, Boehm-sanctioned) -> model predicts the same quantity (git-coding PM). Objective drivers (Equiv Size, type, language, team) scale coding effort; we do NOT use the 17 subjective EMs. Model's predicted quantity stated explicitly = VCS-measured coding effort; total/cost = documented bridge later.
- IMPLEMENTED the 3 strengthenings (user-approved):
  (a) more planned-PM anchors: harvester now indexes applications across BOTH w3f/Grants-Program AND w3f/General-Grants-Program (older grants), recursive, and matches by repo-URL-in-application (most robust) + slug + fuzzy.
  (b) scope-difference interpretation + calibrate-to-target principle documented in pm_validation.md.
  (c) substantive primary-repo: pick_primary now deprioritises thin meta/submission repos (societal -> societal-node). Also: harvest groups by SLUG (merges case-variant project_ids e.g. ParaSpell-followup==Paraspell-followup).
- Efficiency: measure_repos resumability now also keyed by normalised repo_url (recognises unchanged repos under relabeled project_ids -> no re-clone) and refreshes passthrough columns (project_id/planned_*) on reuse -> a re-harvest can be re-measured in ONE cheap pass (only societal + genuinely-new repos re-cloned). Pure-function logic unit-tested (pick_primary societal->node, parse, syntax).
- Next: push -> census.yml auto re-harvests (new manifest: more planned, societal-node, slug-grouped) -> dispatch measure-census subset=all (reuse+refresh) -> read pm_validation.json (more coverage) + headline; then proceed to COCOMO II (M1 Equivalent Size).

## 2026-05-30 (PM VALIDATION suite: prove the ground truth before COCOMO calibration)
- User's pivotal question: how to PROVE the measured PMs (ground truth) are correct? Answer: effort is a LATENT construct (no timesheet oracle) -> cannot prove exact; instead establish VALIDITY+RELIABILITY (Kitchenham/Pfleeger/Fenton 1995 framework). KEY: PM-from-VCS is a PEER-REVIEWED method - Robles & Gonzalez-Barahona 2022 (Empirical Software Engineering), validated against 1,000+ developer questionnaires. Our approach follows it; unit = Boehm 152h.
- Built scripts/validate/validate_pm.py (pure-stdlib, reproducible) -> reports/pm_validation.json, computing on the deduped reliable+plausible set (n=51):
  - TRIANGULATION (Spearman among 3 PM estimators): low~mid 0.99, mid~high 0.80, low~high 0.79 -> methods agree strongly (construct validity).
  - CRITERION COVERAGE: 73% (11/15) of W3F planned PM fall inside [PM_low,PM_high]; corr(log planned, log PM_mid)=0.37; median measured/planned 0.50 (plans over-state).
  - EXTERNAL SANITY: median ~0.49 PM/KSLOC (~2000 SLOC/PM), within published ranges.
  - RELIABILITY: deterministic/bit-stable; PH/PM is a monotone factor (rank-invariant).
  Verified: script reproduces the hand-computed numbers exactly.
- Wired validate_pm into measure_census.yml (runs every census run; publishes pm_validation.json to census branch). Wrote docs/method/pm_validation.md (framework, results, citations, honest limits, open: developer self-report + git-hours cross-check).
- CITATIONS verified via search: Robles&GB 2022 (EMSE, arXiv:2203.09898); Kitchenham/Pfleeger/Fenton 1995 (IEEE TSE); Shepperd&MacDonell 2012 (IST 54:820-827); Boehm 2000; ISO/IEC/IEEE 15939.
- Next: push -> CI emits pm_validation.json; then proceed to COCOMO II calibration (M1 Equivalent Size) with the PM ground truth now validated/defensible. Optional strongest add-on: developer self-report subset + git-hours cross-check.

## 2026-05-30 (crossed n>=30 via subset=all batch; found non-independence; added per-repo dedup)
- measure-census subset=all (max 80) measured the next tranche -> reliable+plausible jumped to ~59 (CI) / 54 (local snapshot).
- CRITICAL data-quality finding: the expanded set is NOT independent. ~24 repo_urls appear 2-3x (paraspell/sdk x3, emeraldpay/polkaj x3, perun x3, sandox x3, Luno/LunoKit x2, ...) = multi-milestone / multi-grant deliveries to the SAME repo measured at different commits -> nested, non-independent (size,effort). Also delivery-filename CASE variants created duplicate project_ids (Iunokit==lunokit; ParaSpell-followup==Paraspell-followup). PANIC (158 KSLOC) checked = legitimate large real project (1568 commits/10 authors/22mo, gen 280 LOC), not contamination.
- FIX (pre-registered): calibrate_size_effort.py dedups to ONE observation per distinct repository, keeping the LATEST effort_until (most complete as-delivered), tie-break larger size. --no-dedup for sensitivity. Records dedup_by_repo in results.
- CLEAN deduped result (n~51 distinct repos): corr(log KSLOC, log PM_mid) ~= 0.36 (was 0.59 @ n=21 = small-sample optimism); PM_mid = 1.38*KSLOC^0.27. Bracket agrees (low .37 / mid .36 / high .27).
- ASSESSMENT (the n>=30 checkpoint): single-variable size->effort is confirmed INSUFFICIENT for blockchain grants (weak corr, LOOCV MMRE ~130%). PMs themselves are clean/bracketed/deduped/Boehm-anchored - this is a genuine finding, not a measurement fault. It is the evidence motivating the MULTIVARIABLE COCOMO II extension. (Open: also dedup at harvest by slug to stop case-variant project_ids.)
- Next: push dedup -> read official CI deduped headline; then proceed to COCOMO II multivariable calibration on the clean n~51 (or expand further first, user's call).

## 2026-05-30 (PM bracket MEASURED @ n=21; headline PM_mid; robust across low/mid/high)
- Re-measured verified subset under the Boehm PM bracket. Bracket holds per repo (pm_low<=pm_mid<=pm_high).
- corr(log KSLOC, log PM): PM_low 0.54, **PM_mid 0.59 (headline)**, PM_high 0.45 -> signal is STABLE across the whole bracket, not an artifact of the PM definition. Switching author-months->active-days/19 RAISED corr 0.45->0.59 and PRED25 0.19->0.33, SA 0.25->0.34 (active-days is a cleaner effort proxy than coarse author-months).
- Fitted (n=21): PM_mid = 0.90 * KSLOC^0.58. Benchmark magnitude: total ~71 PM central, bounded [26 (low), 280 (high)].
- planned-vs-measured: corr 0.41, median measured/planned = 0.48 -> by active-days, grants consumed ~HALF the planned person-months (FTE x duration). (Author-months had said 1.4x; the Boehm active-days view is the defensible one.)
- Note: foundation doc's 0.45 figure was author-months; PM_mid (0.59) now supersedes as headline.
- Phase-1 status: PMs are measured, bracketed, unit-anchored (Boehm 152h), reproducible. Ready to cross n>=30.

## 2026-05-30 (PM DEFINITION locked to Boehm 152h; three-estimate bracket implemented)
- Decided the person-month unit (the benchmark lynchpin). Researched + verified: COCOMO II nominal 1 PM = 152 person-hours = 19 working days x 8h (Boehm, COCOMO II Model Definition Manual; PH/PM is an explicit adjustable parameter). No ISO overrides it - ISO/IEC/IEEE 15939 only requires the unit be explicitly defined (which we do). Divisor = 19 (152/8), NOT 19.33/21.7 (calendar averages, internally inconsistent with 152h@8h). User accepted 19.
- DOUBLE-CHECKED the time-window tools (git-hours, git_time_extractor, GitClear): all use a session-gap + first-commit-buffer heuristic with DIFFERENT params (120min/120min vs 3h/30-per-commit vs 2h) and explicitly are not billing-accurate -> they do NOT resolve the hours ambiguity, they parameterize it. Conclusion: bound, don't pretend.
- IMPLEMENTED a 3-estimate PM bracket in measure_repos.py (replaces single active_person_months):
  - PM_high = active author-months (over-counts) [upper bound]
  - PM_mid  = active developer-days / 19 (Boehm) [HEADLINE]
  - PM_low  = time-window hours / 152, git-hours algorithm REIMPLEMENTED in-house (gap=120, first-commit=120 min) [lower bound]
  Columns pm_mid/pm_low/pm_high/active_dev_days added; reliability flag now on pm_high+authors+commits. Logic unit-tested offline (session math, bracket low<=mid<=high, lone-commit=buffer).
- calibrate_size_effort.py: --pm {pm_mid|pm_low|pm_high}, default pm_mid (headline); records pm_estimate in results. Backward-compatible with legacy active_person_months.
- Wrote docs/method/person_month_definition.md (unit, sources, tool verdict, bracket, all parameters explicit, honest limits).
- Next: re-measure verified subset (force) under the new PM bracket -> read PM_mid headline + the [low,high] band; then cross n>=30.

## 2026-05-30 (FOUNDATION: size->effort decoupling framed + COCOMO II direction; pause before scaling)
- Per user: build the foundation on the verified subset BEFORE scaling; reach n>=30, assess (works/rework), calibrate COCOMO II, THEN scale.
- Analysis on clean n=21: corr(log KSLOC, log effort)=0.45; productivity PM/KSLOC spans 0.39 (polkadart SDK) -> 9.2 (crossbow tooling) = ~23x spread. Decoupling is STRUCTURED by project type (size-dense SDK/scaffold vs effort-dense research/tooling/novel-language).
- HONESTY caveat recorded: effort proxy (author-months) is structurally coupled to authors x duration, so those higher correlations (0.71/0.76) are partly circular and NOT claimed; the clean finding is the SIZE one (0.45), measured independently of the effort proxy.
- Wrote docs/method/size_effort_decoupling_and_cocomoII.md: finding, caveat, grounded typology, COCOMO II mapping (Equivalent Size via AAF for template/adapted code [generated already removed]; objective git/grant-derived effort drivers: type/domain, language, novelty - each independent of the effort proxy), and the n>=30 test plan (M0 baseline / M1 equivalent-size / M2 +type; LOOCV+nested-CV; pre-registered decision rule works-vs-rework).
- Open (honest): equivalent-size adaptation factor for template code; objective project-type derivation rule (to be specified+unit-tested before fitting); n still 21.
- Next: push foundation doc; then one controlled subset=all batch to cross n>=30 (reliable+plausible), re-read M0; assess before building the multivariable drivers.

## 2026-05-30 (VERIFIED: evidence-based detector correct across census audit log; headline corr 0.45 @ n=21)
- Ran measure-census force=true with the evidence-based detector. AUDIT LOG (printed per excluded file) reviewed: EVERY exclusion is a genuinely generated file, each matched by its own self-declared marker - zero false positives:
  - substrate weights.rs benchmark files marker='Autogenerated' (daos x6: 166/109/78/43/32/21 LOC; cyborg, decentralml, etc.)
  - subxt bindings melodot/api.rs marker='statically generated code' (32,690 LOC)
  - smoldot libp2p single_stream.rs/multi_stream.rs marker='automatically generated' (690/602)
  - mobile scaffolds agridot MainActivity.kt / noop-file.swift marker='@generated'
  No hand-written file was excluded. Each logged with path+marker; ksloc_code_raw vs ksloc_code both stored.
- EFFECT: melodot 46.63->14.06 KSLOC; small trims elsewhere; many repos 0 excluded (delmonicos, eightfish, crossbow, tellor, dotnix, fractapp...). 
- HEADLINE (reliable+plausible, n=21): corr(log KSLOC, log effort) 0.32->0.38 (langs)->0.45 (generated). LOOCV MMRE 80%/PRED25 19%/SA 0.25. Size->effort still only MODERATE on clean data = genuine decoupling remains (template scaffolding + research-heavy low-LOC work) -> motivates the multivariable COCOMO II extension. Size pipeline is now trustworthy.
- Next: expand census subset=all in batches toward full n with the trustworthy size pipeline; keep effort goal central.

## 2026-05-30 (size-artifact fix 2: EVIDENCE-BASED generated-file detection; language fix raised n=21 corr 0.38)
- Language fix re-measured: headline n=21 (yatima recovered via Lean; dotnix corrected to 0.85 KSLOC), corr 0.32->0.38. Still weak.
- DOUBLE-CHECKED melodot (46.6 KSLOC/8PM suspect) via GitHub tree at the delivered commit: a single root file `api.rs` = 1,248,025 bytes; VERIFIED generated by reading its content (subxt codegen: `pub mod api` of subxt storage-address builders + raw byte hashes; line 323 says "...statically generated code"; sits beside melodot_metadata.scale). Real generated-code inflation.
- METHOD (user-reviewed; rejected size-as-criterion as too risky): exclusion is now EVIDENCE-ONLY. count_sloc scans each source file's content for an explicit self-declared generation marker (linguist-style: @generated, DO NOT EDIT, automatically generated, code generated by, statically generated code, ...). Size is used NOWHERE in the decision. A huge hand file with no marker counts in full; a tiny generated file with a marker is excluded. Automatic, deterministic - no manual per-file review.
- TRANSPARENCY: reports ksloc_code_raw (nothing excluded) AND ksloc_code (markered-generated removed) + generated_loc_excluded + generated_files_n; every excluded file is logged with its matched marker. Fully auditable/reversible.
- Detector unit-tested: matches melodot api.rs ("statically generated code"), Go "Code generated by...DO NOT EDIT", subxt/prettier "@generated"; does NOT match prose like "generates a keypair" or "randomly generated data" (zero false positives on traps).
- Next: re-measure verified subset (force) -> compare ksloc_code_raw vs ksloc_code, re-read headline; then double-check polkadart the same way.

## 2026-05-30 (clean census headline n=20: KSLOC weakly predicts effort; size-artifact fix begun)
- CLEAN HEADLINE (reliable AND duration-plausible, n=20): corr(log KSLOC, log effort)=0.32 (WEAK), LOOCV MMRE 75%/PRED25 20%/SA 0.22; planned-vs-measured r=0.38, actual ~1.39x planned. The pilot's 0.94 was small-n optimism; at census scale size alone weakly predicts effort (melodot 47KSLOC/8PM vs crossbow 3.9/36PM) - a defensible finding, but partly measurement artifact.
- DIRECTION (user): effort estimation is THE goal (map COCOMO II to blockchain, prove on git); cost is secondary/later. Fix size artifacts BEFORE expanding. Flag, don't delete; discard only after per-repo double-check (avoid shrinking n).
- ARTIFACT FIX 1 (language coverage): SOURCE_LANGS += Nix, Lean, Circom. These are the DELIVERABLE language for some grants and were undercounted to ~0: dotnix (Nix, was 0.076 KSLOC) and yatima (Lean, was 0.000 -> auto-dropped by size>0). The fix corrects dotnix AND RECOVERS yatima (8.7 KSLOC, 41 PM, 7 auth) -> n grows, not shrinks.
- Added measure_census.yml `force` input to re-measure already-OK rows after a measurement-logic change.
- Next: dispatch measure-census subset=planned force=true -> re-read clean headline; then per-repo double-check the high-KSLOC/low-effort suspects (melodot, polkadart) for vendored/generated-code inflation before any discard.

## 2026-05-30 (CI fix: forced checkout on census re-runs)
- measure-census run #2 failed (exit 1) at the publish step: on re-runs measurements_census.csv already exists on the census branch, gets restored+modified, and `git checkout -B census origin/census` refused ("local changes would be overwritten"). Run #1 escaped this only because the file did not yet exist. FIX: `git checkout -f -B census origin/census` (outputs are already copied to /tmp before the switch, so discarding the worktree is safe). Headline (reliable+plausible) not yet read - awaits this fix.

## 2026-05-30 (census batch 1 measured: fork contamination found; plausibility filter added)
- measure-census batch 1 (verified-application subset) measured ~45 OK (2 ERROR: deip, tpscore = private/removed repos). Reliable subset n=23.
- KEY FINDING: grounded first-commit->delivery duration EXPOSED FORK CONTAMINATION - repos that forked a large upstream chain inherited its whole history: cryptex=ideal-lab5/smoldot (99 KSLOC,15 auth,41.9mo,80PM), konomi=konomi-network/cumulus (27 auth,29mo,84PM), liberland=forked Substrate (105 auth,52.6mo,378PM). All caught by duration_plausible=0 (>24mo). They are effort_reliable=1 so they leaked into the reliable-only headline and wrecked it (corr 0.59, LOOCV MMRE 164%).
- FIX: calibrate_size_effort gains --plausible-only (filters duration_plausible). CI now publishes 3 layers: census_full (all), census_reliable (effort signal only), census (reliable AND plausible = HEADLINE). Removing 3 forks -> headline n=20 of clean grant-window repos.
- Residual honest scatter remains (e.g. dotnix=76 lines Nix/mostly non-source -> near-zero KSLOC but 7PM = leverage point; melodot 46 KSLOC/8PM). Noted for later (min-KSLOC floor? language coverage) - will inspect the clean fit before any further tuning.
- Next: push calibrate+workflow change; re-run measure-census (recalibrate only, rows already OK) to read the clean reliable+plausible headline; then expand subset=all in batches toward n>=30 clean.

## 2026-05-30 (GROUNDED duration: removed 3-month fallback; measure first-commit->delivery)
- User (correctly) rejected the 3-month default window as an ungrounded assumption that would not survive grant/publication review. Removed window_since + DEFAULT_WINDOW_MONTHS entirely.
- NEW Phase-1 methodology, fully measured from git: effort window END = delivered commit's own date; START = first commit reachable from the delivered commit (project inception for grant-dedicated repos); explicit since_date overrides. New columns actual_duration_months (MEASURED calendar span) + duration_plausible (provisional review flag, <=24 mo; long spans may carry pre-grant history - flagged, not dropped). This also fixes the old over-count honestly: the inflated whole-lifetime numbers came from measuring to HEAD (post-grant commits), which stopping at the delivered commit excludes.
- Plan (user): PACE step-wise. Batch 1 = the ~47 verified-application rows (lets us validate the method AND run actual-vs-planned duration check), then batches of 30/40/50. PHASE 2 (later) = add an idle-trimmed "active span" as a SECOND effort method -> a calendar-span vs active-effort study for blockchain dev, expected to yield more nuanced COCOMO values.
- Tooling: measure_repos gains --only-with-planned (verified subset) and the measured-duration columns; partial clone + --max batching retained. measure_census.yml gains a subset input (planned|all). Pure-function logic unit-tested offline (months_between, plausibility).
- Next: push -> dispatch measure-census subset=planned -> review the ~47 (durations sane? actual vs planned?) before expanding.

## 2026-05-30 (census harvested: ~432 eligible; scalable batched measurement wired)
- Census run scanned ~444 W3F delivered projects -> ~432 INCLUDED, ~15 EXCLUDED (8 un-separable shared-monorepo, 7 no-project-repo) - eligibility rule behaving as designed. Dates span 2020-2026 (peak 2022-23). 35 commit-pinned, ~397 measured-at-cutoff. Published to dedicated 'census' branch (projects_manifest.census.csv + census_audit.csv).
- Issue: planned fields matched for only ~47/432 (delivery filename often != application filename). FIX: window_since now falls back to DEFAULT_WINDOW_MONTHS=3 (modal W3F duration) when planned_duration is blank -> effort window still bounded (no whole-repo over-count). planned_pm cross-check simply has fewer points; headline size->effort fit unaffected.
- Scalability: ensure_clone now uses treeless partial clone (--filter=blob:none) -> full commit history for effort/dates, blobs on demand at checkout; fits hundreds of repos in CI. measure_repos --max N = batched + resumable (skips OK rows, carries rest as PENDING). Logic unit-tested offline (window fallback, max guard, reliability).
- Added .github/workflows/measure_census.yml (dispatch): uses main scripts, restores manifest+prior progress from census branch, measures a batch, calibrates reliable(headline)+full(sensitivity), publishes back to census. Dispatch repeatedly to cover all ~432.
- Next: dispatch measure-census in batches; watch n grow and the reliable-subset fit stabilize toward n>=30.

## 2026-05-30 (n>=30 expansion via pre-registered CENSUS - harvester built)
- HEADLINE confirmed (reliable subset, n=5): corr(log KSLOC, log effort)=0.94; in-sample MMRE 15.4% / PRED25 80% / PRED30 100% / SA 0.71 (passes Conte in-sample); LOOCV MMRE 31% / PRED25 60% / SA 0.40. Full set (n=7) sensitivity: corr 0.74. Actual effort ~1.7x planned (median); planned-vs-measured r=0.40.
- DECISION (user): expand via a CENSUS (all eligible), not a sample - strongest external validity, pre-registered inclusion rule, no analyst selection.
- Built scripts/extract/harvest_deliveries.py: scans EVERY w3f delivery file, groups by project (robust milestone-marker stripping), picks a separable primary repo (own-org slug rule; excludes shared monorepos paritytech/AcalaNetwork/...), dates via earliest-add commit (full-history clone), and sources planned duration/FTE/cost from applications/<slug>.md (regex on the Overview block; verified against real Fennel app = 3mo/3FTE/$50k -> pm 9). Emits projects_manifest.census.csv (INCLUDED) + reports/census_audit.csv (every project + verdict). Pure functions unit-tested offline (project_key variants, repo extraction, primary selection, planned regex). 
- Added .github/workflows/census.yml (separate, heavy, dispatch/push-triggered) -> publishes candidates to rolling for human review before promotion to main.
- Next: push -> census runs -> review census_audit.csv (count + spot-check) -> promote eligible to main manifest -> measure + recalibrate at n>=30.

## 2026-05-30 (effort-reliability flag + sensitivity reporting; n=7 result read)
- Run #9 (commit-date anchor) rescued ParaSpell (4 PM, 3 authors) and Roloi (1 PM); AdMeta + AgriDot stay 0 = squash/single-import repos (no git history). Usable n=7.
- **MEASURED size->effort, n=7:** corr(log KSLOC, log effort) ~= 0.74 (strong, on clean grant-windowed effort; was an over-counted 0.89 before windowing). In-sample MMRE 66%, PRED25 43%, SA 0.49. LOOCV MMRE 115%, PRED25 0%, SA 0.27. Accuracy proxy-noise-limited at small n.
- IMPORTANT finding: corr(planned PM, measured effort) = 0.20 -> planned grant effort barely predicts actual git effort.
- Two structural effort-proxy limitations identified (citable): (a) squash-imports (AdMeta, AgriDot) give no git-effort signal; (b) single-committer funnelling (Societal: 71 commits / 1 author -> 4 PM) under-counts person-months.
- DECISION (user): quality-flag + sensitivity. Added effort_reliable column (>=2 authors AND >=10 commits) in measure_repos.py; calibrate_size_effort.py gains --reliable-only and now reports size_effort_corr_log. CI writes size_effort_results_measured_full.json (all OK rows = sensitivity) and size_effort_results_measured.json (reliable subset = HEADLINE, runs last = canonical). Reliable subset at n=7 = {Fennel, ParaSpell, bright, fair, lastic} (Roloi+Societal drop).
- Next push publishes the headline (reliable) vs sensitivity (full) fits; then expand toward n>=30.

## 2026-05-30 (effort window anchored on delivered-commit date, not paperwork date)
- After the shallow-clone fix, real cutoffs gave 5/9 non-zero effort (Fennel 4, Societal 4, bright 12, fair 15, lastic 10 PM). But 4 (AdMeta, AgriDot, ParaSpell, Roloi) were still 0.
- ROOT CAUSE: the effort window was anchored on the delivery-FILE (milestone-paperwork) date. Code is typically committed weeks-to-months BEFORE the milestone is formally submitted, so the planned-duration window sat *after* the work and caught no commits (the delivered commit predated the window start).
- FIX: measure_repos.py now anchors the window on the DELIVERED COMMIT's own committer date (commit_date(sha)); since = commit_date - planned_duration; falls back to delivery cutoff_date if commit date unknown. The 5 working repos are unaffected (their cutoff-resolved commit date ~= cutoff). Commit RESOLUTION still uses the paperwork date to reject post-cutoff pins (an as-delivered commit cannot post-date its own delivery) - that stays correct.
- Next push should rescue the commit-pinned zeros (unless a repo is a single squashed import = genuinely no git-effort signal, which we then document/drop).

## 2026-05-30 (CRITICAL fix: shallow-clone defeated delivery dates -> all effort=0)
- DIAGNOSIS (run #7): the window-start bound zeroed ALL effort. Root cause found via reports/resolved_repos.csv: delivered_date = 2026-04-15 for EVERY project (impossible). The resolver cloned the W3F delivery repo with `--depth 1`; a shallow clone collapses every file's "last commit" onto the single tip commit, so `git log -1 -- <file>` returned one uniform recent date for all files. Wrong cutoff (~2026) -> grant window [cutoff-duration, cutoff] landed in 2026 where these 2022-2023 repos have no commits -> active_person_months=0 everywhere. (Run #6 only "worked" because it had no since-bound: until=2026 still captured all history.)
- FIX: resolve_repos_online.py clone() takes shallow flag; delivery repo now cloned FULL (real per-file dates), grants repo stays shallow (links only). delivery_file_date now takes the EARLIEST (add) commit = true submission moment, not a later edit.
- Next push re-resolves real ~2022/2023 cutoffs -> grant-windowed effort should be non-zero and correctly bounded; then re-read measured fit.

## 2026-05-30 (refinements: window-start + AgriDot)
- measure_repos.py: effort window now has a START bound `window_since = cutoff - planned_duration` (curbs long-lived-repo over-count: bright/fair counted years of pre-grant history). New columns effort_since/effort_until for provenance.
- resolve_commit: rejects a pinned commit whose commit-date POST-DATES the cutoff (an as-delivered commit cannot be after delivery) -> falls back to cutoff. This generally fixes AgriDot (its pin post-dated delivery -> window gave 0).
- Manifest: AgriDot commit unpinned (measure at cutoff). Logic unit-tested offline.
- Next push re-measures all 9 with grant-window effort; then re-read measured fit.

## 2026-05-30 (FIRST measured size->effort signal — run #6)
- Size filter now works (ksloc_code != ksloc_all). Fennel zero fixed via cutoff fallback (now 31 PM). commit_source column populated.
- **KEY RESULT (measured KSLOC vs measured git-effort, n=8; AgriDot dropped =0):** PM = 2.47 * KSLOC^0.80; **corr(log KSLOC, log PM) = +0.89** (strong). This refutes the old artifactual r(SLOC,PM)=-0.23 (that was mis-measurement). Constructive core has real signal.
- Accuracy NOT yet there: LOOCV MMRE 106%, PRED25 12%, SA 46% (better than random). Limited by n=8 + git effort-proxy noise (author-months ~ team shape) + residual over-count (no window START bound).
- Fixed CI bug: `--effort planned` run was clobbering the measured results.json. Now writes size_effort_results_{measured,planned}.json; measured runs last = canonical.
- Still open: AgriDot active_PM=0 (pinned-commit/cutoff interaction) -> diagnose or drop; add since_date window-start (cutoff - duration) to curb long-lived-repo over-count (bright 63, fair 40).

## 2026-05-30 (effort-window + as-delivered fix)
- measure_repos.py: (a) commit reachability check + enforced checkout (a pinned sha NOT in the repo now falls back to cutoff/HEAD with a flag instead of silently measuring HEAD); (b) effort bounded by cutoff_date (`git log --until`); (c) new `commit_source` column (commit|cutoff|head) so every row shows whether it was measured as-delivered.
- resolve_repos_online.py: (a) `commit_for_repo` - only pins a commit that belongs to the chosen repo (fixes AgriDot/Fennel zeros, which were caused by pinning a sibling-repo commit); (b) `delivery_file_date` -> emits delivered_date (git date of the milestone-delivery file) -> --fill writes cutoff_date; (c) skips EXCLUDED rows so they are never revived. Logic unit-tested offline.
- measure.yml: resolver --fill re-enabled (safe: keeps confirmed repos, only fills blank cutoff/commit, skips EXCLUDED) -> adopt -> measure. Next run measures source-only KSLOC + as-delivered effort in the grant window.

## 2026-05-30 (first measurement run #5 — data-quality review)
- CI measured 10 repos OK. Review found 3 data-quality problems (NOT yet calibration-ready):
  1. SIZE BUG: `count_sloc_cloc` returned ksloc_all for BOTH ksloc_code and ksloc_all (line 71) -> size counted JSON/YAML/MD/PO etc. FIXED: added SOURCE_LANGS filter; ksloc_code now source-only. Verified impact (AgriDot 36->5; ParaSpell 10->1.4; Web3Go 742->301; AdMeta 3.3->2.6).
  2. EFFORT ZEROS: AgriDot, Fennel returned active_person_months=0 (commit unreachable / squashed-import) — to diagnose.
  3. HEAD OVER-COUNT: un-pinned repos measured whole-lifetime effort (bright_treasury 63 PM, fair 40, lastic 24) — need grant-window bounding via cutoff_date.
- Web3Go EXCLUDED (even code-only = 301 KSLOC whole-platform consolidation; not separable). Measurable set now 9.
- No calibration reported yet — data must be re-measured clean first.

## 2026-05-30 (resolution reviewed + manifest finalized for clean cases)
- CI clone-based resolver ran (run #4): produced candidates for all 13 -> reports/resolved_repos.csv (on rolling).
- Human review (judgment pass) applied. CONFIRMED + filled into main manifest: AdMeta, AgriDot, Fennel_Protocol, ParaSpell_follow_up (with **delivered commits**); bright_treasury, fair_squares, Societal, Roloi (repo only; Roloi disambiguated to RoloiMoney W3F-grant repo, not NeoPower/tempora).
- Matcher hardened to prefix-based: fixed substring false-matches ('lastic' in 'eLASTIClabs'; 'tdot' in 'daTDOT'). Re-tested.
- FLAGGED for decision (left blank in manifest, not measured): Coinversation (no code delivery; only white-paper), Afloat (hashed-substrate monorepo = whole chain), Web3Go (multi-repo), lastic (LasticXYZ; main app repo unconfirmed), tdot (lives inside Acala monorepo; not separable).
- Open methodological question raised: multi-repo / monorepo attribution rule (primary repo vs sum of delivered repos) + as-delivered cutoff_date for the no-commit repos.
- DECISION (user): attribution rule = PRIMARY repo per project + EXCLUDE un-separable monorepo cases. Finalized:
  - KEEP (10): AdMeta, AgriDot, Fennel_Protocol, ParaSpell (commit-pinned); bright_treasury, fair_squares, Societal, Roloi(RoloiMoney), Web3Go(web3go-xyz-v2 primary), lastic(LasticXYZ/LasticUI - confirmed primary app).
  - EXCLUDE (3, documented): Coinversation (no code), tdot (inside Acala monorepo), Afloat (inside hashed-substrate whole-chain).
  - CI now measures the human-reviewed manifest directly (resolver demoted to audit-only, no --fill); 4 measured at delivered commits, 6 at HEAD pending cutoff_date.

## 2026-05-30 (robust repo/commit resolution)
- Rebuilt `scripts/extract/resolve_repos_online.py` to be robust: it CLONES the W3F delivery + grants repos (reliable in CI; no rate limits / no fragile filename guessing), fuzzy-matches each project to its milestone-delivery file(s), and extracts the delivered repo URL + commit (/tree|/commit/<sha>); application repo links as fallback. Writes `reports/resolved_repos.csv` for human review; `--fill` writes `projects_manifest.online.csv`. Matcher + parsers unit-tested offline.
- Reason for rebuild: live delivery filenames are irregular (e.g. AgriDot's is NOT `AgriDot-milestone_1.md` — that path 404s), so URL-guessing missed most projects. Cloning + directory fuzzy-match fixes this and scales to 150.
- CI (`measure.yml`): resolve now runs with `--fill`; the rolling snapshot adopts the resolved repos+commits and measures at the PINNED commit. `main`'s manifest changes only after human review of `reports/resolved_repos.csv`.
- `.gitignore`: added `resolve_cache/`, `projects_manifest.online.csv`.

## 2026-05-30 (accuracy rigor — Stage 1)
- Added `scripts/validate/metrics.py`: canonical metric suite — MMRE, MdMRE, PRED(25/30), MAE, and **Standardized Accuracy (SA) vs a random baseline (MARP0)**, plus Cliff's delta. Unit-tested (SA=1 on perfect, ~0.39 on mean-guess, negative when worse than random).
- Wired the suite into `calibrate_size_effort.py` (now reports MAE + SA alongside MMRE/PRED). Verified on synthetic measured data.
- Added `docs/method/accuracy_validity_plan.md`: agreed "both, staged" approach — methodological rigor first, honest accuracy second; grounded realistic target bands; anti-leakage red lines. Rationale: MMRE alone is biased (Shepperd & MacDonell); near-perfect accuracy on real effort data signals leakage, not excellence.
- Wired SA/MAE into `calibrate_bc_cocomo.py` too (both models now report on equal modern footing). Verified on real data: LOOCV MMRE 41.1%, PRED25 30.8%, MAE 2.70, **SA 0.463** (baseline is ~46% better than random — informative even though it fails the strict Conte bars).
- Added `scripts/validate/nested_cv.py`: reusable leakage-proof nested-LOOCV tuning harness, demonstrated on an Analogy-Based Estimation (k-NN) baseline whose k is tuned by inner CV. Passed a behavioural leakage test (corrupting a held-out point does not change its own prediction). Note: the OLS calibrators have no tuned hyperparameters, so plain LOOCV is already unbiased for them; nested CV is the guardrail that activates for any Stage-2 tuned model.

## 2026-05-30 (source→claim chain)
- Added `provenance/claims_ledger.md`: every published number traced to script → data → raw source, with reproduced?/frozen? status. Names the open lineage gaps explicitly.
- Added `scripts/extract/freeze_raw.py`: snapshots verbatim raw W3F application + delivery sources into `data/raw/` with `RAW_MANIFEST.csv` (sha256, captured_at). Logic unit-tested offline. Wired into Makefile (`make freeze`, in `all`) and CI (freezes + commits `data/raw/` to rolling).
- `data/raw/` declared as committed evidence (not git-ignored).
- Assessment recorded: baseline chain (C1–C4) is reproduced (make verify MATCH) but not yet frozen at raw source; measured size→effort (C6) awaits CI. Audit-grade reached when data/raw frozen + C6 produced + promoted to a tag.

## 2026-05-30 (Phase 2 + datasheet)
- Added one-command pipeline: `Makefile` (targets: setup/baseline/resolve/measure/calibrate/figures/quickcheck/all/verify/clean) + portable `run_all.sh`. `.RECIPEPREFIX` used for portability.
- Added `scripts/validate/make_figures.py` (deterministic; matplotlib guarded). Tested: `make quickcheck` reproduces the baseline + writes reports/figures/baseline_actual_vs_pred.png; `make verify` → MATCH (MMRE 0.4109, PRED25 0.3077, bit-stable).
- Added `docs/DATASHEET.md` on the Gebru et al. *Datasheets for Datasets* (CACM 2021) 7-section standard.
- Switched all forced pushes to `--force-with-lease` (with prior fetch); plain `--force` banned. Codified in release_policy.md.
- Fixed 00_check_environment.py to find the manifest under data/calibration/; `setup` made non-gating.

## 2026-05-30 (later) — governance + Action 2 start
- Added `provenance/release_policy.md`: the living benchmark is gated — CI publishes only to a non-authoritative `rolling` branch; published claims live in reviewed, **tagged** releases (cite tags + Zenodo DOI versions, never `main`).
- Updated `.github/workflows/measure.yml` so CI commits to `rolling`, never `main`.
- Extended `scripts/extract/resolve_repos_online.py` to parse W3F **milestone-delivery records** (authoritative source for the delivered repo AND the pinned commit); delivery sources outrank application sections. Unit-tested.
- Manifest: confirmed `Societal -> sctllabs/societal-node` (from its delivery record); cleared the prior wrong `bright_treasury` auto-suggestion (tutorial repo). Remaining repos+commits to be resolved authoritatively by the CI resolver run.

## 2026-05-30
- Restructured the repository into the **trimmed layered architecture** (calibration / provenance / docs / reports + external_holdout), declaring its role as a **reproducibility backbone (Option B)**.
- Applied the **decision rule** to every artifact → `provenance/source_map.md`.
- Excluded blockchain *performance* benchmark suites (Blockbench/TrustedBench) from the data layers; they remain related-work context only.
- Mirrored the real verified dataset and the honest baseline calibration into the repo so results are reproducible from within it.
- Updated `.github/workflows/measure.yml` to the layered paths; outputs routed to `data/calibration/` and `reports/`.
- Established `canonical_factsheet.md` as the single source of truth.

## Earlier (recorded in thesis docs)
- Reproducible honest baseline established: LOOCV MMRE 41.1%, PRED(25) 30.8% (FAILS Conte) — `calibrate_bc_cocomo.py`.
- Structural finding: PM ≡ FTE × Duration (effort defined, not measured).
- Provenance trace: headline A=2.1143 / QI-GAN / 22.9% results not reproducible from the folder (no code, no data, harness unrun).
- Measurement toolkit built + unit-tested; GitHub repo + Actions engine created.

## Phase 2 — COCOMO II synthesis + calibration (GitHub-native)
- Probe run #1 (cocomo-synthesis workflow) extracted objective signals for the full measured
  set → data/calibration/repo_attributes.csv (census branch). Signals: CI/tests/docker/docs/
  audit/lint, onchain_runtime, has_contracts, dep_{consensus,crosschain,zkcrypto,contract,frontend}.
- Added scripts/validate/cocomo_fit.py: synthesizes ALL 5 SF + 17 EM (Nominal default) + 7
  COCOBLOCK blockchain EMs from those signals using verified COCOMO II.2000 magnitudes
  (cocomo2_tables.py); calibrates ln A by closed-form OLS = lognormal MLE (B=0.91 fixed);
  proves variable roles — REDUNDANCY (pairwise corr + VIF), NECESSITY (per-variable ablation
  ΔSA under LOOCV), SUFFICIENCY (residual structure). Outputs reports/cocomo_analysis_{pm}.json
  and data/calibration/cocomo_synth_{pm}.csv for pm_mid (headline), pm_low, pm_high.
- Wired both into .github/workflows/cocomo.yml (probe → fit → publish to census branch).
- Local end-to-end validation on synthetic substrate confirmed the redundancy machinery:
  deliberately-overlapping blockchain EMs (BC_EM_AUD↔RELY, BC_EM_GAS↔TIME, BC_DC/BC_EM_NODE↔PVOL)
  surface as |corr|→1 with VIF→∞, i.e. the double-counting is PROVEN by the data, not asserted.

## Phase 2b — fixed-weight failure diagnosed; pivot to LOCAL CALIBRATION (PM=PM goal)
- cocomo_fit.py (Boehm FIXED multiplier magnitudes + calibrate A only) gives LOOCV SA<0 on all
  three PM brackets (pm_low/mid/high: -1.64/-1.82/-4.19); blockchain EMs proven non-identifiable
  (BC_EM_AUD≡RELY, BC_EM_GAS≡TIME, BC_DC≡PVOL at corr=1.0/VIF→∞) and non-necessary (ablation ΔSA≤0).
- DIAGNOSIS: SA<0 is a fixed-weight artefact, NOT size→effort decoupling. With coefficients FIT
  locally, ln(ksloc_code) alone gives LOOCV SA≈+0.45 (Pearson ln-size vs ln-PM=+0.60). total_commits
  is the strongest correlate (+0.96; fitted SA≈+0.70) but is not pre-project knowable.
- Added scripts/validate/cocomo_localcal.py: COCOMO II local-calibration (Boehm 2000 ch.4). Fits
  ln PM = b0 + b1 ln(KSLOC) + Σ b_k driver_k by OLS in log space; greedy forward-selection over
  PROSPECTIVELY-knowable drivers (size, on-chain/contracts/audit/consensus/cross-chain/zk/frontend
  dummies, primary-language archetype; team-size reported separately), each model scored by LOOCV
  (SA/PRED25/PRED30/MMRE). Reports the smallest variable set maximising out-of-sample accuracy +
  its fitted coefficients = the applied effort model. Guards against fake PM=PM via LOOCV + var cap.
- Wired into cocomo.yml; publishes reports/cocomo_localcal_{pm}.json to census branch.

## Phase 2c — structural drivers exhausted; introduce FUNCTIONAL SIZE
- Local-calibration result (n=63, all brackets): best PROSPECTIVE model is size-dominated at
  LOOCV SA≈0.50, PRED(30)≈30% (ln_ksloc + language archetype; +team-size lifts pm_high to
  SA0.53/PRED30 48%). Every blockchain STRUCTURAL driver (onchain/consensus/crosschain/zk/
  contracts) sits at the mean baseline (univariate SA≈0.20-0.24) and is rejected by forward
  selection; the all-driver model OVERFITS (SA falls to 0.31). => structural binary flags
  cannot reach PM=PM; proven.
- Opening: total_commits (a VOLUME measure) predicts PM at fitted SA≈0.70 — the effort signal is
  not noise-bound. Need a PROSPECTIVE volume measure => FUNCTIONAL SIZE (function-point analogue).
- Extended cocomo_probe.py to count blockchain feature units from .rs/.sol contents: n_pallets,
  n_extrinsics (#[pallet::call_index]), n_storage, n_events, n_ink_msgs, n_sol_funcs,
  n_contracts_def, n_rpc. Validated counts on synthetic substrate/ink/Solidity fixtures.
- Extended cocomo_localcal.py: adds ln(1+count) per family + composite ln_feature_units to the
  candidate set. Next: dispatch probe with force=true to backfill FS columns, then re-fit and
  compare functional-size model vs the LOC-based 0.50 ceiling.

## Phase 2d — archetype stratification (does functional size predict WITHIN a type?)
- Full-data confirmation (force re-probe, max=300): on the POOLED corpus functional-size counts
  stay at baseline (univariate LOOCV SA 0.20-0.23) vs ln_ksloc 0.444; forward selection rejects
  them; all-driver model overfits (SA -0.60). Cause: corpus mixes incompatible archetypes, so any
  one feature family is zero for most repos.
- Added archetype_of() + stratified() to cocomo_localcal.py: classify each repo as onchain_pallet
  / smart_contract / offchain_app / library_tool, then run per-archetype local calibration
  (forward selection over ln_ksloc + matching feature size, LOOCV, cap=3). Tests whether a FAMILY
  of archetype-specific functional-size models beats the universal LOC ceiling (~SA 0.50).
- Validated stratified logic on synthetic substrate/contract/app/tool fixtures (functional size
  correctly selected within onchain_pallet & smart_contract groups). by_archetype now emitted in
  reports/cocomo_localcal_{pm}.json.

## Phase 2e — archetype stratification result (grounded) + independent re-verification
- INDEPENDENT re-verification (own script, authoritative measurements file, not CI JSON):
  dedup n=63 ✓; ln_ksloc LOOCV SA=0.444 ✓; ln_commits SA=0.713 ✓; Pearson(lnPM,lnksloc)=+0.604,
  (lnPM,lncommits)=+0.961 — all match published numbers. Core spine grounded.
- Stratified local calibration (pm_mid) improves over pooled SA 0.50:
  smart_contract n=11 SA 0.73 (PRED30 55%); onchain_pallet n=19 SA 0.62 (47%);
  offchain_app n=19 SA 0.59 (47%); library_tool n=14 SA 0.48 (43%). counts sum 63 ✓.
- HONEST caveats: (1) functional-size counts STILL not selected even within archetypes —
  the "blockchain functional size predicts effort" hypothesis is NOT supported; gain is from
  stratification + size + incidental flags. (2) per-group n=11-19 is small; selected binary
  flags (has_docker/dep_frontend/has_docs) carry overfit risk despite LOOCV; smart_contract
  R2_insample=0.94 at n=11 is fragile.
- Conclusion: correct ARCHITECTURE found (per-archetype, size-anchored, locally calibrated) but
  insufficient statistical power. Route to PM=PM = expand n per archetype + parsimonious models.

## Phase 2f — 2-archetype consolidation (power-adequate) toward PM=PM
- Per user direction (consolidate first, expand later, focus PM=PM): added coarse_of() grouping
  onchain (pallet+contract, ~30) vs offchain (app+tool, ~33) to cocomo_localcal.py.
- stratified() generalised (keyfn, cap, with_preds): each group now reports forward-selected model
  (cap=4), a SIZE-ONLY reference metric (separates stratification+size from incidental-flag overfit),
  and per-repo LOOCV predicted-vs-actual [id, pred, actual, MRE] to expose PM=PM closeness directly.
- Validated new logic (coarse split, size-only ref, pred_vs_actual) on synthetic fixtures.
- Emitted as by_archetype_2group in reports/cocomo_localcal_{pm}.json.

## Phase 2g — effort-quality gate (Boehm-style data hygiene) toward PM=PM
- 2-archetype consolidation TESTED and rejected: pooling pallet+contract (0.62/0.73->0.57) and
  app+tool (0.59/0.48->0.50) DILUTED accuracy. Finer 4-way split is more faithful; keep it.
- Per-repo predicted-vs-actual exposed the real ceiling driver: effort-measurement artifacts.
  Worst misses have implausible authoring velocity (ElasticLabs 965, ares 920, CESS 631,
  hybrid-node-research 548 delivered LOC/active-day) => git history not capturing true effort
  (imported/generated code or squashed history). Median across corpus is 84 LOC/active-day.
- Effort-quality gate (drop LOC/active-day above threshold), pooled SIZE-ONLY effect:
  none n63 SA0.444 MMRE133%; <=300 n55 SA0.541 MMRE83%; <=250 n53 SA0.563 PRED30 40% MMRE80%.
  Threshold grounded in productivity literature (delivered code accrues at tens, not hundreds,
  of LOC/day); sensitivity reported (not p-hacked).
- Implemented --maxlocday gate in cocomo_localcal.py (records threshold + excluded list); cocomo.yml
  now emits ungated AND gated(250) reports per pm bracket.
- Operational target set: PM=PM at Boehm grade == PRED(30) >= 0.70 (Conte/Boehm standard).
- Two distinct error sources separated: (1) effort artifacts (gate handles), (2) small-n overfit on
  incidental flags (prefer size-anchored parsimonious models; size_only_metrics reported per group).

## Phase 2h — MILESTONE: clean PM=PM demonstrated (gate=200, n=52)
- Effort-quality gate (LOC/active-day<=200) excluded 11 artifact repos (ElasticLabs 965, ares 920,
  dot_marketplace_v2 845, CESS 631, hybrid 548, dot_marketplace-Phase3 479, grant_mgmt 371, ajuna 305,
  clover 302, ink-analyzer-phase 290, hamster 285, FIAT 213). n: 63 -> 52.
- Pooled prospective: SA 0.593, PRED30 46%, MMRE 68% (was 0.50/30%/112%).
- 4-way gated, size-anchored (defensible) results:
    onchain_pallet  n15  SIZE-ONLY SA 0.774  exponent ln_ksloc=0.92 (PM ~ KSLOC^0.92), PRED30 47%
    offchain_app    n16  size-only SA 0.551, full 0.642
    library_tool    n12  size-only SA 0.440
    smart_contract  n9   size-only SA 0.424 (full 0.849 is has_docker overfit at n=9 — NOT claimed)
  2-group gated: onchain n24 SA 0.629 size-only (+ln_n_ink_msgs ->0.694); offchain n28 SA 0.519.
- onchain per-repo PM=PM on clean data: bit_country 13.01/12.95, fair_squares 10.1/9.89,
  delmonicos 2.42/2.37, GenesisDAO 3.56/3.37, calamar 9.3/8.37 — predicted ~ actual within a few %.
- VERDICT: clean PM=PM achievable; on-chain pallet effort follows a Boehm-form size law (SA 0.77).
  Remaining gap to uniform PRED30>=0.70 is statistical power (n=9-16/group) + off-chain effort noise.
- NEXT (step 1): expand dataset per archetype to stabilise + lift off-chain/smart_contract.

## Phase 2i — COCOMO II conformance audit (maths-security gate before expansion)
- Added docs/method/cocomoII_conformance_audit.md: element-by-element map of canonical COCOMO II
  (A,B; 5 SF Table 10; 17 EM Tables 17-34; exponent; size/reuse model; local-calibration procedure;
  schedule; accuracy standard) to implementation status. Constants/tables VERIFIED EXACT.
- Honest position recorded: classical FIXED-weight COCOMO II is implemented & run (cocomo_fit.py)
  and fails on blockchain effort (SA<0) = a finding; PM=PM comes from LOCAL CALIBRATION
  (cocomo_localcal.py), which is Boehm-prescribed (Ch.4), NOT a deviation. Claims must say
  "locally-calibrated COCOMO II for blockchain".
- Conformance GAPS to close before the full classical-sense claim (gated on W3F expansion):
  (9) reuse-adjusted equivalent SLOC (AAF/SU/AA/UNFM) not yet implemented;
  (11/5) full 22-driver local calibration needs n>=~100 (Boehm used 161) to avoid overfit;
  (12) schedule/TDEV out of scope (effort-only, stated);
  blockchain-EM identifiability to be re-tested on expanded set.
- Next: W3F-only data expansion (n>=100), then canonical size model + full-driver calibration.

## Phase 3 — W3F EXPANSION: measured 63 -> 190; gated n=102; on-chain law robust
- Root cause of small n found: measure-census left 171 candidates PENDING (batch default 'planned').
  Ran measure-census subset=all max=300 -> 173 OK measured; reliable+plausible+dedup n=190 (size-effort).
- Re-probed attributes+FS (force) for full set; cocomo_localcal gated(200) now n=102 (39 import/dump
  repos excluded incl ipfs_utilities 9080, Solang_Playground 5009, MangoBOX 3032 LOC/active-day).
- 4-way gated (size-anchored): onchain_pallet n27 SA0.76 (size-only 0.66, exp 0.69) PRED30 56%;
  smart_contract n16 SA0.83 PRED30 75% (size-only 0.54 — flag-driven, report conservative);
  offchain_app n28 SA0.60 PRED30 43%; library_tool n31 SA0.52 PRED30 39%.
- 2-group gated: onchain n43 SA0.75 size-only 0.68 exp 0.79 (ln_n_ink_msgs SELECTED, +0.07 SA =
  functional size earns place at scale); offchain n59 SA0.60 size-only 0.55.
- On-chain per-repo PM=PM at scale: openbrush 16.2/16.4, calamar 8.55/8.37, parachain_staking 23.7/25.1,
  fair_squares 9.37/9.89, CoinFabrik 2.98/3.05, ocelloids 2.77/2.68.
- Frontier: off-chain SA 0.52-0.60 (vendored JS/TS likely inflating KSLOC) -> motivates canonical
  reuse-adjusted equivalent SLOC (#23) then full 22-driver local calibration (#24, now feasible at n=102).

## Phase 3.1 — canonical reuse-adjusted equivalent SLOC (conformance gap #9) implemented
- docs/method/cocomoII_reuse_model.md: canonical AAF/AAM equations + NON-CIRCULAR origin-based
  New/Adapted rule (import-scaffold + copied-3rd-party = adapted; developed-on-top = new), judged on
  SURVIVING delivered lines, never in-window churn. Confirmed by user.
- scripts/extract/equivalent_sloc.py: blob-filtered full clone @ delivery commit; matches ksloc_code
  base (same vendored-dir + content-@generated exclusions as measure_repos); classifies via
  git-log add-origin (root-commit +24h = scaffold) + reuse-path markers; CM = fraction of adapted
  base modified later; applies COCOMO II AAM (AA=2,SU=30,UNFM=0.3,IM=10; sensitivity to follow).
  equivalent_sloc = new + adapted*AAM. Validated on synthetic repo: 65%-reused -> equiv 3.89 vs raw 10.
- .github/workflows/equiv_sloc.yml: computes + publishes equivalent_sloc to census branch (resumable).
- cocomo_localcal.py: ln_equiv_sloc added as a size candidate (only when present for all rows),
  competes with ln_ksloc in forward selection.
- Next: dispatch equivalent-sloc, then re-fit; expect off-chain to tighten (vendored/template JS
  reclassified as adapted at low AAM) with on-chain stable.
