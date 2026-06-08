# Blockchain COCOMO II — variable SYNTHESIS specification (keep all 22 + constants + blockchain EMs)

**Aim (Phase 2):** a fully functional COCOMO II model whose predicted PM reproduces our *measured*
PM (PM = PM). We **keep every COCOMO II variable and constant** — nothing is dropped. Each variable
is **synthesized objectively** from the repository/grant where a defensible signal exists; where no
defensible repository signal exists, it is set to **Nominal** (COCOMO's own baseline, multiplier
1.0 / nominal SF) — present, not discarded. We apply the **published COCOMO II.2000 rating tables**
(values applied verbatim; verified against the COCOMO II Model Definition Manual at implementation)
and **calibrate only the constant A** (B fixed at 0.91 unless a refit is justified), per Boehm's
local-calibration guidance. This aligns with the existing COCOBLOCK design (18/22 directly apply,
4 modified: PREC, DATA, PCON, APEX; 7 blockchain EMs added).

## Model form
    PM_pred = A · (KSLOC)^E · (∏ EM_i) · (∏ BC_EM_k)
    E = B + 0.01 · Σ_j SF_j         (B = 0.91)
- KSLOC = delivered source size, generated-code excluded (Phase-1 measure).
- SF_j  = 5 scale factors (published SF values per rating).
- EM_i  = 17 standard effort multipliers (published EM values per rating).
- BC_EM_k = 7 blockchain effort multipliers (COCOBLOCK; values start at design defaults, may be
  calibrated later).
- A calibrated so median/most predicted PM ≈ measured PM_mid (local calibration).

**Rating synthesis principle:** every rule maps an OBJECTIVE repository signal → a COCOMO rating
(VL/L/N/H/VH/XH); unknown ⇒ **Nominal**. Rules are pre-registered and unit-tested before fitting.
Signals available per repo: KSLOC & languages (cloc), git history (authors/commits/dates/duration),
repo files (tests/, .github/workflows CI, Dockerfile, docs/, SECURITY.md, audit reports),
dependency manifests (Cargo.toml/package.json → crypto/zk/consensus/xcm libs), grant metadata
(W3F level, milestones, planned FTE/duration/cost), on-chain vs off-chain structure.

---

## 1. Scale Factors (5) — set the exponent E
| SF | synthesis signal → rating | default | blockchain adaptation |
|---|---|---|---|
| **PREC** (precedentedness) | template-fork/standard pattern ⇒ High (precedented); novel chain/consensus or new primitive ⇒ Low; typical pallet/dApp ⇒ Nominal | Nominal | *modified*: emerging blockchain standards lower precedentedness |
| **FLEX** (flexibility) | milestone-fixed grant deliverables ⇒ Nominal (low variance across corpus) | Nominal | — |
| **RESL** (risk/arch resolution) | architecture docs + tests + CI present ⇒ High; none ⇒ Low | Nominal | — |
| **TEAM** (cohesion) | single owner-org contributors ⇒ High; many external orgs ⇒ Low | Nominal | — |
| **PMAT** (process maturity) | CI + tests + Docker + releases (count signals) ⇒ High; none ⇒ Low | Nominal | — |

## 2. Effort Multipliers — Product (5)
| EM | synthesis signal → rating | default | blockchain adaptation |
|---|---|---|---|
| **RELY** | audit report / SECURITY.md / handles-funds (DeFi) ⇒ High–VeryHigh | Nominal | *RELY → audit criticality* (funds at risk) |
| **DATA** | on-chain storage-heavy vs light; data-file ratio | Nominal | *modified*: on-chain vs off-chain storage |
| **CPLX** | crypto/consensus deps+keywords ⇒ High; ZK/novel-crypto ⇒ VeryHigh; plain CRUD ⇒ Low | Nominal | core blockchain complexity driver |
| **RUSE** | SDK/library project type ⇒ High; one-off app ⇒ Nominal | Nominal | libraries built for cross-project reuse |
| **DOCU** | docs/comment ratio: rich ⇒ High; sparse ⇒ Low | Nominal | — |

## 3. Effort Multipliers — Platform (3)
| EM | synthesis signal → rating | default | blockchain adaptation |
|---|---|---|---|
| **TIME** | Solidity/smart-contract + gas-optimization signals ⇒ High–VeryHigh | Nominal | *TIME → gas/execution constraint* |
| **STOR** | on-chain storage-cost-sensitive code ⇒ High | Nominal | on-chain storage is the "memory" constraint |
| **PVOL** | Substrate/Polkadot-SDK stack (frequent breaking changes) ⇒ High; mature/stable stack ⇒ Nominal | Nominal | chain-SDK volatility is real |

## 4. Effort Multipliers — Personnel (5)
| EM | synthesis signal → rating | default | reasoning |
|---|---|---|---|
| **ACAP** | no reproducible objective signal | **Nominal** | analyst skill not observable from repo |
| **PCAP** | no reproducible objective signal | **Nominal** | programmer skill not observable; also risks leaking into effort proxy |
| **PCON** | author retention first-third vs last-third of window | Nominal | *modified*: crypto turnover; computed cautiously (endogeneity-aware), else Nominal |
| **APEX** | org's prior W3F grants / prior domain commits if detectable | Nominal | *modified*: blockchain learning curve; weak signal ⇒ Nominal mostly |
| **PLEX** | experience with the specific chain stack (weak) | Nominal | *modified*: specialized blockchain skills; mostly Nominal |
| **LTEX** | (note: LTEX is the 6th personnel-ish factor in COCOMO II) dominant-language tooling maturity | Nominal | language/tool experience; weak ⇒ Nominal |

## 5. Effort Multipliers — Project (3)
| EM | synthesis signal → rating | default |
|---|---|---|
| **TOOL** | CI + linters + formatters + test framework present ⇒ High (lowers effort); none ⇒ Low | Nominal |
| **SITE** | contributor multi-org/timezone spread (weak) | **Nominal** |
| **SCED** | planned-duration compression vs typical (planned is noisy) | **Nominal** |

## 6. Blockchain Effort Multipliers (COCOBLOCK, 7) — the blockchain-aware extension
Values begin at the COCOBLOCK design defaults (refit later if data supports). Each is synthesized
from objective signals; absence ⇒ 1.0 (no effect), never dropped.
| BC_EM | meaning | synthesis signal → multiplier |
|---|---|---|
| **BC_BEM** | baseline blockchain overhead | 1.0 baseline for all blockchain repos (or a calibrated blockchain constant) |
| **BC_DC** | decentralization / consensus complexity | consensus/runtime code present ⇒ >1 (e.g. 1.1) |
| **BC_EM_GAS** | gas optimization effort | Solidity/EVM contract ⇒ ~0.95–1.1 |
| **BC_EM_AUD** | audit/security overhead | audit report / SECURITY.md / formal-verification ⇒ >1 |
| **BC_EM_MC** | multi-chain / cross-chain | XCM / bridge / multi-chain deps ⇒ >1 |
| **BC_EM_REG** | regulatory / compliance | KYC / identity / compliance keywords ⇒ >1 |
| **BC_EM_NODE** | node / chain infrastructure | runs a full node/chain (runtime) vs contracts-only ⇒ >1 |

## 7. Calibration & evaluation (PM = PM)
1. Synthesize all variables per repo (objective rules + Nominal defaults), store ratings AND values.
2. Compute `PM_pred = A·KSLOC^E·∏EM·∏BC_EM` with COCOMO II.2000 published values; E from SFs.
3. **Calibrate A** to measured **PM_mid** (log-space: A = exp(mean(ln PM_mid − ln(KSLOC^E·∏EM)))) —
   Boehm local calibration; B fixed 0.91 (refit B only if strongly justified, documented).
4. Evaluate predicted-vs-measured under **LOOCV**: MMRE, MdMRE, PRED(25/30), and **Standardised
   Accuracy** + effect size (MMRE is biased; Shepperd & MacDonell). Sensitivity on PM_low/PM_high.
5. Compare against M0 (size-only) to quantify the value added by the synthesized drivers.
6. Report which variables are Nominal-defaulted (transparency) and the distribution of synthesized
   ratings, so the synthesis is auditable.

## 8. Guardrails
- Exact COCOMO II.2000 SF/EM values are applied verbatim from the Manual (verified at implementation).
- No variable is dropped; Nominal is a *present* value with reasoning recorded.
- Rating-synthesis rules are objective, pre-registered, unit-tested; nothing hand-rated per project.
- Personnel-skill factors (ACAP/PCAP/…) default Nominal because they are unobservable from repos —
  this is COCOMO-consistent (Nominal = average), not a removal.
