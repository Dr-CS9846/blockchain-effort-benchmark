# Real reported-effort dataset: verified and classified (2026-06-18)

38 reported-effort observations, every one verified against its primary source, normalised, and
classified. This is meant to be a rigorous layer, not just a list of rows: rows you can defend
one at a time, with the source behind each one.

## What makes this different from a raw list of links

1. **Primary-source verified.** Each row's reported hours were read directly from the source
   file or post. For example: Polkascan, October 2020, 10 plus 46 plus 49 plus 37 equals 142
   hours, confirmed. Kusama Referendum 83, 264 plus 164 equals 428 hours, confirmed. The
   stakeworld tables, given in euros per hour, were read in full.
2. **Person-months are normalised to Boehm's 152 hours per person-month**, not the 160 hours per
   month some source sheets use, so the figures slot directly into COCOMO.
3. **Classified by work type**, which is the distinction most lists like this miss:
   - `dev`: software development. The TrueBlocks Go port, Polkascan PolkADAPT and Explorer, and
     six other grants with itemised hours.
   - `maintenance`: software maintenance of a codebase with reported hours, such as the Polkascan
     Python API periods.
   - `INFRA-OPS`, explicitly flagged: RPC, bootnode, and snapshot operations, such as stakeworld.
     These are real reported hours, but they are DevOps work, not software construction. Mixing
     them into a software-effort calibration unflagged would be a category error.
4. **Spans more than one ecosystem and platform**: Polkadot, Kusama, and an Ethereum Foundation
   grant, sourced from GitHub repositories, Medium posts, and governance platforms.

## Honest accounting, so this cannot be challenged later

- These 38 rows are observations across roughly 9 distinct projects and teams, not 38 independent
  projects. The Polkascan rows, PK01 through PK21, are 21 monthly or quarterly slices of one
  ongoing project. They are legitimate as periodic effort observations, but they have to be
  modelled as repeated measures, not treated as 21 independent data points. Doing the latter is
  pseudo-replication, and it would inflate the sample size artificially.
- The TrueBlocks person-months figure is derived, 2 FTE times 12 months, not itemised hours. This
  is flagged as such rather than presented as an equally strong observation.
- The INFRA-OPS rows are real, but excluded from any software-effort modelling. They are kept in
  this file for completeness and transparency, not as usable calibration data.

## How this could scale further

Voluntary actual-effort reports exist across many places: team treasury-report repositories such
as Polkascan and stakeworld, grant retrospectives on Medium such as TrueBlocks and the Ethereum
Foundation, OpenGov referenda and posts on Polkassembly and Subsquare, and programs like Gitcoin
and Optimism RetroPGF. The discovery method is straightforward: enumerate team repositories,
mine governance APIs, and read the underlying post. Each additional team that reports its effort
carefully adds several more verifiable rows. What limited this so far was scope, not the supply
of source material.
