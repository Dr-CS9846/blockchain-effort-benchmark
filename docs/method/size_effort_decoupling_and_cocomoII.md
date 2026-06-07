# Size → Effort Decoupling and the Blockchain-Aware COCOMO II Direction

**Status:** foundation note written on the *verified* census subset (n = 21) BEFORE scaling.
**Goal (fixed):** effort (size→effort) estimation — map COCOMO II to blockchain and prove it on
git-measured data. Cost/financial modelling is secondary and deferred.

All numbers below come from the reproducible pipeline at the delivered commit of each grant:
KSLOC = source-language code with **evidence-declared generated files removed** (markers only,
size-independent; audited per file), effort = **active person-months** over the measured
first-commit→delivery window, restricted to the **reliable** (≥2 authors, ≥10 commits) and
**duration-plausible** (≤24 mo, excludes fork-contaminated histories) subset.

---

## 1. Finding: delivered size only weakly predicts delivered effort

On the clean subset (n = 21):

| relationship | corr (log–log) | note |
|---|---:|---|
| **KSLOC → effort** | **0.45** | the COCOMO size assumption — only *moderate* |
| authors → effort | 0.71 | see caveat below (partly definitional) |
| duration → effort | 0.63 | see caveat below |
| authors × duration → effort | 0.76 | see caveat below |

**Productivity (PM / KSLOC) spans 0.39 → 9.2 — a ~23× spread.** Delivered LOC and delivered
effort are substantially decoupled. This is the central empirical result that motivates a
multivariable model: a single size→effort power law (plain COCOMO) cannot fit blockchain grants.

### Measurement caveat (stated up front, not buried)
Our effort proxy, *active person-months*, is computed as distinct (author × month) pairs. It is
therefore **structurally related to team size and duration** — so the high `authors`,
`duration`, and `authors×duration` correlations are **partly circular** and are NOT claimed as
predictive findings. The scientifically clean statement is the one about **size**, which is
measured independently of the effort proxy: *size weakly predicts effort (0.45)*. Any future
driver we add must likewise be independent of the effort proxy to count as explanatory.

---

## 2. The decoupling is structured by project type (grounded typology)

Productivity (PM/KSLOC), sorted, reveals three regimes:

- **Size-dense / low PM-per-KSLOC (≈0.4–0.8):** `polkadart` (Dart SDK), `lunokit` (wallet SDK),
  `melodot` (DA chain). SDK / library / config-heavy code: much delivered LOC per unit of effort
  (scaffolding, bindings, boilerplate).
- **Standard band (≈1–3):** `daos`, `tellor`, `eightfish`, `delmonicos`, `ventur`, `typink`,
  `polkamask`, `subquery` — typical Substrate pallets / dApps.
- **Effort-dense / high PM-per-KSLOC (≈4.8–9.2):** `yatima` (Lean VM), `parallel` (DeFi parachain,
  17 authors), `dotnix` (Nix infrastructure), `crossbow` (cross-platform build tooling).
  Research-heavy, novel-language, or tooling work: much effort per unit of delivered LOC.

Interpretation: the residual that plain size cannot explain is **systematic, not random** — it
tracks *what kind of software* the grant delivered. That is precisely the variation COCOMO II
encodes.

---

## 3. Mapping to COCOMO II (the blockchain-aware extension)

COCOMO II Post-Architecture form:

    PM = A · (Size)^E · ∏ EM_i ,   E = B + 0.01 · Σ SF_j

- **Size = Equivalent Size**, not raw KSLOC. COCOMO II already adjusts size for
  generated / reused / adapted code via the Adaptation Adjustment Factor (AAF).
  - *Done:* generated code removed (evidence-based).
  - *Next:* template/adapted code (Substrate `node-template` scaffolding) — the dominant source
    of the "size-dense" regime — to be down-weighted toward an Equivalent Size. This is a core
    thesis contribution: an objective, reproducible Equivalent-Size for blockchain repos.
- **EM (effort multipliers) / SF (scale factors):** classical COCOMO drivers are subjective
  ratings, not recoverable for hundreds of repos. The blockchain-aware extension substitutes
  **objective, git/grant-derived proxies**, each independent of the effort proxy:
  - project **type/domain** (chain · pallet · SDK/library · dApp/frontend · tooling) — derived
    from objective repo signals (dominant language; presence of `runtime/`+`pallets/`; frontend
    ratio; CLI/lib structure), NOT hand-labelled;
  - primary **language/platform** (Rust/Substrate vs TS/frontend vs Solidity vs novel);
  - **novelty/reuse** (from-scratch vs template-fork), via the same Equivalent-Size signal.

Honest framing: this is a *COCOMO II-style, objectively-measurable* model for blockchain grants,
not a reproduction of subjective COCOMO ratings.

---

## 4. Test plan at n ≥ 30 (decision before scaling)

Reach n ≥ 30 by measuring more verified-eligible projects (no methodology change), then fit and
compare, all under leave-one-out / nested CV (leakage-guarded):

- **M0 (baseline):** PM = A · KSLOC^E.
- **M1 (Equivalent Size):** M0 with template/adapted code down-weighted.
- **M2 (+ type/domain factor):** M1 × an objective project-type multiplier.

Report MMRE, MdMRE, PRED(25/30), MAE, SA-vs-random for each. **Decision rule:**
- if M1/M2 materially cut LOOCV MMRE and raise PRED/SA over M0 → the blockchain-aware extension is
  validated → proceed to calibrate on n≥30 and then scale to the full census;
- if not → rework the size/effort definitions before scaling (do not paper over with parameters).

Guardrails: keep the model parsimonious (few drivers vs small n); every driver must be objective
and independent of the effort proxy; pre-register the type-derivation rule before fitting.

---

## 5. What is NOT yet done (open, honest)
- Equivalent-Size adaptation factor for template/scaffold code (only *generated* code removed so far).
- Objective project-type derivation rule (to be specified and unit-tested before use).
- n is 21; the above correlations are indicative, not final — revisit at n≥30.
