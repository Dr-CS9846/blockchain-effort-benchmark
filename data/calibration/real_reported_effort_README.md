# Real reported-effort dataset — verified, classified (2026-06-18)

**38 reported-effort observations, every one verified against its primary source, normalised and classified.**
This is the *rigour* layer to put on the table — not just rows, but rows you can defend line-by-line.

## What makes this different from a raw link-list
1. **Primary-source verified.** Each row's reported hours were read directly from the source file/post (Polkascan
   Oct-2020 = 10+46+49+37 = 142 h ✓; Kusama Ref-83 = 264+164 = 428 h ✓; stakeworld €85/h tables read in full).
2. **PM normalised to Boehm's 152 h/PM** (not the 160 h/PM some sheets use) — so it slots into COCOMO directly.
3. **Classified by work type** — the critical distinction most lists miss:
   - `dev` = software development (TrueBlocks Go port, Polkascan PolkADAPT/Explorer, the 6 gold grants).
   - `maintenance` = software maintenance of a codebase with reported hours (Polkascan Python API periods).
   - `INFRA-OPS` = **flagged**: RPC/bootnode/snapshot *operations* (stakeworld). Real reported hours, but this is
     DevOps, **not** software construction — it must NOT be mixed into a software-effort calibration. Including it
     unflagged is a category error.
4. **Multi-ecosystem, multi-platform** — Polkadot, Kusama, **Ethereum (EF grant)** — sourced from GitHub repos,
   Medium, and (extensible) governance platforms. The data is internet-wide, exactly as noted.

## Honest accounting (so it can't be challenged)
- These 38 rows are **observations across ~9 distinct projects/teams**, not 38 independent projects. The Polkascan
  rows (PK01-PK21) are 21 monthly/quarterly slices of ONE ongoing project — legitimate as *periodic effort
  observations*, but they must be modelled as repeated measures, **not** treated as 21 independent datapoints
  (doing so is pseudo-replication and inflates n artificially).
- `TrueBlocks` PM is **derived** (2 FTE × 12 mo), not itemised hours — flagged as such.
- `INFRA-OPS` rows are real but excluded from software-effort modelling (kept for completeness/transparency).

## How this scales (the proven method)
Voluntary actual-effort reports live across the whole internet: team treasury-report repos (Polkascan, stakeworld),
Medium grant retrospectives (TrueBlocks/EF), OpenGov referenda + Polkassembly/Subsquare posts, Gitcoin/Optimism
RetroPGF. Discovery = enumerate team repos (jsDelivr) + mine governance APIs (Subsquare) + read the post. Each new
diligent-reporter team adds several verified rows. The constraint was scope, not supply.
