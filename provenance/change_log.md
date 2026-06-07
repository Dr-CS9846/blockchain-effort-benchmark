# Change Log — append-only audit trail

Newest first. Each entry records what changed and why, for reproducibility and review.

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
