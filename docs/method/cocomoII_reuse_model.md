# COCOMO II Reuse Model — canonical equivalent SLOC for the benchmark (conformance gap #9)

**Goal.** Replace raw authored KSLOC with COCOMO II's **equivalent SLOC**, so that delivered code
which was *reused/adapted* (frameworks, templates, copied third-party, generated bindings) is
discounted to its true effort weight. This is the one remaining canonical size gap (conformance
audit #9) and the most direct lever on the **off-chain** archetypes, where vendored JS/TS and
boilerplate inflate the final tree. Reference: *COCOMO II Model Definition Manual v2.1 (2000) §2.2*.

---

## 1. The canonical equations (verbatim form)

For adapted/reused code:

&nbsp;&nbsp;**AAF = 0.4·DM + 0.3·CM + 0.3·IM**   (Adaptation Adjustment Factor)

&nbsp;&nbsp;**AAM** = ( AA + AAF·(1 + 0.02·SU·UNFM) ) / 100&nbsp;&nbsp; if AAF ≤ 50
&nbsp;&nbsp;**AAM** = ( AA + AAF + SU·UNFM ) / 100&nbsp;&nbsp; if AAF > 50

&nbsp;&nbsp;**Equivalent SLOC = (New SLOC) + (Adapted SLOC) · AAM**

Parameters (Manual tables): **DM** = % design modified, **CM** = % code modified, **IM** = %
integration & test effort vs new; **AA** = assessment & assimilation (0–8); **SU** = software
understanding (10 very-structured … 50 very-unstructured; **0 when DM = CM = 0**); **UNFM** =
programmer unfamiliarity (0 completely familiar … 1 completely unfamiliar). New code → AAM = 1.

---

## 2. The trap we must avoid: in-window churn (circularity)

The tempting shortcut is to set "new SLOC = lines the team added during the grant window" (git
churn). **We will not do this.** Our effort proxy (`pm_mid`) is itself derived from in-window git
activity; making size another function of in-window activity would correlate size with effort *by
construction*, inflating SA/PRED artificially and destroying the result's defensibility. (This is
why the earlier blame-in-window idea was correctly rejected.)

**Principle:** equivalent SLOC must be a property of the **delivered artifact's composition**
(how much of the final product is new vs adapted), *not* a measure of in-window activity volume.

---

## 3. How we derive New vs Adapted from git evidence (non-circular, reproducible)

At the pinned **delivery commit**, classify each surviving logical source line of the
already-generated-excluded tree by **origin**, using `git blame`:

- **ADAPTED/REUSED (ASLOC):** lines whose introducing commit is the project's **initial import**
  (the first commit, or an early bulk scaffold/fork drop — detected as a commit adding ≫ the
  repo's median commit size), **or** lines under vendored/third-party paths
  (`vendor/`, `third_party/`, copied `openzeppelin*`, node-template boilerplate, `typechain`-style
  generated bindings).
- **NEW (New SLOC):** every other surviving line — i.e. code the project authored on top of the
  scaffold, regardless of *when* (origin-based, not window-based ⇒ non-circular).

This uses blame only to attribute **surviving final-tree lines** to import-vs-developed origin —
a property of the product, not of activity. A repo with 10 commits or 200 commits delivering the
same 8 kSLOC of developed code gets the same size; only effort differs. ✔ non-circular.

**CM proxy (modification of the adapted base):** CM = fraction of the initial-import lines that
were later edited by project commits (git evidence). DM and IM are not separately observable from
git → set conservatively (DM = CM, IM = small default), and report sensitivity. SU follows the
Manual table; UNFM defaults to "mostly familiar".

---

## 4. Default parameters (documented, conservative, sensitivity-reported)

| Param | Default | Basis |
|---|---|---|
| AA | 2 | basic assessment of a known framework |
| SU | 30 | nominal-structure understanding (Manual Table) |
| UNFM | 0.3 | mostly familiar (grantees work in their own stack) |
| DM | = CM | git-observed code modification used for design proxy |
| IM | 10% | modest integration of adapted base |

These yield a specific AAM per repo from §1; **we will report SA/PRED under a sweep of these
defaults** (e.g. UNFM ∈ {0,0.3,0.6}, AA ∈ {0,2,4}) so no single hand-set value drives the result.

---

## 5. Prospective applicability (firm-facing)

A blockchain firm estimating a new project supplies exactly these COCOMO inputs up front: expected
**new SLOC**, expected **adapted SLOC** (framework/template they'll build on), and DM/CM/IM/AA/SU/
UNFM judgements. So equivalent SLOC is fully prospectively estimable — the calibration just *derives*
the same quantity from git for the historical W3F set.

## 6. Plan

1. `scripts/extract/equivalent_sloc.py`: full-history clone at delivery commit → blame-classify
   New/Adapted (generated already excluded) → compute AAM → `equivalent_sloc`, plus raw
   `new_sloc` / `adapted_sloc` / `cm_observed` for transparency.
2. Add `equivalent_sloc` (+ components) to `measurements_census.csv`.
3. Re-fit `cocomo_localcal` with **`ln_equivalent_sloc`** as the size candidate alongside `ln_ksloc`;
   compare per-archetype SA/PRED — **expected: off-chain tightens** (vendored/boilerplate reclassified
   as adapted at low AAM), on-chain stable.
4. Keep raw KSLOC reported side-by-side (honesty + ablation).

**Decision to confirm before coding:** the New/Adapted classification rule in §3 (initial-import +
vendored-path origin, blame on surviving lines). This is the crux; everything else is the Manual's
formula applied with documented parameters.
