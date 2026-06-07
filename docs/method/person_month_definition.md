# Person-Month (PM): definition, unit, and the grounded measurement

This benchmark's Phase-1 deliverable is a set of **defensible, reproducible person-months (PM)**
measured from delivered blockchain git repositories. PM is the unit because COCOMO II — the model
to be calibrated in Phase 2 — outputs PM. This note fixes the definition so it is unchallengeable.

## 1. The unit (published, authoritative)
**1 PM = 152 person-hours** (COCOMO II nominal), i.e. **19 working days × 8 h**, excluding
holidays, vacation, and weekends. In COCOMO II, hours-per-person-month (PH/PM) is an **explicit,
adjustable parameter** with 152 as the default. (Boehm et al., *COCOMO II Model Definition
Manual*.)

There is **no international standard that overrides this**: ISO/IEC/IEEE 15939 (software
measurement process) does not fix a universal hours-per-PM; it instead *requires that the effort
unit be explicitly defined and documented*. We satisfy that by adopting Boehm's 152 h and stating
every parameter here. We use **19** days/PM (= 152 ÷ 8), not the calendar average 19.33/21.7,
because the divisor must be internally consistent with PH/PM and an 8-hour day.

## 2. Why git cannot give exact hours (and the tool double-check)
Git records commit *timestamps*, not hours worked. The published "time-window" method
(implemented by `git-hours`, `git_time_extractor`, GitClear) groups an author's commits into
coding sessions by a gap threshold and adds a fixed buffer for the unseen work before each
session's first commit. We reviewed all three:

- `git-hours`: gap **120 min** + first-commit buffer **120 min**; README states it "might not be
  accurate enough to be used in billing."
- `git_time_extractor`: **3 h** window, **30 min/commit**.
- GitClear: **2 h** default gap; remainder proprietary/commercial.

They use **different parameters and disagree**, which *proves* the pre-first-commit work and
single-commit-day duration are unobservable from git. **No tool resolves this**; each substitutes
a different assumption. Therefore we do not claim exact hours — we **bound** the PM.

## 3. The grounded PM bracket (what we compute per repo)
For each repo at its as-delivered commit, over the measured first-commit→delivery window
(non-merge, non-bot commits; reliable & duration-plausible repos for the headline):

| estimate | definition | bias | role |
|---|---|---|---|
| `PM_high` | active **author-months** (≥1 commit in a month ⇒ 1.0 PM) | over-counts | upper bound |
| **`PM_mid`** | active **developer-days ÷ 19** (Boehm 152 h @ 8 h/active-day) | central | **headline** |
| `PM_low` | time-window **hours ÷ 152** (git-hours method, reimplemented in-house) | under-counts | lower bound |

The true effort lies in **[`PM_low`, `PM_high`]**; `PM_mid` is the Boehm-anchored point estimate.
The time-window method is **reimplemented in our own code** (≈ git-hours' ~30-line algorithm) so
`PM_low` is reproducible and glassbox — no dependence on any external/commercial tool.

## 4. Parameters (all explicit and adjustable)
- `PH_PER_PM = 152` (COCOMO II nominal) · `HOURS_PER_DAY = 8` ⇒ `DAYS_PER_PM = 19`
- `SESSION_GAP_MIN = 120` · `FIRST_COMMIT_MIN = 120` (git-hours defaults)

Sensitivity to any of these can be reported by re-running with different values; the bracket makes
the residual ambiguity visible rather than hidden.

## 5. Known limits (honest)
- An active commit-day with little work is still counted toward `PM_mid` at 8 h — this is exactly
  why `PM_low` (which assigns < 8 h to light days) is reported as the lower bound.
- Effort that produced no commit (design, review, meetings) is invisible to git → all three
  estimates can under-count uncommitted work; this is inherent to repository-mined effort and is
  disclosed, not corrected away.

## Sources
- COCOMO II Model Definition Manual (Boehm et al., USC CSSE): https://athena.ecs.csus.edu/~buckley/CSc231_files/Cocomo_II_Manual.pdf
- Softstar Systems, COCOMO FAQ (152 h/PM = 19 d × 8 h): https://www.softstarsystems.com/faq.htm
- ISO/IEC/IEEE 15939:2017, Measurement process: https://www.iso.org/standard/71197.html
- git-hours (time-window method): https://github.com/kimmobrunfeldt/git-hours
- git_time_extractor: https://github.com/rietta/git_time_extractor
- GitClear, time-per-commit: https://www.gitclear.com/help/estimating_time_used_per_commit
