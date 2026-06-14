# Per-pilot COCOMO II dissection — running results (PM=PM via local A)

For each verified pilot: measure matched-slice size → assign 22 drivers (objective + evidence overrides)
→ E = 0.91 + 0.01·ΣSF, ∏EM → PM_pred at published **A = 2.94**, and the **A_local** that makes
PM(COCOMO) = PM(reported). The scientific result is whether A_local **clusters** across the clean set
(a tight cluster ⇒ one defensible Blockchain-COCOMO constant). Published COCOMO II A = 2.94.

| Pilot | Size (KSLOC) | size basis | E | ∏EM | Reported PM | PM_pred@2.94 | over-pred | **A_local** | status |
|---|---|---|---|---|---|---|---|---|---|
| 11 Kheopswap | 15.36 | cloc whole-repo (greenfield) | 1.100 | 0.999 | 3.16 | 59.25 | ~19× | **0.157** | CLEAN anchor |
| 12 ink! analyzer | 37.49 | net-delta window (TOO WIDE) | 1.070 | 1.344 | 2.79 | 190.9 | ~68× | 0.043 | size inflated — re-do v5-only |

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
