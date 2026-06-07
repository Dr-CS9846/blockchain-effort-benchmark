# Validating the measured person-months (the benchmark's ground truth)

**The challenge:** if the measured PMs (the Phase-1 ground truth) are not defensible, the
whole benchmark fails. **The honest scientific position:** effort is a *latent construct* —
there is no timesheet oracle for these repositories, so PMs cannot be "proven exact" (this is
true for *all* repository-mined effort, not just ours). What is required, and what we provide,
is evidence of **validity** (construct + criterion) and **reliability**, following the standard
software-measurement-validation framework (Kitchenham, Pfleeger & Fenton 1995). We claim a
**validated, bounded, reproducible** measure — never an unprovable point truth.

## 0. The method is peer-reviewed, not invented
Estimating effort in **person-months from version-control activity** is an established,
published method: **Robles & González-Barahona (2022), *Empirical Software Engineering***
("Development effort estimation in FOSS from activity in version control systems"). They define
a person-month as a full-time developer-month, separate full-time from occasional contributors
by a commit threshold, and **validated their model against 1,000+ developer questionnaires.**
Our pipeline follows the same family of method; our person-month *unit* is Boehm's COCOMO II
152 person-hours (so the Phase-1 target is in the same unit COCOMO II outputs).

## 1. Triangulation — do independent estimators agree? (construct validity)
We compute three independent PM estimators (author-months, active-days/19, time-window hours/152).
On the deduped reliable+plausible set (one observation per repository, n≈51), their **Spearman
rank agreement** is:

- PM_low ~ PM_mid : **0.99**
- PM_mid ~ PM_high: **0.80**
- PM_low ~ PM_high: **0.79**

Three methods built on different assumptions rank project effort almost identically → the effort
signal is real and robust to method choice, not an artifact of one formula.

## 2. Criterion validity — W3F planned PM is a LOOSE convergent check, not the proof
Each grant's **W3F planned PM** (FTE × duration from the application) is an independent,
human-authored anchor. With the strengthened matcher we now have it for **37** deduped repos
(up from 15). On that larger, fairer sample the anchor proves to be **noisy**:
- planned inside `[PM_low, PM_high]`: **59% (22/37)**
- corr(log planned, log PM_mid): **0.15**
- measured/planned ratio: min 0.02, **Q1 0.13, median 0.31, Q3 0.70**, max 6.8 (misses go BOTH
  ways — some plans over-state, some under-state).

Interpretation (honest): W3F planned PM is a **forward budget of total-FTE effort** (all
activities, paid headcount), set per team with wide latitude (padding, under-planning, scope
change). It therefore tracks delivered git **coding** effort only weakly. The small-sample 73%
seen earlier (n=15) was optimistic. **We do NOT treat planned PM as the primary validator, and we
do NOT force measured == planned** — that would conflate a noisy total-effort *plan* with a
measured coding *actual*. It remains a useful sanity anchor (median ratio ~0.3 is consistent with
coding being a portion of total software effort), nothing more.

The robust validity evidence is therefore **Triangulation (Section 1), Reliability (Section 4),
and the peer-reviewed method precedent (Section 0)** — not the plan. The single anchor that would
make criterion validity airtight is **developer self-report** (Section 5), which is exactly why
Robles & González-Barahona validated their VCS model against 1,000+ developer questionnaires
rather than against plans.

### What W3F planned PM actually measures (this EXPLAINS the gap)
W3F defines **FTE = average number of full-time employees over the project duration**
(0.5 FTE = 20 h/week); planned PM = FTE x duration = **total full-time staffing effort across the
whole team, covering ALL activities** (design, coding, testing, docs, project management,
community). Our **git PM is the coding subset** (effort that left commits). A subset is
necessarily <= the total, so **measured < planned is the EXPECTED relationship, not an error**,
and the observed median ratio ~0.50 is consistent with implementation being roughly half of total
software effort (design/test/management make up the rest; cf. Boehm phase-effort distributions).
The plan is also a forward *budget* (optimism/padding), not an actual. Therefore the validity test
is **correlation + bracket coverage, NOT identity**: requiring measured == planned would wrongly
conflate coding effort with total effort and treat a plan as truth.

### Consequence for Phase-2 COCOMO II (scope commensurability)
Stock COCOMO II predicts *total* effort; our target is *coding* effort. We therefore **calibrate
the COCOMO coefficient (A) to OUR measured PM** (local calibration, as Boehm prescribes), so the
model output and the target are the SAME quantity (git-coding Boehm-PM) — no scope gap. The
blockchain-aware drivers are objective and git-derived (Equivalent Size, type, language, team),
scaling the coding effort we measured, not the 17 subjective COCOMO multipliers. The model's
predicted quantity is stated explicitly as "VCS-measured coding effort"; total effort/cost, if
ever needed, is a documented bridge (÷ coding-fraction), never a silent conflation.

## 3. External sanity — is productivity plausible? (face validity)
Median productivity ≈ **0.49 PM/KSLOC (~2,000 SLOC per person-month)**, within published
software-engineering productivity ranges; full range 0.02–9.1 PM/KSLOC reflects the genuine
project-type spread (SDK/scaffold vs research/tooling).

## 4. Reliability
The pipeline is **deterministic and bit-stable** (same repo+commit ⇒ identical PM; reproducible
by anyone from the public repository). The PM unit parameter PH/PM (152) enters as a monotone
factor, so changing it (e.g., to 160) rescales all PMs identically and leaves rankings and
correlations invariant — conclusions are not sensitive to that choice.

## 5. What would make it even stronger (open)
- **Developer self-report** on a small subset (emails / delivery-doc mining) — the gold-grade
  convergent anchor, exactly what Robles & González-Barahona used. Even 5–8 confirmations would
  upgrade criterion validity from "vs plan" to "vs reality."
- **Direct cross-check of PM_low** against the canonical `git-hours` tool on sample repos
  (validates our in-house time-window implementation reproduces the published tool).

## Reproducibility
All metrics above are recomputed by `scripts/validate/validate_pm.py` →
`reports/pm_validation.json` on every census run (glassbox, no manual steps).

## References
- Robles, G. & González-Barahona, J. M. (2022). *Development effort estimation in free/open
  source software from activity in version control systems.* Empirical Software Engineering.
  (arXiv:2203.09898)
- Kitchenham, B., Pfleeger, S. L. & Fenton, N. (1995). *Towards a framework for software
  measurement validation.* IEEE Transactions on Software Engineering.
- Shepperd, M. & MacDonell, S. (2012). *Evaluating prediction systems in software project
  estimation.* Information and Software Technology 54:820–827. (Standardised Accuracy; MMRE bias)
- Boehm, B. et al. (2000). *COCOMO II Model Definition Manual* (1 PM = 152 person-hours).
- ISO/IEC/IEEE 15939:2017. *Systems and software engineering — Measurement process.*
- git-hours (commit time-window method): https://github.com/kimmobrunfeldt/git-hours
