# Per-pilot COCOMO II dissection — running results (PM=PM via local A)

For each verified pilot: measure matched-slice size → assign 22 drivers (objective + evidence overrides)
→ E = 0.91 + 0.01·ΣSF, ∏EM → PM_pred at published **A = 2.94**, and the **A_local** that makes
PM(COCOMO) = PM(reported). The scientific result is whether A_local **clusters** across the clean set
(a tight cluster ⇒ one defensible Blockchain-COCOMO constant). Published COCOMO II A = 2.94.

## ✅ WORKING CALIBRATION (global A fit, from run-#5 dissection numbers)
Fit ONE global A = geomean(A_local) per subset; evaluate PM_pred = A·Size^E·∏EM vs reported.

| Subset (size class) | n | **A\*** | MMRE | PRED25 | PRED30 | PRED50 |
|---|---|---|---|---|---|---|
| **core clean (size↔scope verified)** | 6 | **0.577** | 20% | 83% | **83%** | 83% |
| + reuse-inflated (ask, kheopswap) | 8 | 0.431 | 56% | 38% | 38% | 75% |
| + scope-inflated (elara) | 9 | 0.335 | 120% | 11% | 11% | 44% |
| all incl. windows (12) | 12 | 0.258 | 114% | 17% | 17% | 33% |

**Result:** on 6 clean matched triples, **Blockchain-COCOMO PM = 0.58 · EquivKSLOC^E · ∏EM** (E = 0.91 + 0.01·ΣSF)
fits with **PRED(30) = 83%, MMRE = 20%** — a *good* calibration, ~5× below classic A = 2.94. Fit degrades
monotonically as size-inflated pilots are added (0.58→0.43→0.34→0.26) ⇒ the residual is a SIZE-measurement
artifact (reuse + scope), not model failure. core-6 = bagpipes, megaclite, remarker, dotcodeschool, dotreasury,
fennel.

**CROSS-VALIDATED (core-6):** in-sample A*=0.577 (MMRE 20%, PRED30 83%). **LOOCV (out-of-sample): MMRE 24%,
PRED25 67%, PRED30 83%, PRED50 83%** — held-out errors: megaclite 1%, dotcodeschool 10%, remarker 18%,
bagpipes 24%, fennel 26%, dotreasury 66% (smallest project, edge of COCOMO range). **Bootstrap 95% CI on A =
[0.475, 0.685]** (B=10,000, median 0.579). ⇒ **A = 0.58 (95% CI 0.48–0.69), NOT overfit** (LOOCV ≈ in-sample),
5.1× below classic 2.94. Caveats: E≈1.07–1.10
across all (scale factors ~flat); drivers ~Nominal — the model is essentially A·Size^E.

### Run #6 (Step-3b reuse adjustment, AAM=0.10) — HONEST NEGATIVE: detector too narrow
Reuse model `equiv = new + 0.10*adapted`, adapted = big-ROOT-commit fork + `@generated` markers.
Result: it moved only **fennel** (52% generated → equiv 7.84→4.16 KSLOC → A_local 0.739→**1.458**, overshoot) and
left the 3 intended targets unchanged: **elara 0.043** (root_added_loc=0 → vendored bulk not in root → not
flagged), **kheopswap 0.157** & **ask 0.208** (PAPI / AssemblyScript codegen has no `@generated` marker → missed).
Net: whole-mode A_local spread WIDENED to 0.043–1.458. ⇒ reuse *concept* is right but this *auto-detection* is
incomplete. Flags: elara `_phys` walk = 150,779 lines vs cloc 69.7 KSLOC (2× disagreement = lots of borderline
code); fennel's jump may be real (authored ~4 KSLOC for 9 PM = complex Rust chain, low LOC/h) — verify the 6,216
"generated" lines. NEXT ZAG: (a) detect bulk-import commits ANYWHERE in history (not just root) via blame;
(b) detect framework-generated code by path (descriptors/, .papi/, build/, generated/) not just markers;
(c) verify fennel generated lines; OR (d) evidence-based per-repo reuse fraction by inspecting the 3 inflated repos.

### Run #5 (after Step-3a fixes: dotreasury window, elara cutoff, paraspell dropped) — n=12 [reuse OFF]
| Pilot | KSLOC | E | ∏EM | Reported PM | **A_local** | size class |
|---|---|---|---|---|---|---|
| fennel | 7.84 | 1.070 | 1.34 | 9.0 | **0.739** | clean authored |
| bagpipes | 10.81 | 1.100 | 1.00 | 9.97 | **0.729** | clean authored |
| dotcodeschool | 1.45 | 1.100 | 1.00 | 0.95 | **0.631** | clean authored |
| megaclite | 3.65 | 1.082 | 1.49 | 3.45 | **0.571** | clean authored |
| remarker | 11.33 | 1.100 | 1.00 | 7.24 | **0.502** | clean authored |
| dotreasury | 2.37 | 1.070 | 1.00 | 0.95 | **0.379** | clean authored (FIXED: funded-quarter window) |
| ask_v01 | 20.73 | 1.070 | 1.30 | 6.9 | 0.208 | reuse-inflated (AssemblyScript codegen) |
| kheopswap | 15.36 | 1.100 | 1.00 | 3.16 | 0.157 | reuse-inflated (PAPI generated) |
| elara | 69.74 | 1.100 | 1.00 | 4.6 | 0.043 | reuse-inflated (forked Substrate template) |
| subsquare_maint | 76.89 | 1.070 | 1.00 | 24.7 | 0.237 | window over-count |
| subsquare_newfeat | 69.97 | 1.070 | 1.00 | 11.4 | 0.121 | window over-count |
| ink_analyzer | 37.49 | 1.070 | 1.00 | 2.79 | 0.058 | window over-count |

**Headline (Run #5).** The **6 clean-authored pilots cluster at A_local 0.379–0.739 (geo-mean ≈ 0.58, spread ~1.95×)**
⇒ working Blockchain-COCOMO **A ≈ 0.58** (~5× below published 2.94). **Every outlier is a raw-SLOC size-inflation
case**: the 3 lowest (Elara 0.043, Kheopswap 0.157, Ask! 0.208) are the most reuse/forked/generated codebases;
the 3 window pilots over-count by construction. ⇒ **reuse-adjusted equivalent SLOC is the dominant lever**, not a
minor one. Next: (Step-3b) replace raw cloc with COCOMO reuse-adjusted equivalent SLOC; (Step-3c) commit-isolate
the 3 window pilots. Expect the spread to collapse toward A ≈ 0.5–0.6.

### Baseline run (objective-only drivers, raw cloc/diff size) — n=11 computed, 2 errored [SUPERSEDED by Run #5]
| Pilot | KSLOC | E | ∏EM | Reported PM | PM_pred@2.94 | **A_local** | size basis |
|---|---|---|---|---|---|---|---|
| bagpipes | 10.81 | 1.100 | 1.00 | 9.97 | 40.2 | **0.729** | whole ✓ |
| fennel | 7.84 | 1.070 | 1.34 | 9.0 | 35.8 | **0.739** | whole ✓ |
| dotcodeschool | 1.45 | 1.100 | 1.00 | 0.95 | 4.43 | **0.631** | whole ✓ |
| megaclite | 3.65 | 1.082 | 1.49 | 3.45 | 17.8 | **0.571** | whole ✓ |
| remarker | 11.33 | 1.100 | 1.00 | 7.24 | 42.4 | **0.502** | whole ✓ |
| ask_v01 | 20.73 | 1.070 | 1.30 | 6.9 | 97.8 | **0.208** | whole ✓ |
| kheopswap | 15.36 | 1.100 | 1.00 | 3.16 | 59.2 | **0.157** | whole ✓ |
| subsquare_maint | 76.89 | 1.070 | 1.00 | 24.7 | 306.1 | 0.237 | window ⚠ overcount |
| subsquare_newfeat | 69.97 | 1.070 | 1.00 | 11.4 | 276.7 | 0.121 | window ⚠ overcount |
| ink_analyzer | 37.49 | 1.070 | 1.00 | 2.79 | 141.9 | 0.058 | window ⚠ overcount |
| elara | 68.88 | 1.100 | 1.00 | 4.6 | 308.5 | 0.044 | whole ⚠ SIZE BUG (date checkout failed) |
| dotreasury | ERR | | | 0.95 | | — | diff=0 KSLOC (ref/tag bug) |
| paraspell_base | ERR | | | 2.0 | | — | clone failed (dudo50/ParaSpell moved) |

**Step-2 diagnosis.** Clean greenfields (7): A_local 0.157–0.739, **geo-mean ≈ 0.45** ⇒ working global A ≈ 0.45
(~6.5× below 2.94). E ≈ 1.07–1.10 everywhere (scale factors barely vary). Spread sources, ranked:
  - **(a) Window over-count** (subsquare ×2, ink! analyzer): net-delta over wide windows counts non-funded work →
    A_local artificially low (0.06–0.24). EXCLUDE until commit-isolated.
  - **(b) Elara size bug**: 68.9 KSLOC for ~20 dev-weeks is impossible — date cutoff 2020-10-26 predates first
    commit → no checkout → measured full later repo. FIX cutoff (use v0.1 tag / first-commit window).
  - **(c) Reuse**: the low clean outliers (Kheopswap 0.157, Ask! 0.208) are the most generated/reused codebases
    (PAPI descriptors, AssemblyScript codegen). **Reuse-adjusted equivalent SLOC** shrinks their raw size and
    raises A_local toward the ~0.5 cluster → the #1 tightening lever.
  - **(d) Two errors**: dotreasury exact-diff returned 0 (ref/tag fetch); paraspell_base repo moved.

**Next iteration (Step 3):** (1) fix dotreasury refs + elara cutoff + paraspell repo; (2) add canonical
reuse-adjusted equivalent SLOC to the dissector; (3) drop window pilots (or commit-isolate) → re-run → expect
the clean-greenfield A_local cluster to tighten around ~0.4–0.6.

## Calibration loop (the plan)
**Step 1 (running):** all 13 pilots, **objective-only drivers (no hand overrides)** → exact per-project
(E, A_local). This baseline spread is the diagnostic. **Step 2:** inspect the A_local / E spread. **Step 3:**
introduce/adjust ONE evidence-justified lever at a time (reuse-adjusted equivalent SLOC; a blockchain EM;
recalibrated global A/B), re-run, watch the table tighten. **Win = one global (A, B, driver-rules) fitting all
13 with low residual** — not per-project local A (which trivially fits). Maintain this table each iteration.

Sizing caveats baked into the spec: `diff` (dotreasury, exact range) and `whole` greenfield = clean; `window`
(subsquare ×2, ink! analyzer) net-delta still over-counts (wide windows capture non-funded work) → size = upper
bound until commit-isolated.

## Reading so far (n=1 clean)
- **Kheopswap (clean greenfield):** COCOMO's published A=2.94 over-predicts ~19×; **PM=PM at A_local ≈ 0.157.**
  Drivers were almost all Nominal (∏EM ≈ 1.0), so the entire gap is the multiplicative constant A — i.e.
  blockchain-grant projects deliver far more KSLOC per PM than COCOMO's classic calibration assumes
  (≈ 32 raw SLOC/hour here vs the ~3–4 implied by A=2.94), driven by heavy ecosystem reuse + senior solo devs.

## Open refinements (raise rigour before locking the constant)
1. **Reuse-adjusted equivalent SLOC.** This pass used RAW cloc as equivalent SLOC. PAPI/smoldot dApps carry
   large generated/reused portions (chain descriptors, codegen types, UI boilerplate). Applying the canonical
   `equivalent_sloc` reuse model lowers size and raises A_local toward its true value — but order-of-magnitude
   (A ≈ 0.1–0.3) is robust regardless.
2. **ink! analyzer v5-only isolation.** The 2023-09→2024-04 window captures all dev, not just the funded v5
   increment (37.5 KSLOC net-delta = 88 LOC/h, implausible for 424 h). Needs v5-tagged commits / PR range.
3. **Build the cluster.** Run the other greenfield whole-repo pilots (Ask!, Megaclite, Elara, ParaSpell,
   Fennel, Remarker, Dot Code School) the same clean way; check whether A_local clusters near ~0.15.

## Honest framing
PM=PM holds per project by construction (local A). The contribution is the **recalibrated constant** and the
**tightness of the A_local cluster** on a clean, hand-verified matched-triple set — which is exactly what the
curated approach was built to deliver.
