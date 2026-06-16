# Dataset Expansion Charter — Blockchain-COCOMO Matched-Triple Corpus
*The governing protocol for the 100-day n-growth campaign. Locked v1.0, 2026-06-15.*
*Twin north stars (mandate): **QUALITY** and **DIVERSITY**. Pace: very slow, very keen, very clean —*
*each pilot fully analyzed and admitted one at a time. No figure enters until read from its primary source.*

---

## 0. Mandate

Build the matched-triple software-effort dataset that **surpasses Boehm's COCOMO II.2000 calibration set
(n = 161 projects)** — not only in count but, decisively, in **auditability, provenance, and diversity**.
Boehm's 161 points were largely proprietary, confidentially self-reported, gathered through heterogeneous
instruments, and are not independently re-checkable. Our corpus answers each of those weaknesses by
construction: every point is traceable to a primary, frequently **on-chain**, source that anyone can re-read,
pinned to an exact commit, and — new in this campaign — **author-confirmed** wherever we can reach the team.

> **"Surpass by all means" is operationalized as: n ≥ 165 admitted pilots AND every transparency/auditability
> property strictly greater than Boehm's set AND deliberate diversity coverage (not convenience sampling).**

This charter inherits, unchanged, every standard already established: the matched-triple unit, the CEVRP
reuse rule, the integrity invariants (no reverse-engineering drivers to the target), the SA-primary metric,
and the auditable exclusion log. It adds the machinery to scale that standard to 165+ while *raising* rigour.

---

## 1. The unit — a verified matched triple (hardened)

A pilot is admitted only as a complete record:

`{ reported effort → PM · the single repo + pinned commit/range that produced it · executed-funding proof
   · author contact · verification status }`

The first three are the original triple. The last two are **new required fields** for this campaign: a pilot
cannot be *admitted* without (a) at least one captured author-contact channel and (b) a verification-status
value (even if that value is "public-record only, no response").

---

## 2. Inclusion gates — a candidate becomes a pilot only if ALL pass

| Gate | Condition | Failing → |
|---|---|---|
| **G1 Matched scope** | Reported effort maps to **one** repository / commit-range, unambiguously | reject (multi-repo umbrella) |
| **G2 Completed & verifiable** | Work is *delivered and measurable*, not a forward-only estimate with no artifact | reject / hold |
| **G3 Funding proof** | Executed on-chain transaction, OR durable milestone acceptance (curator-verified) | reject (never-awarded / rejected on-chain) |
| **G4 Effort traceable** | Effort figure quoted verbatim from a primary source; tagged **Actual** or **Proposed** | reject (no person-effort figure) |
| **G5 Size measurable** | Sizable under whole / window / diff at a pinnable SHA | reject (repo deleted / unbuildable) |
| **G6 CEVRP-evaluable** | Reuse/scope assessable against C1–C3 of the locked reuse protocol | hold for evidence |
| **G7 Author-contactable** | ≥ 1 contact channel captured (email / GitHub / org / social) | hold (cannot verify) |

Every rejection is appended to the **exclusion log** with the *named* failing gate, so the curation is
reproducible from the criteria alone (this log is itself a contribution — it proves the corpus is not
cherry-picked for favourable fits).

---

## 3. Diversity matrix — the axes we deliberately spread across

Diversity is a *design target*, pursued quota-style: we actively seek under-represented cells rather than
admitting whatever is easiest to find. Each pilot is tagged on every axis; coverage gaps drive the next
discovery wave.

| Axis | Buckets (seek spread, not concentration) |
|---|---|
| **Ecosystem / chain** | Polkadot · Kusama · Ethereum + L2s · Solana · Cosmos · NEAR · Tezos · Aptos/Sui (Move) · Bitcoin/Stacks · Filecoin · Stellar · Algorand · multi-chain |
| **Funding mechanism** | On-chain treasury/governance · foundation grant · retroactive public goods (RetroPGF) · bounty · hackathon→grant graduation |
| **Project type** | L1/runtime · smart-contract language/compiler · crypto/ZK library · RPC/node infra · wallet · DEX/DeFi · NFT/marketplace · governance app · dev-tooling/LSP · education · oracle · bridge/XCM · indexer/data |
| **Size class** | XS (<2 KSLOC) · S (2–10) · M (10–30) · L (30–100) · XL (>100) |
| **Effort type** | Actual (retrospective) · Proposed (forward) — **target ≥ 50 % Actual** |
| **Effort magnitude** | sub-PM · 1–5 PM · 5–20 PM · 20–100 PM · >100 PM — **deliberately seek large projects to beat Boehm's range** |
| **Team size** | solo · small (2–4) · team (5+) |
| **Language / stack** | Rust/Substrate · ink! · Solidity · Vyper · Move · Go/Cosmos-SDK · Rust/Solana(Anchor) · TS/JS · AssemblyScript · Cairo |
| **Geography** | spread of team regions (record where known) |

A live **diversity tracker** (intake register) reports coverage per cell after every admission.

---

## 4. Source universe — everything, ordered by provenance strength

| Tier | Sources | Why / extraction |
|---|---|---|
| **A — strongest (on-chain executed)** | Polkadot OpenGov · Kusama treasury | We read the executed transaction itself (Subsquare / Polkassembly). Itemized effort common. The backbone — hundreds still unmined. |
| **B — durable structured delivery** | Web3 Foundation grants · Polkadot Fast-Grants | Public GitHub repos of applications + milestone deliveries; FTE×duration fields; curator-verified acceptance. |
| **C — large public grant corpora** | Ethereum: Gitcoin Grants, EF ESP, Optimism RetroPGF, Arbitrum, Uniswap/Aave grants · Solana Foundation · Cosmos (ICF/Interchain) · NEAR · Tezos (TF / Tezos Commons) · Aptos/Sui · Polygon · Filecoin · Stellar Community Fund · Algorand | Proposals + deliverables, often with retrospective reports. Adds dominant ecosystems and a **market-rate productivity contrast** to the grant-context constant. |
| **D — out-of-the-box (completed, reported effort)** | Foundation-funded OSS with public effort reports · hackathon→grant graduations with logged hours · published blockchain-SE effort datasets (reuse with citation/permission) · audit-firm effort-days (flagged as *audit*, not dev — separate stratum) | Broadens beyond grant programs; each documented with how effort + proof + repo are extracted. |

No source is excluded a priori ("everything and anything that brings us on top"); provenance strength simply
sets the order and the confidence flag attached to each pilot.

---

## 5. Per-pilot intake pipeline — the assembly line (one pilot at a time)

| Stage | Action | Output |
|---|---|---|
| **1 Discover** | Harvest a candidate from a Tier A–D source | candidate row (intake register) |
| **2 Triage** | Test against gates G1–G7 | accept-to-analyze / reject (logged) |
| **3 Provenance read** | Open the on-chain tx / grant record *with our own eyes*; record amount (native + **USD @ execution**), dates, links | provenance block |
| **4 Repo pin** | Identify the one repo + commit/range; pin SHA | pinned ref |
| **5 Effort extraction** | Verbatim figure → PM (152 h/PM, or ÷4.345 for dev-weeks); tag A/P; capture itemization | effort record |
| **6 Size + CEVRP** | CI dissection: size, E, ∏EM, A_local; apply CEVRP C1–C3 | dissection JSON |
| **7 Contact capture** | Author name(s), GitHub, email, org, alt channel, source-of-contact | contact block |
| **8 Author verification** | Send confirmation email (template §6); record response; follow up if doubtful & non-responding | verification status |
| **9 Admit** | Write full record to VERIFIED_PILOTS; update diversity tracker + change_log | admitted pilot |

**Nothing is admitted before Stage 9.** A candidate may sit in "in-analysis" or "emailed" for as long as it
takes. This is the literal meaning of *very slow, very keen, very clean*.

---

## 6. Author-verification protocol (user-mandated)

**Contact info is a required, first-class field**, captured for every picked candidate:
`primary_email · github_handle · org · alt_channel (X/Discord/LinkedIn) · source_of_contact`.

**Policy:** we *pick good data first*, then **email everyone** whose data we admit. The email asks the author
to confirm: (a) total effort and unit; (b) the exact repo + commit range that delivered the funded work;
(c) team size and seniority; (d) any forked/generated/reused fraction; (e) whether the figure is actual or
budgeted.

**Verification-status values:** `unverified → emailed → author-confirmed | author-corrected | no-response`.

**Follow-up cadence:**
- Data carries **any doubt** AND no response → follow-up at **+7 days** and **+21 days** (max 2 follow-ups).
- Data is **doubt-free** AND no response → single email, then proceed flagged **"public-record only."**
- `author-corrected` → update the figure to the corrected value, keep the original in the change_log.

All correspondence is logged (date, channel, outcome) for audit. **I will draft and queue every email but
will not send on your behalf without your explicit approval per batch.**

---

## 7. Quality bar vs Boehm (how we win on substance, not just count)

| Property | Boehm COCOMO II.2000 (n=161) | This corpus (target) |
|---|---|---|
| Independent auditability | Mostly confidential / proprietary | **Every point** re-readable at a primary source (often on-chain) |
| Effort confirmation | Self-reported, instrument-mixed | **Author-confirmed** flag where reachable + on-chain itemization |
| Size reproducibility | Reported KSLOC, not re-measurable | **Pinned SHA**, re-measurable via published CI |
| Provenance | Survey records | Public, versioned, fully-logged (on-chain JSON / grant markdown) |
| Diversity control | Convenience sample | **Quota-driven** across 9 explicit axes |
| Exclusions | Not published | **Logged with named failing gate** |

Surpassing Boehm therefore means: **count ≥ 161 AND every row strictly more auditable.**

---

## 8. Cadence & statistical gating (100-day horizon)

- A **live intake board**: candidates → in-analysis → emailed → admitted / rejected.
- **Weekly checkpoint:** admitted count, diversity-coverage gaps, author response rate, exclusion tally.
- **Gated re-fit:** recompute the global constant A, its bootstrap CI, SA, and PRED(30) at milestones
  **n = 15, 25, 40, 60, 100, 161+**. Watch the CI tighten; watch whether A holds across ecosystems (the
  generalizability test) or splits by chain (also a result). Never let convenience sampling skew the matrix.
- **Pre-registration:** before the n = 60 milestone, register a holdout (≥ 5 untouched pilots) to validate
  the constant out-of-sample, addressing the reviewers' overfitting concern at scale.

---

## 9. Integrity invariants (carried over, non-negotiable)

1. Driver values are set from project evidence, **never** reverse-engineered from the residual to the target.
2. **Raw size is the conservative default**; reuse correction is applied **only** through the locked CEVRP.
3. Every exclusion is logged with the **named** failing gate.
4. Negative results are reported in full.
5. Every effort, amount, and proof is read from its **primary source** before admission — "with our own eyes."

---

*This charter is the rail for every subsequent action in the n-growth campaign. It is versioned; any change to
a gate, axis, or protocol is recorded with rationale in `provenance/change_log.md`.*
