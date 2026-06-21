# æternity JS SDK — within-project repeated-measures result (2026-06-20)

A controlled within-subject panel: **one developer (Denis Davidyuk), one repository
(`aeternity/aepp-sdk-js`), one language/toolchain**, observed over multiple quarters with
**itemised actual hours** (retroactive final reports) and **quarter-specific git churn**.
Everything that normally varies across projects is held constant; only the quarter's work changes.

## The panel (5 of 6 quarters measured; Q4-2023 churn pending a re-run)

| quarter | hours | churn (KSLOC added) | h / KSLOC |
|---|---|---|---|
| Dec 2022 – Mar 2023 | 342.8 | 4.91 | 70 |
| Q2 2023 | 412.0 | 2.05 | **201** |
| Q2 2024 | 384.9 | 3.74 | 103 |
| Q3 2024 | 253.4 | 8.91 | **28** |
| Q4 2024 | 196.4 | 2.05 | 96 |
| (Q4 2023) | 115.3 | — pending | — |

## Result — size/churn is a *weak* effort predictor even under perfect controls

- **Pearson r(churn, hours) = −0.25** (ln–ln r = −0.06). Quarterly churn does **not** predict quarterly
  hours; if anything the sign is negative.
- The same developer on the same codebase ranges **28 → 201 h per KSLOC — a ~7× productivity swing**
  quarter to quarter. The starkest contrast:
  - **Q2-2023: 412 h produced only 2.05 KSLOC** of net churn (slow, hard work — design/debugging),
  - **Q3-2024: 253 h produced 8.91 KSLOC** (fast, high-volume — mechanical/scaffold churn).

## Why this matters (this is the headline)

This is a **controlled demonstration that effort-per-line is not stable even when team, language,
architecture, and tooling are all fixed.** It means the scatter in the cross-project size→effort law is
**not merely cross-project heterogeneity** — it is intrinsic: the *nature* of a quarter's work (hard
reasoning vs bulk code) drives effort far more than the line count does.

Directly supports the COCOMO thesis: **size alone cannot estimate effort; effort multipliers (esp.
complexity / type-of-work) are necessary**, because even a single developer's h/KSLOC varies 7×. It also
warns against git-churn-as-effort proxies (a separate literature) — here churn is uncorrelated with logged
hours.

*Caveat:* net-delta churn can undercount high-rewrite quarters (adds+deletes cancel), which may deepen the
apparent decoupling; the hours are source-itemised and exact.

## Role in the dataset
- **Within-project study:** this 5–6 point longitudinal panel (a small controlled experiment).
- **Cross-project calibration:** æternity contributes **one aggregated point** — Σ(5 quarters) = 1,589.5 h
  = 10.46 PM on 21.65 KSLOC summed churn (full-6 target 1,704.8 h / 11.22 PM once Q4-2023 churn is
  re-measured). This makes the cross-project set **n = 15 distinct projects, 7 ecosystems** — with **no
  pseudo-replication** (the 6 dependent quarters collapse to one independent point).

Provenance: `reports/dissect_all.json` (CI run #12, window mode). Figure: `reports/figures/aeternity_within_project.png`.
