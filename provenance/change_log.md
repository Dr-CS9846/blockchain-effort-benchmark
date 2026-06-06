# Change Log — append-only audit trail

Newest first. Each entry records what changed and why, for reproducibility and review.

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
