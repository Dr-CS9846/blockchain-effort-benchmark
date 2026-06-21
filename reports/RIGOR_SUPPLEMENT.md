# Rigor supplement — responses to expert review (2026-06-20)

Statistical strengthening of the pilot calibration on the **core-8 actual-PM matched set**
(A* = 0.564). All computed locally (no CI needed); reproducible from `reports/dissect_all.json`.

## 1. Model-adequacy battery (closes review Gap 2)

| Metric | Value | Reading |
|---|---|---|
| **SA** (1 − MAE_model/MAE_mean-baseline) | **0.711** | strongly beats a naïve mean predictor |
| MMRE | 17% | — |
| **MdMRE** (robust) | **14%** | added per Shepperd & MacDonell (2012) |
| PRED(25) / PRED(30) / PRED(50) | 88% / 88% / **100%** | full cumulative curve |
| **Wilcoxon signed-rank vs classic A=2.94** | **W=0, z=−2.52, p=0.0117** | blockchain A=0.56 **significantly** more accurate (classic MMRE = 433%) |

The "blockchain-COCOMO beats classic COCOMO" claim is now **statistically defended**, not just asserted.

## 2. Joint (A,E) identifiability (closes Gap 1 — better than free-fitting)

Bootstrap free-fit of both parameters (B=10⁴): A = 0.53 [0.27, 1.13], E = 1.18 [0.82, 1.55], and crucially
**corr(lnA, E) = −0.99**. A and E are *not separately identifiable* at n=8 — the bootstrap cloud is a thin
anti-diagonal ridge (`figures/joint_AE_region.png`). This is the rigorous justification for the Boehm-faithful
choice: **fix E structurally (0.91+0.01·ΣSF) and locally calibrate A**. Free-fitting both would report a
spuriously precise pair from an ill-posed problem. (To identify E independently to ±0.1 needs ~100 matched
triples — a dataset-growth target, not a pilot deliverable.)

## 3. Residual & influence analysis (closes Gap 3)

- **Heteroscedasticity**: Spearman(|log-resid|, size) = 0.19 → none (the log-log form is adequate).
- **Temporal drift**: Spearman(year, ln A_local) = 0.14 (2020→2024) → no model drift over the corpus span.
- **Influence**: all Cook's D < 4/n = 0.50; highest is dotreasury (0.48, smallest project, high-leverage but
  below threshold). No single project drives the calibration.

## 4. Effort ground-truth sensitivity (closes review Sec 3.5)

Perturbing every reported PM by ±20% (plausible grantee mis-statement) gives **A* ∈ [0.451, 0.677]** (±20%
band around 0.564). Even under systematic ±20% mis-statement, A stays far below classic 2.94 — the headline
result is robust to the stated-effort assumption.

## 5. Data-verification responses (corrections vs rebuttals)

| Review item | Verdict | Detail |
|---|---|---|
| **TP-57 R2 = 249 not 289** | **REBUTTED — 289 is correct** | Source has 4 contributor sections: PolkADAPT 63 + UI 99 + Explorer API 87 + **Project Support (Arjan) 40** = 289. The 249 omits the 4th section. No change. |
| Ideal Network hours | **CORRECTED** | Master fixed 4380→**2020 h** (source: total actual delivery 2,020 h; ref 1798 was only the 340-h overrun). |
| ref 459 → 439, ref 544 → Talisman, ref 426 920≠926 | **No impact** | These three were already **excluded** from the master (dollar-denominated / non-dev), so the mis-references never entered the calibration. Worth fixing in the friend's working notes, not in our dataset. |
| DotBot | **flagged** | ref 1848 covers "completed + committed future deliverables" → part-prospective; not a clean actual point. |

## 6. Open items requiring the repo owner (housekeeping, not science)

- **v0.1 release tag** (enables DOI/citability) — a publish action; recommend the PI create it.
- **DATASHEET / source_map staleness** (n=13 → current; old filenames → effort_master_final.csv).
- **reports_local/ + stray root file** — `.gitignore` or relocate.
- **TrueBlocks (Ethereum) scope note** — it sits cross-ecosystem; either add a one-line scope justification or
  mark out-of-domain. Note it is `derived(2FTEx12mo)`, so it is already a weaker anchor.
- **dotreasury blank hours** — PM 0.95 is a measured-repo/reported-days figure, not hour-itemised; add an
  explanatory note rather than back-deriving hours from PM (which would be circular).

## 7. Deferred to dataset growth (correctly out of pilot scope)

Hierarchical Bayesian calibration with informative Boehm priors + partial pooling by sub-domain (Sec 3.1),
domain-stratified A (Kruskal-Wallis/Dunn, Sec 3.3), formal power analysis (Sec 3.2), blockchain-adapted SF/EM
tables "BCScale-5" (Sec 4), and a 20–30 project external hold-out (Sec 3.4) all require the larger matched-triple
corpus the team is building toward n=161. They are the right **paper-3** agenda; the pilot stands on §1–4 above.
