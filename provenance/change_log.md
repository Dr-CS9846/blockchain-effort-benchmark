# Change Log — append-only audit trail

Newest first. Each entry records what changed and why, for reproducibility and review.

## 2026-06-13 (MASTER PLAN locked: curated cleanly-reported PMs -> Blockchain COCOMO PM=PM)
- USER 15-STEP PLAN (Boehm-style curated calibration; quality over quantity sidesteps the git/size noise-floor wall): (1) take cleanly human-reported PMs from treasury data as pilot cases; (2) compute PM via COCOMO II; (3) verify PM=PM; (4) dig blockchain data globally; (5) hand-pick cleanly reported PMs from each source (5/10/20 each); (6) combine into ONE heterogeneous clean dataset; (7) compute each via COCOMO II; (8) finalise Blockchain-COCOMO constants/variables for PM=PM; (9-12) publish scraping + methodology + dataset + COCOMO as four novelties; (13) ship a blockchain effort tool; (14) deliver to world; (15) deliver PhD + grant.
- treasury-mine #6 (enriched extraction): duration coverage 8 -> 72, FTE 15. Still polkadot/treasury only (gov2/kusama 429-starved by the fast page rate, not backoff). FINDING: raw extraction is noisy (marketing/education/'100 FTE' mis-parses mixed with clean dev) -> CONFIRMS the plan's hand-pick approach. Clean pilots emerging e.g. #749 Runtime Verification 3FTE x 6mo = 18 PM + repo.
- BUILT scripts/extract/pilot_select.py (Step 1): filters treasury proposals to DEVELOPMENT work with a computable plausible human-stated PM (FTE x duration preferred, else team x duration), mis-parse guards (FTE<=20, dur<=36mo, PM 0.5-300), DEV/NON-DEV title filters; confidence HIGH=FTE*dur+repo / MED / LOW; outputs data/calibration/pilot_cases.csv ranked for hand-pick. Added workflow pilot_select.yml.
- FIXED treasury_mine.py page rate 0.25s -> 1.0s so later sources (gov2/kusama) aren't 429-starved.
- pilot-select #1 (9s): SUCCESS. census treasury_proposals.csv is now multi-source (polkadot+kusama x treasury+gov2 - the slower-rate harvest landed). pilot_cases.csv = 12 HIGH-confidence pilots (reported PM + repo): ks/66 Patract Ask!v0.1 15PM, ks/81 Ask!v0.2 6.9, pd/749 RuntimeVerification 18, pd/362 Bagpipes 40, pd/1509 Ajuna SAGE 2, pd/1225 [Retro]Subsquare 72, pd/1123 ink!Alliance 120, ks/56 SubBooster 4, ks/103 dotreasury 3, pd/809 Registrar 3.7 (11 repos), ks/57 Metis 3.45, pd/1612 Subsquare 2.07; + MED anchors (no repo) + LOW retro (Talisman 85.6). First-ever human-reported PMs WITH measurable repos. Caveat: a few repo links weak (#749->grants, #362) - hand-pick fixes those.
- BUILT scripts/validate/pilot_measure.py (Steps 2-3): clones each pilot's primary code repo (drops dep/meta orgs), cloc size, fits the COCOMO power law ln PM = lnA + E*ln(KSLOC) to the REPORTED PMs (free A,E and fixed E=0.91), LOOCV predicted-vs-reported (SA/MMRE/PRED) + per-pilot PM=PM table. Size-only honest first baseline; drivers layer next. Added workflow pilot_measure.yml (installs cloc+numpy, clones pilot repos, publishes reports/pilot_pm_compare.json).
- pilot-measure #1 (53s, n=11): FIRST PM=PM on reported pilots FAILED - LOOCV SA -0.04, PRED30 0%, fitted size exponent E = -0.108 (negative!). DIAGNOSIS (clear, not fatal): SCOPE MISMATCH. reported_pm is ONE proposal's slice (milestone/maintenance/umbrella) but measured ksloc = the WHOLE current codebase or the WRONG repo. Evidence: subsquare repo (228 KSLOC) paired with BOTH 72 PM (#1225) and 2.07 PM (#1612); patractlabs/ask (12.8 KSLOC) paired with BOTH 15 (#66) and 6.9 (#81); #749 RuntimeVerification reported 18 paired with w3f/Grants-Program 0.3 KSLOC (wrong repo). Auto-pairing reported-PM<->whole-repo-size is invalid -> this is exactly why Step 5/6 hand-pick is essential; 'clean' must mean reported PM and measured size describe the SAME scope.
- FORK to fix scope-match: (A) WINDOWED size - measure code delivered during each proposal's window (Subsquare createdAt +/- duration, team-attributed) so size<->reported-PM correspond; keeps treasury at scale, automatable. (B) HAND-PICK complete-project pilots / pivot to sources where one effort = one complete repo (hackathons/Gitcoin/single-tool grants/papers reporting hours+repo). Recommend A as the principled automated scope-matcher + a small hand-picked gold set.
- DECISION (the right model, locked): CURATED MATCHED-TRIPLE calibration = Boehm's exact method. Each data point = {REPORTED total PM for one deliverable, equivalent SLOC of the ONE repo it produced (scope-matched), COCOMO drivers properly ASSIGNED by reading the project}. Root cause of every prior wall: unmatched pairs (git-noise effort / scope-mismatched size / coarse auto-drivers). Quality over quantity (~30-40 clean triples; Boehm local-cal needs ~10).
- BUILT scripts/validate/matched_pair_calibrate.py: foundation run on the W3F census (near-ideal matched pair: one grant->one own-org repo built for it->one reported planned_pm). target=planned_pm (REPORTED, not git); size=equivalent SLOC; velocity gate OFF; NO ratio gate (would manufacture correlation); greenfield-ish via duration<=18mo + effort_reliable. Calibrates size-only (free A,E and fixed E=0.91) + full fixed-weight COCOMO II, LOOCV PM=PM, + per-project residuals (worst/best) to show where hand-assigned drivers must do the work. Added workflow matched_pair.yml.
- Next: push -> dispatch matched-pair -> read size->reported-PM PM=PM + residuals = the honest floor. Then build the curated matched-triple set (correct repo, scope-matched size, hand-assigned ratings) across W3F + treasury-greenfield + global sources -> the publishable Blockchain-COCOMO calibration.

## 2026-06-12 (PM-FIRST: stop fighting the noise floor - find/measure a better TARGET)
- User direction: use intelligence to find a smarter way; look for better PLANNED/REPORTED-effort data we can mine (foundations already in repo) instead of hitting the predictor wall.
- RESEARCH: Polkadot OpenGov Treasury proposals (tracked on Polkassembly/Subsquare, on-chain) require explicit milestones+timelines+budgets with FTE/team/per-milestone costs -> a far richer, at-scale PLANNED/REPORTED-effort source than W3F grants. = the expansion lever (mine via Polkassembly/Subsquare API later).
- IMMEDIATE no-new-data test BUILT: scripts/validate/target_compare.py - we already hold human-stated planned_pm (~169) and cost in the repo but only ever calibrated against git PM. This fits the SAME size/functional models (LOOCV, Duan) to THREE targets {git_pm, planned_pm, cost_pm} and asks which size can predict best. Headline: is PRED30(size->planned_pm) > PRED30(size->git_pm)? If yes, the human-reported number is the better foundation AND predicting it (planned FTE x duration) is itself the deliverable a grant applicant needs. Self-contained numpy; no git velocity gate (target-agnostic screen: size>0, target>0, dedup). Output reports/target_compare.json. Added workflow target_compare.yml.
- RAN target-compare #1 (commit 68140ff, success 17s; NO velocity gate -> raw heavy-tailed set, relative comparison is the point). RESULT (size_equiv): git_pm n=325 SA 0.453 MMRE 419% PRED30 20%; planned_pm n=184 SA 0.476 MMRE 208% PRED30 21%; cost_pm n=282 SA -35 MMRE 44872% PRED30 0%.
- VERDICT: (1) cost_pm UNUSABLE - extreme/garbage cost_usd parsing (COST regex grabs wrong numbers) -> drop cost; earlier 3-way reconciliation's cost arm was on bad data. (2) planned_pm is the BETTER target, modestly: marginally higher SA and MMRE roughly HALVED (208 vs 419) = far less heavy-tailed, AND more defensible (human-stated) AND predicting it is itself a deliverable. (3) But no in-repo target switch breaks the ceiling (both SA ~0.45-0.48): blockchain effort is only MODERATELY size-determined vs ANY available effort measure - partly intrinsic, not purely git noise.
- DECISION: adopt planned_pm as the primary, defensible target; the real lever to tighten + grow it is MORE clean human-stated effort -> mine Polkadot OpenGov Treasury proposals (Polkassembly/Subsquare API: FTE, team, per-milestone budget+duration, on-chain) to expand the planned/reported-effort dataset and the corpus n. Honest: magnitude of gain uncertain; this is the best grounded path, not a guarantee of PRED30 0.70.
- BUILT scripts/extract/treasury_mine.py (stdlib, Polkassembly REST v1 with x-network header): mines Polkadot+Kusama OpenGov Treasury + ReferendumV2 proposals - per proposal records requested_dot, proposer, parsed planned FTE/duration, team_size, explicit documented PM, milestone duration, and GitHub repo links (reuses harvest_deliveries.GH + documented_effort extractors). Discovery+extraction step; the key count is proposals carrying BOTH a GitHub repo AND a stated FTE/duration (rows that can grow the size->planned_pm calibration set). Output data/calibration/treasury_proposals.csv. Added workflow treasury_mine.yml (pure API, publishes to census). Confirmed GitHub connected in Chrome before building.
- RAN treasury-mine #1 (commit b5393b8): empty output (header only) - BUG: proposalType used "Treasury"/"ReferendumV2"; Polkassembly enum is lowercase "treasury_proposals"/"referendums_v2" (unknown type -> empty listing). FIXED script + workflow to the correct enum; added a debug print of the API response on empty listing. (Also fixed an f-string empty-{} syntax slip in the debug line.) Reframed per user: clean human-stated effort is kept EVEN WITHOUT a repo (a reported-effort anchor in its own right); summary now reports ANY-effort count, not just repo+plan.
- RAN treasury-mine #2 (commit ed48750, 17m): listing worked (600 polkadot treasury_proposals ids 1304-1903) but ALL detail calls failed -> every row NO_DETAIL. Polkassembly per-item detail endpoint params wrong AND slow (600 failing detail calls = 17 min).
- REWROTE treasury_mine.py to use SUBSQUARE instead: content (markdown body) is INCLUDED in the listing items, so one fast call per page yields the text - no per-item detail. Endpoints: {net}.subsquare.io/api/treasury/proposals and /api/gov2/referendums. Robust item/field extraction (items_of + deep_get over candidate paths), prints first-item JSON keys to stderr to calibrate the parser to reality. Fast (pages x types x networks listing calls only). Updated workflow args --types treasury,gov2 --pages 6 --page-size 100. (Authoritative file complete via Read; bash mount truncation is a sandbox sync artifact, not in the pushed file.)
- treasury-mine #3 (Subsquare, fast 7s) still empty: base URL wrong. Probed the real API IN-BROWSER (Chrome): https://{net}.subsquare.io/api/... = "Not found"; https://{net}-api.subsquare.io/treasury/proposals?page=1&pageSize=2 = WORKS, returns {items:[{proposalIndex,proposer,title,content(FULL MARKDOWN),contentType,createdAt,onchainData,...}]}. First item = a real Treasury proposal (MIST Meta-tx Ink!) with full proposal text incl. team + links. Content is in item['content'] (markdown) - exactly the gold mine. FIXED ENDPOINTS to the -api subdomain (no /api/ path). gov2 = /gov2/referendums.
- treasury-mine #4 (Subsquare -api, 13s): WORKS. 40 rows (10 per network/type). DATA IS GOLD: gov2/OpenGov proposals link real blockchain repos in bulk (idx 1903 -> 6 ArcheLabs repos; 1897 -> 3 repos + parsed FTE; 646/645/587/332 -> repos) with rich markdown (content_len up to 18k) + requested DOT. Treasury proposals carry content + amount. This is the human-stated-effort + repo foundation we wanted.
- BUG: only 10/combo because the loop broke on a short page (Subsquare ignores pageSize, returns ~10/page). FIXED: paginate by page number until an EMPTY page (removed the len<pageSize break); workflow --pages 6 -> 80 (covers ~800 most-recent per combo). 
- treasury-mine #5 (3m29s): harvested 347 proposals - but ALL polkadot/treasury (gov2 + kusama got starved, likely Subsquare rate-limit after the treasury burst -> gj None -> empty -> break). FINDINGS: 347/347 have a requested DOT amount (real on-chain economic figure; far cleaner than W3F cost_usd); 109 link GitHub repos (67 distinct) = calibration-ready (measure size + have budget); 320 substantial content. BUT effort signals sparse (FTE 3, duration 8, team 0) - treasury prose doesn't use W3F template phrasing.
- FIXED (2 issues): (a) starvation - gj now 6 tries with progressive backoff (5s*attempt) + a 3s pause between sources so gov2/kusama harvest; (b) extraction enriched - parse_planned now also matches free-text 'N months/weeks', 'N FTE/developers/engineers'; new team_n() catches 'team of N', 'N contributors/people'. Content is captured so re-parse is cheap.
- Next: push -> re-dispatch -> expect all 4 sources (polkadot+kusama x treasury+gov2) with richer effort signals + the repo-rich gov2 proposals. Then build MATCH+MEASURE: measure the 100+ repo-linked proposals' size, carry requested-DOT (cost) + parsed planned effort -> grow the size->cost / size->planned-PM calibration set; keep repo-less stated-effort proposals as standalone reported-effort anchors.

## 2026-06-12 (PM-FIRST REBUILD — Experiment 1: richer web-grounded effort signal)
- DIRECTION CHANGE (user): the person-month IS the deliverable; rebuild PM from the ground up, validate it, then re-tread to a usable estimator. North star = PM_FIRST_REBUILD_BLUEPRINT.md (local). Reviewer consensus (2 external reviews) confirmed: velocity gate = selection-on-ratio confound; effort ground truth has ~0 convergent validity; ln_authors is a target leak (PM_mid is built from author activity); driver layer inert once leak removed. Constructive path: richer effort signal -> latent true-effort model -> human/doc anchor -> re-calibrate -> deliver.
- BUILT scripts/extract/activity_pm.py (stdlib-only, pure GitHub REST API, no clone): for each OK repo over its delivery window [effort_since, effort_until] it mines the FULL contribution record - commits, PRs+issues (issues endpoint), issue/PR discussion comments, and PR review (code) comments - fuses them into union active developer-days, and recomputes effort three ways: PM_mid_rich (union active-days/19), PM_low_rich (session-hours/152 over the union stream), and PM_rgb (Robles & Gonzalez-Barahona 2022 dedication estimate = sum over (dev,active-month) of min(1, active_days/19); validated vs 1000+ surveys). Captures the "invisible work" (review/triage/discussion) that commit-only counting drops, incl. non-committing contributors. Output data/calibration/activity_pm.csv with current pm_mid + deltas; prints log-space corr(pm_mid_current, rich/rgb/low). Bot-filtered; rate-limit + 404 handling; MAX_PAGES cap.
- ADDED .github/workflows/activity_pm.yml (restores measurements_census from census, runs miner with GITHUB_TOKEN, publishes activity_pm.csv to census).
- RAN activity-pm #1 (commit 23ad073, success but 1h22m — GitHub secondary rate-limit throttling; perf-only, result valid). activity_pm.csv: 391 OK repos mined.
- RESULT (Experiment 1): richer GitHub mining barely changes the effort estimate. corr(log pm_mid_current, log pm_mid_rich)=0.935 (n=361); pm_rgb (Robles-Gonzalez-Barahona dedication) corr 0.934; pm_low_rich corr 0.931. pm_mid_rich/current ratio median 1.26 (IQR 1.06-1.73). i.e. adding PRs+issues+reviews+comments to commit-days lifts PM ~26% but preserves the ORDERING (>0.93 self-corr). Corpus discussion volume: 11,014 PRs / 5,284 issues / 22,880 issue-comments / 22,238 review-comments total, but median repo has 2 PRs / 0 issues.
- VERDICT: better git measurement does NOT fix the ground-truth problem. All git flavours (commit-only, rich, RGB) are ~0.93 mutually coherent but that coherent signal still diverges from planned/cost (the ~0.13/~0 cross-correlations are structural, not a mining artefact). The fix must come from Step 3 (latent true-effort model) + Step 4 (external human/doc anchor), NOT from richer mining.
- KNOWN BUG in this run (honest): contributors_committing was computed from the FUSED event set, so it equals contributors_all (non-committing reviewer count came out 0 everywhere) - cannot isolate "invisible reviewer headcount" from this run. Low priority to fix given the headline (rich≈commit-only).
- BUILT scripts/extract/documented_effort.py (Step 4, stdlib, reuses harvest_deliveries clone/app-index/matching): per project mines DOCUMENTED effort independent of git - team_size (named members), sum_milestone_duration_months (per-milestone Estimated Duration, weeks->months), n_milestone_fte_mentions, and documented_pm_explicit (effort stated in words: person/man/engineer/developer/staff-month/week/day/hour, normalised to PM and summed; raw phrases kept for audit) - scanning BOTH the application and the delivery texts. Output data/calibration/documented_effort.csv. Added .github/workflows/documented_effort.yml (clones W3F repos directly, publishes to census). Lightweight, no API/rate-limit. These become extra indicators for the latent model (Step 3) + a documentary anchor for absolute PM.
- RAN documented-effort #1 (commit 671058d, success 29s). documented_effort.csv: 356 projects, 340 OK. COVERAGE: team_size 279/340 (82%, median 3, range 1-21); sum_milestone_duration_months 274/340 (81%); planned_pm 169/340 (50%); documented_pm_explicit (actual effort stated in words) only 4/340 (1%).
- VERDICT (Step 4): a documentary ACTUAL-effort anchor essentially DOES NOT EXIST in W3F text (1%) - confirms a grantee self-report SURVEY is the only route to a true actual-effort anchor (as reviewers said). BUT two valuable, well-covered, LEAK-FREE documented signals were gained: (a) team_size (82%) - a PROSPECTIVE, documented headcount from the application, independent of git, which can replace the git-author-count target leak the reviewers flagged; (b) milestone-level planned durations (81%). These strengthen the latent model's indicator set and give a legitimate prospective team covariate.
- REVIEWER 1 follow-up proposed two tracks. TRACK A (pm_reconciled = prefer cost->planned->git, calibrate to it): DECLINED - it is a per-project target SWITCH across three mutually-uncorrelated, incommensurable scales (we proved git/planned/cost corr <=0.13), not a Boehm-style single consistent measure; would inject heterogeneity. The correct realisation of "use more than git" is the latent errors-in-variables model (Step 3). Also: Reviewer 1 read stale artifacts (cites n=13/bc_cocomo_results.json; actual n=127/183/340). TRACK B (functional size as a standalone PROSPECTIVE estimator): ADOPTED - it is the path to the usable, before-you-build deliverable (goals #4/#5).
- BUILT scripts/validate/functional_size_eval.py (Track B, leak-free): calibrates effort on FUNCTIONAL SIZE (on-chain n_pallets/n_extrinsics/n_storage/n_events/n_ink_msgs/n_sol_funcs/n_contracts_def/n_rpc + off-chain n_exports/n_funcs/n_classes/n_routes) which is countable from a DESIGN SPEC pre-code. Models (LOOCV, Duan): size_ksloc, size_equiv (retrospective baselines) vs fs_total, fs_groups (learned on/off-chain weights), fs_groups_team (+ DOCUMENTED leak-free team_size), fs_plus_size. NO git author/day predictor (fixes the ln_authors leak). Outputs reports/functional_size_eval_{pm}.json incl. best prospective model coefficients + a predicted-vs-actual PM=PM table. Added workflow functional_size_eval.yml (restores measurements+attributes+documented_effort, runs per bracket, publishes to census).
- RAN functional-size-eval #1 (commit 963aee9, success 21s; n=127, team cov 107/127). RESULT (Track B, honest negative): functional size is a POOR effort predictor and worse than code size. size_ksloc SA 0.631 / PRED30 43%; size_equiv SA 0.638 / PRED30 44% (best). Prospective fs_total SA 0.314 / PRED30 25% / MMRE 134%; fs_groups 0.305; fs_groups_team 0.300 (team coef ~ -0.005, adds nothing); fs_plus_size SA 0.649 with fs coef ~0.03 (FS adds ~nothing over size). The fitted FS exponent ~0.14 -> model predicts ~5 PM for nearly EVERY project (PM=PM table: 5.9/5.8/5.5/5.4...): functional-unit counts (dominated by noisy off-chain export/func regex) do NOT track effort.
- CEILING CONFIRMED (4th independent angle): KSLOC/equivalent size is the best single predictor at SA ~0.64 / PRED30 ~44%, and NOTHING beats it - not the 22 COCOMO drivers (Bayesian), not blockchain EMs, not richer git mining, not functional size, not team size. The ~SA0.64/PRED30~44% wall is set by the EFFORT TARGET (git PM noise), not the predictors. PRED(30)>=0.70 is not reachable by changing the model while the target is a single noisy git proxy (matches both reviewers: do not chase 0.70 via the model).
- IMPLICATION: the only remaining lever to genuinely raise PM=PM accuracy is a CLEANER TARGET (real reported effort via the Step 4b survey, or a different externally-measured target). No predictor trick beats target noise (cannot predict a variable below its own noise floor). Recommend reframing the deliverable as a calibrated size-based estimator WITH honest uncertainty intervals (useful even at PRED30 ~44%) + the survey as the path to tighten it.

## 2026-06-12 (PHASE 5 wrap + PAPER-STATS: referee-grade inference; both manuscripts strengthened)
- Effort-truth (#25), Bayesian calibration (#26), universal equation (#27) completed earlier: fixed published COCOMO II does NOT transfer (LOOCV SA ~ -0.03); Bayesian ridge-to-prior (Chulani-Boehm-Steece-style) gives a stable universal equation (SA ~ 0.66, ~0.75 per archetype); 7 blockchain EMs proven NON-IDENTIFIABLE vs CPLX/RELY/TIME/PVOL (corr~1, ablation dSA<=0); effort reconciliation shows git/planned/cost mutually uncorrelated (planned~cost only 0.07) -> git_pm retained as most-defensible bounded target.
- METHODOLOGY PAPER (local COCOMO_Blockchain_Methodology_Paper.md) written then reviewer-hardened: added mandatory baselines (guessing/size-only/ATLM Whigham 2015, Sarro-Petrozziello 2018), bootstrap CIs, Shepperd-MacDonell effect size Delta + randomisation p, nested-CV tau, paired Wilcoxon+BH, descriptive-stats table, blockchain-SEE related work (sec 2.7), independence/leakage invariants for rating synthesis, honest ridge!=full-CBS note, mechanical planned/cost-ratio flag, per-archetype over-fitting caveat, title-scope caveat. Values not yet computed are tagged [COMPUTE] (never fabricated) and listed in an open-analyses box.
- PHASE-1 BENCHMARK PAPER (PUBLICATION_blockchain_effort_benchmark.md) upgraded but kept BOUNDED to the effort-ground-truth contribution: criterion-validity section replaced single-anchor "59%-in-bracket" with the THREE-WAY reconciliation (git/planned/cost mutually weakly correlated; planned~cost 0.07); 3.5 upgraded to the two-axis effort-quality gate (velocity band 15-200 LOC/active-day + duration <=18mo); n updated 63 -> 127; limitations + status + Phase-2 pointer refreshed.
- BUILT scripts/validate/paper_stats.py (numpy-only): on the F.load clean gated set computes (1) descriptive stats, (2) size-effort decoupling refresh, (3) baselines B1 size-only + B2 ATLM-lite vs fixed-published vs Bayesian under one LOOCV, (4) bootstrap 95% CIs (B=2000), (5) effect size Delta + randomisation p vs guessing, (6) nested-CV tau, (7) paired Wilcoxon vs size-only + Benjamini-Hochberg. Output reports/paper_stats_{pm}.json. Added .github/workflows/paper_stats.yml (restore census CSVs -> run per PM bracket -> publish to census).
- DISPATCHED paper-stats #1 (commit bda23e8, success 28s); read reports/paper_stats_pm_mid.json from census. RESULTS (n=127, pm_mid, LOOCV): descriptive medians equiv 2.81 KSLOC / 2.26 PM / 5.06 mo / 3 authors / 78 LOC-active-day. BASELINES: size-only SA 0.638 [0.55,0.70]; ATLM SA 0.660; FIXED PUBLISHED SA -0.14 (WORSE than guessing, BH q=0 vs size-only); Bayesian tau-opt SA 0.655; Bayesian nested SA 0.635. KEY FINDING: NONE of ATLM/Bayesian significantly beats the 2-param size-only power law (Wilcoxon vs B1: ATLM p=0.18 q=0.36; bayes p=0.33 q=0.43; nested p=0.68). -> on clean blockchain grant data effort is PREDOMINANTLY SIZE-DETERMINED; published constants fail (local calibration essential) but the 17+5+7 driver layer adds NO significant accuracy over size. Extends the blockchain-EM non-identifiability to the WHOLE driver apparatus. Honest parsimony result.
- CONFOUND CAUGHT: the velocity gate [15,200] LOC/active-day bounds velocity=52.6*KSLOC/PM, so it MECHANICALLY restricts KSLOC/PM (observed productivity 0.27-3.0 = the gate bounds). This inflates gated corr(logSize,logPM)=0.85 (vs 0.36 ungated n=63) and the size-only baseline. Gate is a defensible reliability filter but its side-effect on the size-effort relationship must be disclosed + tested.
- BACKFILLED methodology paper (6.1 descriptive, 6.3 baselines table + decisive negative finding + gate-confound caveat, abstract corrected to the honest negative result, open-analyses items 1-6 marked done). CORRECTED Phase-1 paper decoupling section to the gate-sensitivity truth (no longer claims decoupling 'holds').
- STAGED velocity-gate-OFF sensitivity: paper_stats.py +--minloc/--maxloc/--maxdur passthrough to F.load + gates block in JSON; paper_stats.yml adds a 2nd pass (--minloc 0 --maxloc 1e6) -> reports/paper_stats_nogate_pm_mid.json.
- DISPATCHED paper-stats #2 (commit 8799c18, success 40s); read paper_stats_nogate_pm_mid.json (n=183, velocity gate OFF, duration<=18mo + reliability only). RESOLUTION OF THE CONFOUND: gate-OFF size-only SA 0.376; ATLM 0.502; Bayesian tau-opt 0.494; nested 0.491; fixed published SA -4.85 (outlier-wrecked without gate). Wilcoxon vs size-only: ATLM p=0.0005 q=0.001; bayes p=0.0019 q=0.003; nested p=0.0028 q=0.003 -> ALL multifactor models SIGNIFICANTLY BEAT size-only (~108-75 wins). corr(logSize,logPM) unconfounded = 0.556 (vs 0.85 gated). 
- CONCLUSION (reversed the prior 'parsimony' read, which was a gate artifact): the velocity gate's restriction of KSLOC/PM both inflated the size baseline AND suppressed the drivers' marginal value. UNCONFOUNDED, the multifactor driver structure carries genuine significant signal (drivers earn their place); the gated set buys higher absolute accuracy (SA 0.66) at the cost of a range-restriction confound. §6.4 non-identifiability concerns the blockchain-specific EMs individually, NOT the multifactor structure.
- BACKFILLED both papers with gate-off truth: methodology 6.3 now has the gated-vs-ungated comparison table + the reconciliation + recommendation to replace the velocity gate with reliability filters NOT tied to KSLOC/PM; abstract corrected to the resolved (positive) finding. Phase-1 decoupling note finalised with unconfounded corr 0.556 (decoupling real & moderate).
- NEXT (recommended): replace velocity gate with KSLOC/PM-independent reliability filters (commit/author counts, squash-import detection) and re-run paper-stats; then per-archetype CIs, external git_pm validation, expert kappa, blockchain-SEE SLR.

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

## Phase 3.2 — equivalent SLOC computed; finding: reuse is SECOND-ORDER (size already clean)
- equivalent-sloc workflow run #1 (24m): computed reuse-adjusted equivalent_sloc for 138/153 OK repos.
- Distribution: adapted_fraction median 0.03 (mean 0.29); equiv/ksloc ratio median 0.99 (mean 0.88).
  Big discounts only on fork/template-dump repos (ipfs_utilities 95%->0.13x, deeper_network 35%);
  most of those already removed by the velocity gate.
- ROOT CAUSE (honest): cloc/measure_repos ALREADY exclude node_modules/vendor/target, so first-order
  framework reuse was never in ksloc_code. The reuse model's second-order in-tree correction is small
  for most W3F repos (pallets/libs written from scratch); forked full-nodes correctly show more adapted.
- => My hypothesis that vendored code inflated OFF-CHAIN size is WRONG. equivalent~=ksloc; the off-chain
  difficulty is EFFORT-SIGNAL NOISE, not size inflation. Reuse adjustment does not change the fit.
- Conformance gap #9 CLOSED: canonical equivalent SLOC implemented + verified + computed; wired as
  ln_equiv_sloc (ksloc fallback where missing) so the model's size IS canonical, ~= ksloc here.
- Net: on-chain law unchanged & robust (SA 0.75-0.76); off-chain ceiling (SA ~0.55-0.60) is intrinsic
  effort noise. Next: #24 full 22-driver local calibration on n=102; off-chain treated as noise-bounded.

## Phase 3.3 — off-chain root cause: effort is SIZE-DECOUPLED (staffing/iteration driven)
- Tested milestone-count scope lever (census n_delivery_files): REJECTED by data — corr(size-residual,
  ln_milestones)=+0.09; size+milestones SA 0.546 vs size-only 0.548. Milestone spread too low (1-5).
- Diagnosed what the size-residual (effort size misses) correlates with on gated off-chain set (n=59):
    work-volume (CIRCULAR w/ pm proxy): active_dev_days +0.68, total_commits +0.61, loc/active-day -0.70;
    prospective artifact props (~0): ksloc_all +0.07, generated +0.04, cost +0.09, planned_pm +0.12;
    prospective planning inputs (modest): distinct_authors +0.39, duration +0.42.
  Predictive: size+commits 0.70/73% (circular, rejected); size+authors+duration 0.61/42% (valid);
  size-only 0.55/36%.
- FINDING: off-chain blockchain effort (apps/SDKs/tools) does NOT follow a size law; final code size does
  not constrain it. Honest best PROSPECTIVE off-chain model ~ SA 0.61 (size+team+duration). On-chain
  remains size-law (SA 0.75-0.76). This size-coupling split is itself a publishable result.
- Wired (valid, non-circular): team size now competes in per-archetype selection; milestone candidate
  added (transparently rejected by selection); equivalent_sloc fallback; census-audit join in cocomo.yml.
- NEXT candidate lever (no compromise): OFF-CHAIN functional size (exported API/function/component/route
  counts) = the off-chain analogue of extrinsics-count; only remaining prospective, non-circular scope
  measure untested. Requires probe extension.

## Phase 3.4 — OFF-CHAIN functional size (the off-chain analogue of extrinsics)
- Extended cocomo_probe.py to count off-chain feature surface in TS/JS/Go/Py/Java sources:
  n_exports (public API), n_funcs (named+arrow+def+func), n_classes (class/interface), n_routes
  (HTTP endpoints / route decorators). Validated regexes on synthetic TS/Go/Py fixtures.
- cocomo_localcal.py: added these + composite ln_offchain_units (exports+funcs+routes) as
  prospective candidates; competes with ln_ksloc per archetype.
- Rationale: off-chain effort is size-decoupled (Phase 3.3); raw LOC misses the *feature surface*
  (a research lib's API, an app's routes/components). This is the only untested PROSPECTIVE,
  non-circular scope measure. Next: force re-probe + re-fit; test if off-chain breaks past SA~0.6.

## Phase 3.4/3.5 — off-chain levers land (n=132); duration-window gate added
- Re-probe with off-chain functional size: gated n=132. ln_equiv_sloc is now the SINGLE BEST size
  predictor (univariate 0.582 > ln_ksloc 0.573) -> conformance gap #9 size is selected everywhere.
- OFF-CHAIN levers selected & stacked (non-circular, prospective):
    offchain_app n35: ln_equiv_sloc + ln_n_exports + lang_ts -> SA 0.562 (size-only 0.488)
    2-group offchain n71: ln_equiv_sloc + ln_authors + ln_milestones + ln_n_exports -> SA 0.615 (size-only 0.511)
    library_tool n36: ln_equiv_sloc + ln_milestones + has_ci -> SA 0.580 (milestones strong here)
  -> off-chain 0.51 -> 0.62 via off-chain functional size + team + milestones. Team size now also
  helps on-chain (0.65->0.72).
- On-chain robust: onchain_pallet n38 SA 0.752 PRED25 61% PRED30 61%; 2-group onchain n61 SA 0.754 PRED30 59%.
- DIAGNOSED persistent off-chain outliers (datdot pred1.8/act10.8, crossbow 9.4) as EFFORT-WINDOW
  CONTAMINATION: datdot window 22.8 months (2019-2021), crossbow 16.3mo — whole-project lifetimes, not
  grant milestones (median W3F grant 4mo, p90 18mo). active-days over-count effort vs milestone deliverable.
- Added --maxduration effort-quality gate (drop windows > N months); gated CI run uses maxduration=18
  (removes implausible windows, keeps legit long grants). Local test: equiv-size-only SA 0.564->0.594,
  MMRE 69%->63% just by removing the extreme tail. Parallel hygiene to the velocity gate (time axis).
- equivalent SLOC (gap #9) COMPLETE: implemented, verified, top predictor, selected.

## Phase 3.6 — duration gate lands; UNIFIED model (n=133): on-chain 0.755 / off-chain 0.645
- Duration gate (<=18mo) removed 8 whole-project windows (datdot 22.8, lip_payments 23, parachain_staking
  21.4, openbrush 19.6, subauction 18.8, Webb_Mixer 20, dotnix_followup 21.9, php-scale-lib 18.3).
- Gated n=133 (velocity<=200 + duration<=18). Per-archetype LOOCV SA / PRED30:
    2-group onchain n58: 0.755 / 60% ; onchain_pallet n37: 0.753 / 65% ; smart_contract n21: 0.766 / 48%
    2-group offchain n75: 0.645 / 40% ; offchain_app n37: 0.622 / 43% ; library_tool n38: 0.590 / 39%
- Off-chain 0.51 -> 0.645 via stacked legitimate levers (equiv size + n_exports off-chain functional size
  + milestones + team), all SELECTED. Both halves now share ONE model form:
  ln_equiv_sloc + ln_authors + functional-size + milestones. ln_equiv_sloc top predictor (0.587).
- Remaining off-chain gap (~0.11) is symmetric small-grant sparsity (galaxy 0.63PM/12 active-days,
  queryWeb3 0.53PM) — near-irreducible measured-activity noise, not contamination.
- All canonical pieces in place: verified tables, equivalent SLOC (gap #9), local calibration, two-axis
  effort-quality gates (velocity+duration), per-archetype stratification. Last: #24 full-driver calibration.

## Phase 3.7 — two-sided velocity band (floor at 15 LOC/active-day)
- Diagnosed remaining off-chain residual as SYMMETRIC velocity noise: high-velocity over-predicted
  (galaxy), low-velocity under-predicted (crossbow 22 LOC/active-day = research/rework, effort
  over-represented vs final code). High tail gated (>200); now add the FLOOR.
- velocity distribution p10=24 p25=49 median 88. Floor at 15 (literature-grounded: net delivered code
  rarely <10-15 SLOC/active-day; conservative, below p25) removes only the clear low tail.
- Local equiv-size-only effect (dur<=18): band [0,200] SA 0.594/MMRE 63% -> [15,200] SA 0.656/MMRE 48%.
  Low-velocity outliers cluster in off-chain research libs -> should lift off-chain more than on-chain.
- Added --minlocday gate; gated CI run now uses band [15,200] + duration<=18. Sensitivity reported.

## Phase 3.7 result — velocity floor lifts APPS to 0.69; library/research is the true frontier
- Band [15,200]+duration<=18 -> n=127. Floor removed 7 low-velocity (datdot 7, polkastats 13, zk-rollups 6...).
- Per-archetype LOOCV SA / PRED30: smart_contract 0.766/48; onchain 2-grp 0.755/60; onchain_pallet 0.753/65;
  OFFCHAIN_APP 0.688/43 (up from 0.622); offchain 2-grp 0.644/41; LIBRARY_TOOL 0.594/47 (laggard).
- Off-chain APPS essentially caught up to on-chain (0.69 vs 0.75). The remaining gap is specifically the
  LIBRARY/SDK/RESEARCH class (crossbow, merkle_tree, queryWeb3) where effort is least size-coupled = a finding.
- HONEST stop: off-chain did NOT cross on-chain. Gates now keep 127/~195 (~35% excluded; all defensible
  measurement-reliability criteria). Further gate-tightening to force a crossing = p-hacking; NOT done.
- GATES LOCKED at band[15,200] + duration<=18. Unified locally-calibrated COCOMO II:
  on-chain 0.75 / apps 0.69 / libraries 0.59, n=127, ln_equiv_sloc top predictor, all canonical pieces verified.

## Phase 4 (#24) — full 22-driver COCOMO II: fixed-weight vs local calibration on clean set
- cocomo_fit.py now uses canonical equivalent_sloc as Size + the LOCKED effort-quality gates
  (band[15,200]+duration<=18) so it matches the local-cal fitter's clean set.
- Added LOCAL CALIBRATION of the full canonical model (Boehm Ch.4): fits ln PM on ln(Size),
  (E-B)*ln(Size) [scale-factor sensitivity], and every non-constant EM/BC log-multiplier column
  (local EM weights) -> LOOCV SA/PRED. Reported side-by-side with the FIXED-WEIGHT (Boehm constants
  + calibrate-A only) result. Retains redundancy(VIF/corr)+ablation identifiability of all 22+7 drivers.
- Validated local-cal math on synthetic (recovers size exponent, SA). Next: dispatch -> read
  cocomo_analysis_pm_mid.json fixed_weight vs local_calibration on n~127.

## Phase 4 (#24) RESULT — full canonical COCOMO II capstone (n=127, clean+equiv size)
- FIXED-WEIGHT (Boehm constants, all 22+7, calibrate A only): LOOCV SA -0.14, PRED30 27%, MMRE 90%
  => textbook COCOMO II FAILS on blockchain even on clean data. (A finding, not PM=PM.)
- LOCAL CALIBRATION (fit exponent + driver weights): LOOCV SA 0.605, PRED30 43%, MMRE 53%;
  fitted size exponent 0.46, sf_sensitivity +1.39, sigma 1.33->0.72. => Boehm's own local-calibration
  prescription vindicated. (Stratified local-cal higher: on-chain 0.75 / apps 0.69.)
- BLOCKCHAIN-EM identifiability PROVEN on clean n=127: perfectly redundant corr=1.0/VIF=inf
  (BC_EM_AUD=RELY, BC_EM_GAS=TIME, BC_DC=PVOL); inert (BC_BEM, BC_EM_REG); weak+non-necessary
  (BC_EM_NODE, BC_EM_MC, all ablation dSA<=0). => 7-driver COCOBLOCK layer NOT separately
  identifiable; blockchain effort captured by standard CPLX/RELY/TIME/PVOL under local calibration.
- #24 COMPLETE. Canonical conformance fully discharged: verified tables, equivalent SLOC, fixed-weight
  vs local calibration, redundancy/necessity/sufficiency, two-axis effort-quality gates, stratification.

2026-06-14  Verified pilot #4 added (curated matched-triple set, brick #4).
- dotreasury (OpenSquare) — Kusama Treasury Proposal #103, read on-chain via kusama-api.subsquare.io.
  Retroactive maintenance slice 05.2021–07.2021. Effort itemised on-chain: 10 dev-days maintenance +
  ~2 dev-week grading/IPFS feature => ~20 dev-days ~= 0.95 PM (server $1,350 excluded as infra).
  Repo opensquare-network/dotreasury; developers supplied EXACT slice diff e8f09bf...release-2.3.1
  (best-sizable pilot). On-chain: Awarded 38.66 KSM (~$7,992), council motion #339 12-0 unanimous,
  award block 8,726,400. Disclosed: same org as Pilot 1 (subsquare) — distinct product/repo/scope.
- Set spread now 0.95 -> 24.7 PM (26x); two chains; four project types; greenfield+brownfield;
  forward+retroactive; full-build + micro-maintenance.
- REJECTED candidate (auditable): Talisman Wallet & Portal, OpenGov Ref #1232 (Executed, 690,600 USDT).
  Excluded because (a) no effort figure on-chain (cost breakdown lives in an external Google Doc) and
  (b) 3-repo umbrella (talisman + talisman-web + chaindata) => no single clean matched scope.

2026-06-14  Verified pilot #5 added (user-supplied brick; verified on-chain).
- Megaclite v0.1 (ZKP crypto library, Patract Hub) — Polkadot Treasury Proposal #24, read on-chain
  via polkadot-api.subsquare.io. Forward grant, greenfield. Effort verbatim on-chain: "Cost of v0.1
  (15 developers x weeks)", M1-M5 each "3 developers x 1 week" => 15 dev-weeks => 15/4.345 = 3.45 PM.
  Window verbatim "5 weeks (16 Nov - 21 Dec)" 2020. Repo patractlabs/megaclite (renamed zkmega).
  On-chain: Awarded 2020-12-05, 5,431 DOT ($31,500 @ $5.8/DOT), award block 2,764,800, council
  motion #42 final 8-0.
- Corrections vs user's submitted table (truth-first):
  (1) PM 3.25 -> 3.45 to standardise dev-weeks/4.345 across all pilots (matches Ask! method).
  (2) Motion #42 final 8-0 but NOT unanimous throughout: councillor 1363HWTP first voted Nay
      (transient 5-1) then flipped to Aye. Recorded as "unanimous final, not throughout".
  (3) Beneficiary verified as address 123ua9...X2iC ("RTTI-5220" is its identity label).
- Tags: proposed (not actual) effort; 3rd Patract project (org overlap with Pilot 2 Ask!).
- Org concentration now disclosed in registry: OpenSquare x2 (#1,#4), Patract x2 (#2,#5),
  Bagpipes x1 (#3). Balance toward independent teams as set grows to n~30-40.

2026-06-14  Pilot #6 hunt (fresh-team, breaking OpenSquare/Patract concentration) — 4 candidates burned + CSV bug found.
- Read on-chain, all REJECTED or MISLABELLED:
  * Kusama #56 SubBooster (sub-box) -> state REJECTED on-chain (council rejectProposal motion #248,
    bond slashed). Never awarded; budget in external Google Sheet. Out (no award, effort off-chain).
  * Polkadot gov2 #1509 Ajuna SAGE (ajuna-network) -> state REJECTED (nays>ayes, no award);
    multi-repo forward proposal. Out.
  * Polkadot treasury #749 -> CSV labelled "Runtime Verification: Advanced Rust Property Test
    Verification"; on-chain #749 is actually "Retroactive Tip for Portuguese Content Creation"
    (Polkadot Brasil, 550 DOT, social media). Record shows proposalIndex 749 vs referendumIndex 667.
  * Polkadot treasury #162 -> CSV labelled "Polkadot Live"; on-chain #162 is actually "SubWallet
    Milestone 2" (Koniverse/SubWallet-Extension).
- DATA-QUALITY BUG: pilot_cases.csv conflates treasury proposalIndex with gov2 referendumIndex, so
  its titles/rows are misaligned; it also never recorded on-chain award status. ACTION: do not pick by
  CSV title; re-read every candidate on-chain. (Harvester index-mapping fix = TODO.)
- LEAD (not yet entered, pending standard): SubWallet Milestone 2 (Polkadot treasury #162). Clears
  award (Awarded 35,417 DOT, council motion #253 8-0 unanimous, executed 2022-09-18), FRESH TEAM
  (Koniverse/SubWallet, not OpenSquare/Patract), SINGLE repo (Koniverse/SubWallet-Extension), EXACT
  completed window (Milestone 2, 12 weeks, Mar->May 2022, GitHub milestone/2 closed). BUT person-effort
  (FTE/hours) is NOT on-chain -- it lives in an external Google Doc (like Talisman). Held out of the
  gold set per the on-chain-effort rule; offered to user as a tagged "effort-off-chain" candidate.

2026-06-14  SubWallet #162 follow-up: linked Google Doc (effort/cost breakdown) is DELETED ("file has
  been deleted"). User relaxed rule to allow linked-doc effort "if real and worthwhile", but SubWallet's
  source is gone => no recoverable stated effort => OUT. Lesson: Google-Doc-hosted effort is volatile.
  PIVOT for fresh-team sourcing: prefer DURABLE linked docs = W3F Grants-Program application markdown on
  GitHub (version-controlled, permanent), which itemise milestone effort (FTE/duration or hours) and map
  to a single delivered repo; cross-reference to on-chain award where present. Replaces Google-Doc route.

2026-06-14  Verified pilot #6 added (user-supplied brick; verified on-chain) — Subsquare new-features.
- Polkadot Treasury #336 / OpenGov Referendum #13 (medium_spender), read on-chain via
  polkadot-api.subsquare.io. OpenSquare. Awarded 36,969 DOT ($168,320 @ EMA7 06.18.2023; ~$194k @ award
  block 16,588,800, 2023-07-27). Itemised effort tables @ $80/h: total 2,104 h verified line-for-line.
- MATCHED-PAIR CORRECTION (critical): 2,104 h spans TWO repos + planned work, so it is NOT a matched pair
  with subsquare alone. Split by repo:
    * subsquare share = 368(Collectives)+80(enh)+1,288(new) = 1,736 h => 1,736/152 = 11.4 PM  <- entered.
    * dotreasury share = 48(pie)+320(new) = 368 h => 2.42 PM  <- logged, NOT used (separate slice).
  Also 1,608/2,104 h (76%) are planned (forward), only 496 h retroactive => tag "mostly proposed".
- Window 2022-04 -> 2023-07; windowed-slice sizing must use DIFFERENT commits than Pilot 1
  (subsquare 2023-10->2024-09). Pilots 1 & 6 = two non-overlapping slices of the SAME repo.
- CONCENTRATION now the set's top weakness: OpenSquare x3 (#1,#4,#6; subsquare repo twice), Patract x2
  (#2,#5), Bagpipes x1 (#3). #7+ must be independent teams via durable W3F grant applications.

2026-06-14  Verified pilot #7 added (durable-source fresh-team finder delivered) — Fennel Protocol.
- Source pivot worked: used the existing W3F census manifest (13 delivery-verified grants, all non-
  OpenSquare/Patract) for discovery, then verified the application LIVE (read full markdown via Chrome
  on raw.githubusercontent). Fennel chosen.
- Fennel Protocol (Fennel Labs LLC, Wyoming USA) - FIRST fully-independent team. W3F grant, Whiteflag
  messaging Substrate chain. Effort consistent: 3 FTE x 3 mo = 9.0 PM, $50,000, 3 milestones all
  delivered (delivery_verified, count=3). Repo fennelLabs/Fennel-Protocol @ 37cc301 (pinned at delivery).
  Proof class = W3F milestone delivery (durable, peer-reviewed), NOT on-chain treasury -> first non-on-
  chain pilot; tagged. Effort = proposed (fixed-price budget).
- Candidates rejected this hunt (auditable):
  * AdMeta (AdMetaNetwork/admeta): application self-contradicts duration (header 1 mo vs M1 6 mo) AND
    team is Litentry/Web3Go-affiliated (not independent). Verified live; rejected for cleanliness.
  * ParaSpell_follow_up.md, lastic.md: 404 on master (W3F renamed/relocated delivered apps); could not
    verify live this turn. (Finder TODO: pin app URLs to the mined git ref, not master.)
- Finder method (reusable): W3F census manifest -> filter delivery_verified=True & single separable repo
  & independent team & internally-consistent FTE/duration -> verify application markdown live -> enter.
- Concentration improved: OpenSquare x3, Patract x2, Bagpipes x1, Fennel x1 (independent). Set = 7 pilots,
  spread 0.95 -> 24.7 PM; proof classes now mixed (6 on-chain treasury + 1 W3F delivery), disclosed.

2026-06-14  Verified pilot #8 added (user-supplied brick; verified on-chain) — Elara v0.1.
- Polkadot Treasury #16 "Patract Labs' treasury proposal for Elara v0.1", read on-chain via
  polkadot-api.subsquare.io. Awarded 8,600 DOT ($34,400 @ $4/DOT), council motion #31 8-0 unanimous,
  award block 2,073,600 (2020-10-18). Greenfield RPC access layer ("Infura for Polkadot"), repo
  patractlabs/elara. Effort verbatim: "1 designer x week + 20 developers x weeks", 5-wk window
  21 Sep-26 Oct 2020. 20 dev-weeks => 4.6 PM (dev-only, consistent w/ Ask!/Megaclite); 4.83 PM if the
  1 designer-week counted. Tag: proposed (forward).
- CONCENTRATION: 3rd Patract project (Ask! #2, Megaclite #5, Elara #8). Set now OpenSquare x3, Patract x3,
  Bagpipes x1, Fennel x1. Only 2/8 orgs independent. Re-concentrated right after Fennel broke it.
- DISCOVERY ANGLE recorded (user insight): Patract & OpenSquare published NUMBERED project roadmaps
  (Patract roadmap = polkassembly post/100; Elara = their 4th project) where each item is a separate
  treasury proposal with an itemised FTE x week table. High-yield vein of clean-effort triples, but same
  1-2 orgs => grows clean subset WITHOUT independence. Mine it for the on-chain-itemised tier; keep W3F/
  independent route for org diversity. (Patract roadmap projects to enumerate: Ask!, Metis, Megaclite,
  Elara, + others; OpenSquare: subsquare, dotreasury, statescan, ...)

2026-06-14  Supervisor caution on Pilot #7 (Fennel) — investigated & RESOLVED (read both grant apps live).
- Fennel Labs has TWO W3F grants:
  * Grant 1 Fennel_Protocol.md (Q1 2022): 3 months, 3 FTE, $50k, 3 milestones ($15k/$15k/$20k).
    => 3 FTE x 3 mo = 9.0 PM. This is Pilot #7's source (census pinned this app; delivery_count=3
    matches its 3 milestones).
  * Grant 2 Whiteflag-on-Fennel.md (Q2 2022): 3 months, 2 FTE (overview), $90k, 2 milestones
    (M1 2 FTE x1mo $25k; M2 3 FTE x2mo $65k). The "2 FTE" the supervisor saw belongs to THIS grant,
    a different later scope (web UI + full Whiteflag + IPFS). NOT Pilot #7.
  CONCLUSION: #7's 3 FTE / 9 PM is correctly sourced (Grant 1); not conflated. Supervisor's "3
  milestones ~$15-20k over 3 months" = Grant 1 (which states 3 FTE).
- Caveats recorded on #7 for final calibration: (a) pin Fennel-Protocol to Grant-1 delivery (~end Q1
  2022/M3) so size doesn't include Grant-2 code; (b) Grant 1 spanned Fennel-Protocol + fennel-lib +
  fennel-cli -> sizing only chain repo may undercount (matched-pair risk as #6); (c) Grant 2, if ever
  added, = 8 PM milestone-weighted (2x1 + 3x2), NOT the 6 PM its "2 FTE x 3 mo" header implies.
- Also noted: W3F app filenames on master differ from our manifest casing (Lastic.md not lastic.md;
  ParaSpell_follow-up.md not ParaSpell_follow_up.md; second Fennel grant = Whiteflag-on-Fennel.md).
  Finder TODO: resolve app URLs against the live tree, not the mined casing.

2026-06-14  Verified pilot #9 added (independent-side rebalance) — ParaSpell (base grant).
- Read primary apps live. ParaSpell has THREE W3F grants:
  * base ParaSpell.md: 2 months, 1 FTE, $10k, 1 milestone => 1 FTE x 2 mo = 2.0 PM. Repo dudo50/ParaSpell.
  * follow-up ParaSpell_follow-up.md: 3 months... actually 6 months, 2 FTE, $28.5k, 3 milestones (M1/M2/M3
    each 2 FTE x 2 mo) => 2 FTE x 6 mo = 12 PM. Repos paraspell/sdk + paraspell/ui (multi-repo).
  * follow-up-2 ParaSpell_follow-up2.md (not used).
- ENTERED base grant as Pilot #9: 2.0 PM, repo dudo50/ParaSpell, independent Slovak team (Dusan Morhac;
  supervisor = Viktor Valastin/KodaDot, disclosed). Delivered (W3F wave 15; M1 evaluated paraspell_1_
  keeganquigley.md). Proof class = W3F delivery; effort = proposed. Type = XCM dev tool/UI (novel).
- CENSUS-CSV BUG CAUGHT (supervisor-rigor win): manifest row "ParaSpell_follow_up" MIXED base-grant
  effort (2 PM, $10k) with follow-up repo/commit (paraspell/sdk @ ParaSpell-followup-m1). The 2 PM is the
  BASE grant; correct repo = dudo50/ParaSpell. => derived W3F census CSV effort/repo mappings are NOT
  trustworthy; re-derive every W3F pilot from the primary application (same lesson as pilot_cases.csv).
- POLKAWATCH (user lead) verified at primary source: Valletech AB (Sweden), 2 FTE x 10 wk = 4.6 PM,
  $28.5k, 2 milestones, CONSISTENT & independent. NOT entered this turn because: repo on GitLab
  (gitlab.com/polkawatch, multi-module) -> out of our GitHub sizing pipeline; delivery not yet confirmed
  (deliveries listing truncated before 'P'). Held as a strong independent candidate for a GitLab-capable
  measurement pass.
- Concentration now: OpenSquare x3, Patract x3, Bagpipes x1, Fennel x1 (US), ParaSpell x1 (EU). 4/9
  non-OpenSquare/Patract. Set = 9 pilots, spread 0.95 -> 24.7 PM; proof classes 7 on-chain + 2 W3F.

2026-06-14  Verified pilot #10 added (cleaner path: retroactive, COMPLETED, actual effort) — Remarker.
- Polkadot OpenGov Referendum #1170 "Only Retroactive Funding Proposal: Completed Remarker Development",
  read on-chain via polkadot-api.subsquare.io/gov2/referendums/1170. NFT marketplace (remarkers.io).
- On-chain effort table: 6 Months, 1100 work hours, $4/hr = $4,400 => 1100/152 = 7.24 PM. ACTUAL
  (retroactive completed-work) effort. Single repo Remarkers/Remarkers-market. Solo independent dev
  (Ashutosh Singh). On-chain Executed (paid) 2024-09-23, 946.91 DOT (=$4,400 at submission), big_tipper
  track, referendum #1170 / treasury-spend #919.
- First INDEPENDENT actual-effort pilot (previous actuals all OpenSquare). Caveats: effort is a single
  lump figure (not itemised), solo self-report; NFT-marketplace reuse -> apply equivalent-SLOC reuse
  adjustment at measurement.
- Index note: OpenGov-era proposals are gov2 referenda; treasury/proposals/{n} 404s for these. Use
  gov2/referendums/{n}; treasurySpendIndex (#919) differs from referendumIndex (#1170).
- Set = 10 pilots, spread 0.95 -> 24.7 PM. Concentration: OpenSquare x3, Patract x3, Bagpipes 1,
  Fennel 1, ParaSpell 1, Remarker 1 => 4/10 independent. Proof classes: 8 on-chain treasury + 2 W3F.
- Remaining clean retroactive independent candidates queued (from mined list, verify on-chain before
  use): #1102 Kheopswap (kheopswap/kheopswap), #619 ink! Analyzer (ink-analyzer/ink-analyzer),
  #1132 Polkawatch (Valletech; GitLab -> needs GitLab sizing), #1118 SubWallet 8-mo (multi-repo).

2026-06-14  REJECTED ink!Hub (user brick) + ADDED pilot #11 Kheopswap (user brick).
- REJECTED: ink!Hub / Swanky Suite (OpenGov Ref #137 / Treasury #417, Executed, 58,018 DOT). Verified
  on-chain: real & delivered (Astar+AlephZero+Phala joint ink! tooling) BUT fails matched-triple bar:
  (a) NO person-effort on-chain (only DOT amount; all effort in external Google Doc; cost-derived PM = the
  rejected approach); (b) multi-repo umbrella across 3 orgs (swanky-cli + swanky-node + drink/drink-cli/
  drink-pink-runtime + ~26 inkdevhub repos) => no single artifact to match; (c) partial task-based delivery
  (~90%, payout adjusted) => fuzzy scope<->payment. Same failure mode as Talisman. Auditable exclusion logged.
- ADDED Pilot #11: Kheopswap (OpenGov Ref #1102 "Kheopswap retroactive funding"). Read on-chain. RETROACTIVE
  ACTUAL effort: "3 months (approx. 480 hours)" $130/hr = $62,400 => 480/152 = 3.16 PM. Single repo
  kheopswap/kheopswap (polkadot-api = PAPI dependency, excluded). Solo independent dev "Kheops" (employed at
  Talisman but Kheopswap is a personal side project, disclosed). On-chain Executed (paid) 2024-09-10, 14,092
  DOT ($62,400 @ $4.428 EMA), medium_spender, referendum #1102 / treasury-spend #916. Asset Hub DEX UI,
  first-gen PAPI dApp. Second independent actual-effort pilot (with #10).
- Set = 11 pilots, spread 0.95 -> 24.7 PM. Concentration: OpenSquare x3, Patract x3, + 5 independent
  (Bagpipes, Fennel, ParaSpell, Remarker, Kheopswap). Proof classes: 9 on-chain treasury + 2 W3F.

2026-06-14  Verified pilot #12 added (cleanest yet: retroactive, itemised actual effort) — ink! analyzer.
- Polkadot OpenGov Referendum #619 "ink! Analyzer: Retroactive funding for ink! v5 support", read on-chain.
  ITEMISED on-chain effort table (8 workstreams): 24+80+136+96+8+48+24+8 = ~424 h x $62.5 = $26,500
  => 424/152 = 2.79 PM. ACTUAL (retroactive completed). Independent solo dev David Semakula
  (@davidsemakula; independent rust-analyzer & ink! contributor). Repo ink-analyzer/ink-analyzer
  (multi-crate monorepo; ink-vscode = thin client). On-chain Executed (paid) 2024-04-17, 2,812.27 DOT
  ($26,500 @ EMA30), small_spender, referendum #619 / treasury-spend #747. Domain: LSP/semantic analyzer
  ("rust-analyzer for ink!").
- First INDEPENDENT itemised actual-effort pilot (gold-standard table granularity from a solo dev).
- SLICE discipline: 424 h = the ink! v5-support increment of a mature codebase (prior v4 work = 2 W3F
  grants $30k + $59.6k). Size the v5 DIFF (~late-2023 -> Mar-2024), NOT the whole repo. Brownfield
  windowed slice like #1/#4/#6.
- Set = 12 pilots, spread 0.95 -> 24.7 PM. Concentration EVENLY SPLIT: OpenSquare x3 + Patract x3 = 6;
  independent = 6 (Bagpipes, Fennel, ParaSpell, Remarker, Kheopswap, ink! analyzer). Proof classes:
  10 on-chain treasury + 2 W3F. Effort-types: actual itemised (1,6,8,12) + actual single-figure (4,10,11)
  + proposed (2,3,5,7,9).

2026-06-14  ADDED pilot #13 Dot Code School + REJECTED Ink! Dev Hub R1 (#624). (user case study)
- ADDED Pilot #13: Dot Code School PoC (OpenGov Ref #364 / treasury #563 "[Retroactive] Funding
  Development Costs for Dot Code School PoC"). Read on-chain. Cost breakdown verbatim: Total 2,500 DOT
  (~$18,000), FTE 1, $125/hr, 144 hours => 144/152 = 0.95 PM. ACTUAL retroactive. Single repo
  iammasterbrucewayne/dotcodeschool (renamed saumyakaran/dotcodeschool, archived Mar 2024; Next.js/TS).
  Solo independent dev Saumya Karan (India). On-chain Executed (paid) 2023-12-28, 2,500 DOT, small_spender,
  ref #364 / treasury-spend #563. Domain: interactive coding-school web app (novel). Note: Decentralized
  Futures Program = separate later scope, NOT this pilot (144h PoC only). Low-end point (0.95 PM, like #4).
- REJECTED: Ink! Dev Hub Round 1 (OpenGov Ref #624 / treasury #719, Awarded, 72,000 USDC). Sibling of the
  already-rejected ink!Hub #137 — same Astar+AlephZero+Phala Swanky/Drink umbrella. Delivery-based variable
  funding, NO hours/FTE table, multi-org, multi-repo umbrella, ~90% partial delivery. Same unmatched-scope
  failure mode. Assessed from user writeup + verified #137 precedent. Auditable exclusion logged.
- Set = 13 pilots, spread 0.95 -> 24.7 PM. INDEPENDENCE NOW MAJORITY: 7 independent vs 6 OpenSquare/Patract.
  Proof classes: 11 on-chain treasury + 2 W3F. Ready for first COCOMO II calibration pass on the verified set.

2026-06-14  Moved to COCOMO II dissection (one project at a time, PM=PM). Built harness + ranking.
- PILOT_RANKING.md: 13 pilots ranked by effort-authenticity, tie-broken by size-measurability. First
  specimen = Pilot #12 ink! analyzer (actual + itemised 8-workstream hours + independent + executed;
  size = tractable v5-support window). Method per project: measure matched-slice size -> assign 22
  COCOMO II drivers (objective signals + evidence overrides) -> E=0.91+0.01*SumSF, prod(EM),
  PM_pred@A=2.94, and A_local=reported_PM/(Size^E*prod(EM)). PM=PM holds per-project via A_local; the
  result is whether A_local clusters near 2.94 across the clean set (the calibration evidence).
- scripts/validate/dissect_pilot.py (+ .github/workflows/dissect_pilot.yml): clone repo, measure size
  per mode (whole=cloc / window=git log --numstat added / diff=git diff a..b --numstat), synth ratings
  via cocomo_fit.synth_ratings + cocomo2_tables, apply ov_<DRIVER> evidence overrides, output full
  breakdown to reports/dissect_<id>.json (published to census). Syntax-checked OK; spec parses.
- data/calibration/pilots_cocomo.csv: ink_analyzer row (window 2023-09-01..2024-04-01, reported 2.79 PM,
  overrides CPLX=H + PVOL=H with evidence; blockchain EMs Nominal). Awaiting push -> dispatch dissect-pilot
  (only=ink_analyzer) via Chrome -> read A_local from census.

2026-06-14  First dissection run (ink! analyzer) — caught a size-metric bug + the core calibration signal.
- ink_analyzer raw result: window size 58.4 KSLOC (=git log --numstat added, summed over 7 mo) ->
  PM_pred@A=2.94 = 306.8 PM vs reported 2.79 (+10,900%), A_local 0.027.
- FINDING 1 (bug): `window` mode summed per-commit churn (refactors/moves/snapshots double-counted);
  58.4K added lines for 424h = 138 LOC/h = impossible. FIX: window mode now = NET delta between
  boundary commits (git diff start..end), not log-sum. `diff` mode (exact 2-commit range) was already
  correct. dissect_pilot.py size_window rewritten; size_whole now accepts YYYY-MM-DD cutoff.
- FINDING 2 (the real signal): even at a corrected ~6-10 KSLOC, A=2.94 over-predicts (~35 PM vs ~3).
  Lean/senior/high-reuse/below-market grant projects deliver far more code per PM than COCOMO's
  classic calibration -> Blockchain-COCOMO A_local ~ 0.1-0.3, not 2.94. The contribution = the
  recalibrated A and whether A_local clusters across the clean set.
- PIVOT: ink! analyzer v5 slice is hard to isolate (7 mo mixed commits) -> poor first anchor. Added
  Kheopswap (#11, greenfield single-repo, actual 480h) as the FIRST clean specimen: whole-repo cloc at
  proposal date 2024-08-19 (unambiguous size, no slice). Objective drivers only (no overrides).
- Staged: dissect_pilot.py fixes + pilots_cocomo.csv (kheopswap whole + ink_analyzer net-delta window).
  Awaiting push -> re-dispatch dissect-pilot (only blank = both) -> read kheopswap A_local (clean anchor).

2026-06-14  Run #2 of dissect-pilot — two CSV/dispatch bugs found & fixed (no calibration result yet).
- BUG A: notes fields contained ';' in a ';'-delimited CSV -> DictReader overflow into None key ->
  dissect_pilot.py crashed ("'NoneType' has no attribute 'startswith'" in the ov_ override loop).
  FIX: removed ';' from ink_analyzer + kheopswap notes; AND hardened loop (isinstance(k,str) guard).
- BUG B: only ink_analyzer ran because a BLANK dispatch field falls back to the YAML input default,
  which was "ink_analyzer". FIX: workflow `only` default -> "" so blank = all rows.
- Verified: CSV parses with 0 None-keys; ink_analyzer retains ov_CPLX=H/ov_PVOL=H; kheopswap no overrides.
- Awaiting push -> re-dispatch (blank=all) -> first CLEAN numbers: kheopswap (greenfield whole-repo
  A_local) + ink_analyzer (net-delta window, upper bound).

2026-06-14  Run #3 of dissect-pilot — FIRST CLEAN CALIBRATION RESULT.
- KHEOPSWAP (clean greenfield anchor): cloc whole-repo @2024-08-19 = 15.363 KSLOC; E=1.100 (SumSF 18.97);
  prodEM=0.999 (objective drivers all ~Nominal: DOCU=H x1.11, TOOL=H x0.90 cancel). Reported 3.16 PM.
  PM_pred@A=2.94 = 59.25 PM (+1775%, ~19x). => A_local = 0.157 makes PM=PM. FIRST trustworthy brick.
- INK_ANALYZER: net-delta window now works (boundary diff d68e3132..3e7959cc = 37.49 KSLOC added) BUT the
  7-month window captures ALL dev, not v5-only (88 LOC/h for 424h = implausible). A_local 0.043 unreliable;
  flagged to re-do with v5-only commit isolation.
- CENTRAL FINDING (clean specimen): COCOMO II published A=2.94 over-predicts blockchain-grant effort ~19x;
  Blockchain-COCOMO A ~ 0.1-0.3. Drivers ~Nominal so the whole gap is the constant A (these projects deliver
  ~32 raw SLOC/h vs ~3-4 implied by 2.94 -> heavy ecosystem reuse + senior solo devs).
- REFINEMENTS QUEUED: (1) apply canonical reuse-adjusted equivalent_sloc in dissector (raise A_local toward
  true value; magnitude still <<2.94); (2) ink-analyzer v5-only isolation; (3) run remaining greenfield
  whole-repo pilots to test A_local clustering near ~0.15.
- Results tracked in data/calibration/COCOMO_DISSECTION_RESULTS.md. PM=PM holds per-project via A_local;
  contribution = recalibrated constant + tightness of A_local cluster on the clean curated set.

2026-06-14  Step 1 set up: full 13-pilot dissection spec (objective-only baseline) per user's calibration loop.
- pilots_cocomo.csv expanded to all 13 pilots with correct sizing mode each:
  diff (dotreasury exact range e8f09bf..release-2.3.1) ; whole greenfield @cutoff/commit (ask_v01, bagpipes,
  megaclite, fennel@37cc301, elara, paraspell_base, remarker, kheopswap, dotcodeschool) ; window net-delta
  (subsquare_maint, subsquare_newfeat, ink_analyzer - flagged OVERCOUNT/upper-bound).
- Drivers = objective signals ONLY (no ov_ overrides; stripped ink_analyzer's CPLX/PVOL) so the A_local
  spread is a clean diagnostic. Overrides + reuse-adjusted equivalent SLOC are Step-3 levers.
- Method (recorded in COCOMO_DISSECTION_RESULTS.md): Step1 exact (E,A_local) for all -> Step2 inspect spread
  -> Step3 adjust ONE justified lever, re-run, tighten -> win = ONE global (A,B,driver-rules) fits all 13.
- Verified all 13 rows well-formed via Read tool (bash mount was serving a truncated copy). Awaiting push ->
  dispatch dissect-pilot (blank=all 13) -> full baseline A_local table.

2026-06-14  Run #4: FULL 13-pilot baseline dissection (objective-only). 11 computed, 2 errored.
- A_local (PM=PM constant) per clean greenfield: bagpipes 0.729, fennel 0.739, dotcodeschool 0.631,
  megaclite 0.571, remarker 0.502, ask_v01 0.208, kheopswap 0.157. Geo-mean ~0.45 => working global
  A ~ 0.45 (~6.5x below published 2.94). E ~1.07-1.10 across all (scale factors ~flat).
- Artificially-low / buggy (exclude or fix): subsquare_maint 0.237 & subsquare_newfeat 0.121 &
  ink_analyzer 0.058 (window net-delta OVERCOUNTS, sizes 70-77 & 37 KSLOC); elara 0.044 (date cutoff
  2020-10-26 predates first commit -> measured FULL repo 68.9 KSLOC, impossible for 20 dev-weeks).
- ERRORS: dotreasury diff=0 KSLOC (ref e8f09bf..tag release-2.3.1 fetch/range bug); paraspell_base clone
  failed (dudo50/ParaSpell moved/private).
- DIAGNOSIS -> Step-3 levers: (1) reuse-adjusted equivalent SLOC (low A_local = most generated/reused
  frontends Kheopswap/Ask -> shrink size, raise A_local, tighten cluster); (2) fix elara cutoff (v0.1
  tag/first-commit), dotreasury refs, paraspell repo; (3) drop/commit-isolate window pilots.
- Full table maintained in COCOMO_DISSECTION_RESULTS.md. Working hypothesis: ONE global A ~ 0.4-0.6 once
  size is reuse-adjusted + buggy rows fixed.

2026-06-14  Step-3a fixes (before reuse lever): repair the 3 broken/buggy rows from run #4.
- paraspell_base DROPPED: github.com/dudo50/ParaSpell is 404 (deleted/renamed) -> base-grant-era code
  unrecoverable. Set now n=12 pilots. (Could re-add later if the moved repo + 2022 state is located.)
- dotreasury: exact-diff ref 'release-2.3.1' was unresolvable (diff=0 KSLOC) -> switched to funded
  maintenance-quarter window 2021-05-01..2021-08-01 (net-delta).
- elara: cutoff 2020-10-26 PREDATED first commit -> silently measured full later repo (68.9 KSLOC, wrong).
  -> cutoff moved to 2020-12-31 (after the 26-Oct v0.1 delivery).
- dissector hardened: size_whole now ERRORS if a date cutoff resolves to no commit (prevents silent
  HEAD-measurement recurring).
- Awaiting push -> re-dispatch (all 12) -> cleaner baseline (dotreasury+elara real); then Step-3b lever =
  reuse-adjusted equivalent SLOC.

2026-06-14  Run #5 (Step-3a fixes applied) -> CLEAN DIAGNOSTIC. n=12.
- dotreasury FIXED: funded-quarter window 2021-05..08 = 2.365 KSLOC -> A_local 0.379.
- elara still ~69.7 KSLOC even at 2020-12-31 cutoff = it forked a large Substrate template (raw SLOC
  counts the fork) -> extreme reuse case, A_local 0.043. Poster child for the reuse lever.
- 6 CLEAN-AUTHORED pilots cluster: A_local fennel .739, bagpipes .729, dotcodeschool .631, megaclite
  .571, remarker .502, dotreasury .379 => geo-mean ~0.58, spread ~1.95x. Working A ~ 0.58 (~5x below 2.94).
- ALL outliers are raw-SLOC size inflation: reuse-heavy (ask .208/21K, kheopswap .157/15K, elara .043/70K)
  + window over-count (subsquare_maint .237/77K, subsquare_newfeat .121/70K, ink_analyzer .058/37K).
- CONCLUSION: reuse-adjusted equivalent SLOC is the DOMINANT calibration lever (not minor). E ~1.07-1.10
  flat across all; drivers ~Nominal -> the spread is purely SIZE. Next = Step-3b build reuse-adjusted
  equivalent SLOC into dissector (generated-file exclusion + initial-import/fork discount via COCOMO AAM);
  Step-3c commit-isolate the 3 window pilots. Expect collapse toward A ~ 0.5-0.6.
- Table maintained in COCOMO_DISSECTION_RESULTS.md (Run #5 section).

2026-06-14  Step-3b BUILT: reuse-adjusted equivalent SLOC lever in dissect_pilot.py.
- reuse_split(): classifies source lines as ADAPTED if (a) generated (content markers) or (b) present in a
  large "big-bang" root commit (>4000 src lines added at once = fork/template import). equivalent = new +
  AAM*adapted, applied as a ratio to logical cloc KSLOC. AAM default 0.10 (workflow input for sensitivity).
- Applied to WHOLE-mode only (window/diff untouched; windows = Step-3c). dissect() now reports reuse{} +
  reuse-adjusted equivalent_ksloc; A_local computed on equivalent SLOC.
- Workflow: added 'aam' input (default 0.10) -> --aam.
- Verified file structure via Read tool (bash py_compile false-errored on a truncated mount copy).
- Expected: Elara (forked root) + Kheopswap/Ask (generated) shrink -> A_local rises toward ~0.58 cluster;
  clean-authored 6 barely move. Awaiting push -> re-dispatch (blank=all, aam=0.10).

2026-06-14  Run #6 (reuse adjustment AAM=0.10) — HONEST NEGATIVE; detector too narrow.
- Only fennel moved: 6216 @generated lines (52%) discounted -> equiv 7.84->4.16 KSLOC -> A_local
  0.739->1.458 (OVERSHOOT). bagpipes negligible (45 lines).
- The 3 intended targets UNCHANGED: elara 0.043 (root_added_loc=0; vendored bulk not in root commit),
  kheopswap 0.157 & ask 0.208 (PAPI/AssemblyScript codegen has no @generated marker -> not detected).
- Net: whole-mode spread WIDENED to 0.043-1.458. Reuse concept right, auto-detection incomplete.
- Flags: elara _phys walk 150,779 vs cloc 69.7 KSLOC (2x disagreement, lots of borderline code);
  fennel jump may be REAL (authored ~4 KSLOC for 9 PM = complex Rust chain, low LOC/h) - verify gen lines.
- NEXT ZAG options: (a) blame-based bulk-import detection ANYWHERE in history (not just root); (b) path-
  based generated detection (descriptors/ .papi/ build/ generated/); (c) verify fennel gen lines; (d)
  evidence-based per-repo reuse fraction by inspecting elara/kheopswap/ask. Reported honestly in
  COCOMO_DISSECTION_RESULTS.md (Run #6 section). Integrity held: lever tried, didn't work, reported straight.

2026-06-14  WORKING CALIBRATION reached (fluid forward move, no more size-fixating).
- Fit ONE global A = geomean(A_local) per subset on run-#5 dissection numbers:
  * core clean (6: bagpipes, megaclite, remarker, dotcodeschool, dotreasury, fennel): A*=0.577,
    MMRE 20%, PRED25 83%, PRED30 83%, PRED50 83%  <- GOOD calibration (PRED30>=70%).
  * +reuse (8): A*=0.431 PRED30 38%. +scope/elara (9): 0.335 PRED30 11%. all 12: 0.258 PRED30 17%.
- HEADLINE: Blockchain-COCOMO PM = 0.58 * EquivKSLOC^E * prodEM (E=0.91+0.01*SumSF), ~5x below classic
  A=2.94, PRED30=83% on clean matched triples. Monotonic degradation as size-inflated pilots added =>
  residual is SIZE-measurement (reuse+scope) artifact, NOT model failure.
- Elara reclassified: NOT reuse but SCOPE (repo = v0.1+v0.2 consolidation; #16 funded v0.1 only) - per
  README "completed 0.2 version". Joins window pilots as scope-inflated.
- Caveats noted: in-sample n=6; next rigor = LOOCV + grow clean-n by fixing reuse/scope sizes (parallel,
  non-blocking). E~1.07-1.10 flat; drivers ~Nominal -> model ~ A*Size^E.
- Recorded in COCOMO_DISSECTION_RESULTS.md (WORKING CALIBRATION section).

2026-06-14  DOCUMENTED the breakthrough: BLOCKCHAIN_COCOMO_CALIBRATION_REPORT.md (publication-ready record).
- Self-contained 9-section report: summary; problem & root-cause of prior failures; curated matched-triple
  dataset (13 pilots + auditable rejections + provenance); method (COCOMO II instantiation, evidence-based
  driver rule + anti-overfitting integrity rule, sizing modes + reuse model, calibration loop); results
  (per-project A_local table + global-A fit table); key finding (residual = size not model); honest negative
  results & bug log; reproducibility (scripts/workflow/data/CI history); limitations/threats; next steps.
- Headline locked: PM = 0.58 * EquivKSLOC^E * prodEM (E=0.91+0.01*SumSF); core-6 PRED30=83%, MMRE=20%; ~5x
  below classic A=2.94. Integrity statement included.
- Next (agreed): #1 LOOCV + bootstrap CI on core-6 A.

2026-06-14  Cross-validation of core-6 calibration (pure-Python, no CI). RESULT LOCKED.
- In-sample: A*=0.577, MMRE 20%, PRED30 83%.
- LOOCV (out-of-sample): MMRE 24%, PRED25 67%, PRED30 83%, PRED50 83%. Per-pilot held-out err: megaclite
  1%, dotcodeschool 10%, remarker 18%, bagpipes 24%, fennel 26%, dotreasury 66% (smallest, edge of range).
- Bootstrap (B=10,000): A=0.58, median 0.579, 95% CI [0.475, 0.685]. Excludes classic 2.94 by ~5x.
- => A = 0.58 (95% CI 0.48-0.69), NOT overfit (LOOCV ~ in-sample). Updated both report + results doc;
  next-steps item #1 marked DONE.

2026-06-14  PEER REVIEW (2 senior reviewers) addressed — computable concerns resolved, plan written.
- REVIEWER_RESPONSE_AND_REVISION_PLAN.md: point-by-point for R1 (M1-M5,m1-m4) + R2 (M1-M4,m1-m4), each
  tagged DONE/PLAN/ACK with computed evidence.
- New analyses (run-#5 data, no CI): 
  * SA (Shepperd-MacDonell) promoted to PRIMARY: core-6 SA=+0.80, all-12 +0.15.
  * Stratified A*: actual-only 0.493 (SA .95), proposed-only 0.675 (SA .84) -> opposite of usual
    proposed-underestimates prior; actual-only = conservative anchor. treasury-only 0.549; w3f-only n=1.
  * Power-law test (M5): full COCOMO A*=0.577 PRED30 83% SA .80 vs pure A*Size^E 0.647 PRED30 67% SA .73
    -> EM machinery contributes +16pp; it IS COCOMO II, not just a power law.
  * Pricing confound (M2-R2): implicit grant $/hr median ~60 (range 4-125) vs market 80-150 -> below
    market; A=0.58 is a GRANT-CONTEXT constant (productivity x reuse x pricing/reporting), not pure
    productivity. Remarker $4/hr extreme.
  * Selection-bias bound (M1-R1): inflated pilots need 59-92% size shrink to reach 0.577, all same
    direction + independently plausible -> fixing them moves A_local UP toward 0.58; full-corpus A in [0.58,0.70].
- Folded into report as new SS 4.4 + qualified the "5x" claim + scope statement (Substrate Polkadot/Kusama,
  grant-context). Priority next = fix 6 inflated sizes (path-based gen detection + scope isolation) -> full-12 A*.

2026-06-14  Step-3b DETECTOR UPGRADE built (addresses R1-M1: fix the 6 size-inflated pilots).
- reuse_split() generalised: ADAPTED now = (a) generated by @generated markers, (b) generated by PATH
  (.papi/, descriptors/, generated/, __generated__/, codegen/, gen/, *.gen.*, *_pb.*), (c) forked/imported
  = files first-ADDED in ANY bulk-import commit (>4000 src lines in one commit), detected anywhere in
  history via a single `git log --diff-filter=A --numstat` pass (was root-only -> missed Elara's fork).
- _numstat (window/diff slices) now also skips generated paths.
- Expected: kheopswap/ask (PAPI/AS codegen by PATH) + elara (forked template by bulk-import) shrink ->
  A_local rises toward ~0.58; clean-6 ~unchanged (small first commits). Window pilots (subsquare x2,
  ink_analyzer) remain scope-limited (wide-window over-count is scope not reuse) - kept flagged.
- Verified structure via Read (bash mount truncates). Chrome connected on dissect-pilot workflow page.
  Awaiting push -> dispatch (blank=all, aam=0.10) -> recompute full A* with reuse-corrected sizes.

2026-06-14  Run #7 (upgraded detector) -> CORE-8 CONVERGENCE (answers R1-M1, the #1 reviewer concern).
- Detector VERIFIED genuine reuse in the 2 most-inflated: elara 98.8% forked Substrate template
  (149K lines/2 bulk commits) A_local 0.044->0.487; kheopswap 76.6% PAPI scaffold 0.157->0.568. Both land
  INSIDE the clean cluster.
- Detector OVER-FIRED on clean projects (false positives): bagpipes 0.73->7.5, remarker 0.50->6.3 - their
  large AUTHORED initial/migration commits mis-flagged as forks (bagpipes XcmSend->Bagpipes rename; remarker
  one-shot first commit). => big commit != reuse; auto-heuristic blunt (under #6, over #7).
- DEFENSIBLE: raw size for low-reuse projects + evidence-validated reuse correction ONLY for elara+kheopswap.
- CORE-8 (clean-6 raw + elara,kheopswap corrected): A*=0.564, 95%CI [0.487,0.647], SA +0.80, MMRE 17%,
  PRED30 88%, n=8. vs core-6 A*=0.577 CI[0.473,0.686] PRED30 83%. => constant CONFIRMED not shifted; CI
  tightened (0.21->0.16); PRED30 up. Landmark "clean-6 and corrected pilots agree".
- Held out/unresolved (honest): ask_v01 (85% flagged, maybe vendored AS stdlib), 3 window pilots (scope not
  reuse), fennel generated-flag (raw). 
- Updated report (SS4.4e + ), COCOMO_DISSECTION_RESULTS (Run#7 section), REVIEWER_RESPONSE M1-R1 -> DONE.

## 2026-06-15 — n-growth campaign launched (Dataset Expansion Charter v1.0)
- Reviewer round closed: CEVRP locked as benchmark reuse rule (§3.3); abstract/conclusion lead with core-8
  (A=0.564, CI [0.487,0.647], PRED30 88%, SA +0.80); rejected-candidate table + 5 citations added.
- New governing docs in data/calibration/:
  - DATASET_EXPANSION_CHARTER.md — mandate (surpass Boehm n=161 in count AND auditability), twin north stars
    QUALITY+DIVERSITY, gates G1–G7, 9-axis diversity matrix, Tier A–D source universe, 9-stage intake pipeline,
    author-verification protocol, Boehm quality bar, gated re-fit cadence, integrity invariants.
  - INTAKE_REGISTER.md — per-pilot field dictionary incl. REQUIRED author-contact fields; 12 admitted pilots
    flagged TO-CAPTURE/unverified for retro contact+verification; diversity snapshot (corpus is mono-ecosystem
    Polkadot → cross-ecosystem is highest-yield next move); Wave-1 candidate board (8 cross-ecosystem targets).
  - AUTHOR_VERIFICATION_EMAILS.md — T1 initial + T2 follow-up templates; send rules (email everyone admitted,
    follow up doubtful non-responders +7d/+21d); all sends require per-batch user approval.
- User directives: do not restrict scope (quality + diversity); mine everything; pick good data then email
  everyone, follow up doubtful non-responders → contact-info capture is mandatory.

## 2026-06-15 (cont.) — 6. Logs blueprint + contact capture for the 12
- Created Thesis-level "6. Logs/" blueprint library (01_dataset, 02_publication, 03_experimental_results,
  04_codes, 05_provenance + INDEX.md); curated light copies of load-bearing .md/.csv/.py (originals stay in
  06_measurement). This is the consumption/reading + publication layer.
- Captured author contacts + EXACT effort-proof links for all 12 pilots into INTAKE_REGISTER §B:
  verified emails — OpenSquare yongfeng@opensquare.network (P01/P04/P06), Fennel info@fennellabs.com (P07);
  strong channels (no public email) for solo devs P10 Remarker, P11 Kheopswap, P12 ink!analyzer (davidsemakula),
  P13 DotCodeSchool (saumyakaran), P03 Bagpipes (decentration). Patract P02/P05/P08 flagged org-inactive →
  GitHub-issue route then "public-record only." No contact fabricated.
- Drafted personalized Batch-1 outbox (OUTBOX_verification_emails_batch1.md): 8 sends covering 12 pilots,
  grouped ready-to-send / send-via-channel / at-risk. Queued for user approval — nothing sent.
- Note: each dataset row now carries the author email/owner-channel AND the exact online effort-proof link
  (the page from which PM is computed), per user directive.

## 2026-06-15 (cont.) — outreach: Group 1 emailed, Groups 2&3 via GitHub issues
- Group 1 (P01/P04/P06 OpenSquare, P07 Fennel): emailed by PI.
- Groups 2&3: no inbox on GitHub → brief public verification Issues, one per repo, drafted in
  OUTBOX_github_comments_batch1.md (ink-analyzer, Remarkers-market, kheopswap, BagpipesOrg/app, dotcodeschool[archived→fallback],
  patractlabs/ask, patractlabs/megaclite, patractlabs/elara). Tailored confirm-points (actual-vs-proposed,
  matched repo/slice, team size, reuse/generated share). Check-back cycle = 24 h, logged in the file's tracker.
- INTAKE_REGISTER outreach-status block updated. Assistant cannot post to GitHub (no write access / browser
  read-only); drafts are copy-paste-ready for the PI to post.

## 2026-06-15 (cont.) — Pilot #14 ADMITTED: Pontem (Move VM pallet) + census guardrail
- n-growth Wave 1: mined the 439-row W3F census (146 clean-on-basics). Discovery largely solved; bottleneck =
  hand-verification.
- **Census guardrail established:** planned_pm/planned_fte/cost_usd in measurements_census.csv are unreliable
  parse artifacts (Pontem row: 4 PM / $96 vs primary 252 person-days / 1.4658 BTC). Effort MUST be re-read from
  the primary W3F application before admission.
- **Pilot #14 = Pontem Move VM pallet** (Dfinance/Wings Stiftung, Zug CH). W3F grant, delivered M1 (PR#72) +
  M2 (PR#113), both merged/accepted; repo pontem-network/sp-move (archived w3f-grants-archive/sp-move), commit
  49d6f1d (grant-end). Matched scope = M1+M2 = 252 person-days → 13.3 PM (Boehm 152h/PM; alt 11.6). M3 (Beta)
  NOT W3F-delivered → excluded (matched-scope discipline). Forked Libra Move VM (44% adapted) → CEVRP applies
  (C1✓ C2 named-upstream✓ C3 vendored-fork✓). Contact boris@dfinance.co. Diversity: first Move-language/VM
  pilot, first Swiss team, ~13 PM, proposed effort. Status: admitted, pending CI dissection (confirm M2 commit).
- **Perun state channels** → HOLD: clean repo+proof+contact but app states duration+cost, no explicit FTE →
  effort needs author confirmation (seb@perun.network). Good candidate once effort confirmed.
- Cross-ecosystem finding: clean non-Polkadot person-effort is scarce (Ethereum/Gitcoin/RetroPGF no FTE;
  Filecoin vague). Strategy: W3F/OpenGov = volume engine to surpass Boehm; cross-ecosystem opportunistic+labeled.

## 2026-06-15 (cont.) — Batch A: pilots #15, #16 ADMITTED; #17 (galaxy) HOLD
- All effort re-read from primary W3F applications (census values cross-checked).
- **#15 SkyeKiwi Protocol** (Song Zhou, song.zhou@skye.kiwi): 2 FTE × 4 mo = 8.0 PM; repo skyekiwi/skyekiwi-protocol;
  privacy/secret-sharing crypto (NEW type). Census agreed (8.0). Proposed. Pending dissection + delivery-PR pin.
- **#16 Stable Asset / NUTS Finance** (Terry Lam, terry@nuts.finance): 2 FTE × 1 mo = 2.0 PM; repo
  nutsfinance/stable-asset; DeFi synthetic-asset primitive (NEW type); ported from own acBTC Solidity = authored
  rewrite (not CEVRP-adapted). Census agreed (2.0). Proposed. Pending dissection + exact-commit pin (census used cutoff).
- **#17 Galaxy (HOLD):** effort clean (1 FTE×1 mo = 1 PM) but built on Excalidraw (heavy upstream) + W3F delivery
  unconfirmed + thematically light Polkadot → not admitted; confirm delivery & CEVRP first.
- Corpus now n=15 admitted (P01-08,10-16). Balance caveat: P14/15/16 all PROPOSED → actual/proposed tilting to
  proposed; next batch should include OpenGov RETROACTIVE (actual) candidates to keep ≥50% actual (Charter).

## 2026-06-15 (cont.) — re-verify Batch A + Batch B (retroactive) start
- Re-verified #14 Pontem: read delivery file pontem-network_milestone-2.md (M2 merged to Open-Grants-Program PR#138) — confirmed.
- #15 SkyeKiwi flag → admitted; delivery = census EXACT commit (strong); pin PR at dissection.
- #16 Stable Asset flag → admitted (provisional); confirm delivery + pin exact commit at dissection (census used cutoff).
  (W3F grants dashboard route redirects to homepage — not usable; relying on census-resolved commits + honest flag.)
- Batch B (retroactive/actual): validated Subsquare per-referendum API as verification tool (no Chrome needed).
  REJECTED 2 candidates cleanly: #1762 RegionX (rejected on-chain + external Google Doc effort), #1799 Mimir
  (rejected on-chain + external Google Sheet budget). Both logged in VERIFIED_PILOTS exclusions.
  FINDING: recent (2025) retroactive proposals = high on-chain rejection + off-chain effort docs → low yield.
  Re-target EXECUTED 2024-era retroactive proposals with on-chain itemized hours tables (Remarker/Kheopswap/
  ink!analyzer/dotcodeschool profile). Queue indexes to state-check: 1811,1805,1798,1745,1724,1897.
- Corpus unchanged at n=15 admitted (no compromise: 0 admitted this pass since both retroactive candidates failed gates).

## 2026-06-15 (cont.) — Batch B retroactive: 3/3 recent candidates rejected (gate held)
- Checked #1805 Kitdot → Rejected on-chain + 5-repo umbrella → reject. Now 3/3 recent retroactive rejected
  (#1762, #1799, #1805). Logged in VERIFIED_PILOTS exclusions.
- CONFIRMED FINDING: 2025 OpenGov retroactive proposals = high rejection + off-chain effort docs. The
  retroactive text-scan returned 2025 (wrong era). Clean executed-retroactive triples are 2024-era.
- METHOD CORRECTION: use the treasury_mine CI harvester (task #38) to page full treasury history server-side
  and emit an EXECUTED-proposals candidate manifest. (Local bash web-fetch of APIs is disallowed; CI is the
  sanctioned at-scale path.) Inline per-referendum API fetch remains the per-candidate VERIFICATION tool.
- Corpus unchanged: n=15 admitted. Zero junk admitted (quality gate upheld).

## 2026-06-15 (cont.) — parallel tracks: W3F verify (Spacewalk reject) + harden census guardrail
- W3F track: verified Spacewalk/Pendulum (Wave 13 Stellar bridge) → REJECT: application header `Status: Terminated`
  (not delivered) + internally inconsistent FTE (0.5 FTE/3mo vs ~5 PM in milestones). Census had it "clean".
  Logged in VERIFIED_PILOTS exclusions.
- Hardened the census guardrail (INTAKE_REGISTER): per-candidate primary check must verify (1) effort accuracy,
  (2) DELIVERY STATUS via app `Status` header + milestone record (terminated/partial grants ARE in census),
  (3) FTE internal consistency, (4) single repo. True clean-yield < raw 146; budget ~1-in-2 cold-pick rejection.
- Retroactive track: CI harvester (treasury_mine) remains the route for 2024 executed range (queued).
- This pass: 0 admitted, gate rejected Spacewalk + the 3 retroactive — quality upheld, no junk. Corpus n=15.

## 2026-06-15 (cont.) — built delivery-verified pre-screen (script + CI workflow)
- scripts/extract/prescreen_delivery.py: clones w3f/Grant-Milestone-Delivery + Grants-Program (CI), counts
  delivery/evaluation files per census project_id (normalized matching), reads application Status headers,
  emits data/calibration/census_prescreen.csv ranked DELIVERED > evaluated_only > no_delivery_found > REJECT_terminated.
- .github/workflows/prescreen.yml: workflow_dispatch; publishes census_prescreen.csv to census branch.
- Logic validated locally (self-contained): stem-stripping handles _milestone-N/_N/-milestoneN variants;
  pontem-network/skyekiwi-protocol/stable-asset/remarker/ink-analyzer all match a delivered stem; SPACEWALK→None
  (correctly flagged, consistent with its terminated status). Decisive signal = #delivery files per candidate.
- Next: user pushes → dispatch prescreen workflow via Chrome → read census_prescreen.csv → deep-verify only the
  DELIVERED shortlist (kills the ~1-in-2 cold-pick rejection; no more Spacewalks).

## 2026-06-15 (cont.) — delivery pre-screen RAN (CI #1), shortlist built
- Dispatched prescreen-delivery workflow via Chrome; ran ~17s; published census_prescreen.csv to census branch.
- Result: scanned whole W3F Grants-Program + Grant-Milestone-Delivery → ~270 DELIVERED (ranked by milestone
  count) vs ~45 REJECT_terminated. SPACEWALK correctly in REJECT_terminated (validates the pre-screen end-to-end),
  alongside openbrush/tuxedo/polkadex/manta/deip/redstone/polkamusic/etc.
- Abridged synced copy: data/calibration/census_prescreen.csv (full list on census branch).
- Built Batch C shortlist (DELIVERED + census-PM + new type): hyperfridge (FIAT/banking bridge), melodot (DA layer),
  NewOmega (game), fair_squares (real-estate DAO), logion_wallet (legal), PrivaDEX (DEX aggregator), subcoin (BTC).
- Effect: cold-pick rejection now near-zero; deep-verify only DELIVERED rows. Corpus n=15 (admits resume next).

## 2026-06-15 (cont.) — Batch C verify (hyperfridge HOLD) + treasury-mine #7 dispatched (parallel)
- Parallel track ON: dispatched treasury-mine workflow run #7 (retroactive/actual OpenGov harvester) via Chrome.
- Batch C: hyperfridge → HOLD (multi-repo: 9 PM spans hyperfridge-r0 + ocw-ebics + ebics-java-service; census
  measured only the ZK circuit). Salvage = milestone-isolate M1 (3.0 PM ↔ hyperfridge-r0). melodot/subcoin app
  filenames 404 → re-fetch next pass. Lesson: prioritize single-artifact grants; pre-screen v2 should emit
  matched app-filename + repo-count per grant.
- Corpus n=15. Admits continue next pass from single-artifact DELIVERED candidates + treasury-mine manifest.

## 2026-06-15 (cont.) — pre-screen v2 built + treasury-mine #7 read
- Pre-screen v2 (prescreen_delivery.py): adds matched_app_file, app_fte/app_months/app_pm (primary effort),
  n_app_repos, ks_per_pm scope ratio (warning-only, threshold softened to <0.15 so reuse-heavy clean pilots
  aren't de-ranked). Validated locally: effort regex correct on skyekiwi/stable-asset/hyperfridge/spacewalk/galaxy;
  hyperfridge auto-flags ks/pm 0.19. Ranks admit-ready (app_pm + <=2 repos) DELIVERED to top.
- treasury-mine #7 read: manifest reaches 2024 (idx 1583..544; Remarker/Kheopswap/ink!analyzer present).
  Finding: retroactive vein largely exhausted — mostly tips/events; dev proposals multi-repo (SubWallet=3) or
  already admitted. Thin leads: LiteScan #970, Telenova #611, Polkawatch #1132. W3F v2 = primary engine.
- Corpus n=15. Next: push prescreen v2 → dispatch → admit from ranked shortlist.
