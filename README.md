# Blockchain Effort Benchmark

This project answers one question: **how much developer effort does it take to build a blockchain software project, and can we estimate it before the work starts?**

It does that by measuring real, completed Web3 Foundation grant projects — how big the delivered code is, and how much development actually went into it — and using those measurements to calibrate a COCOMO-style effort model.

It is part of the PhD research *"Proof of Effort — A Blockchain-Aware Extension of COCOMO II."*

---

## What this is, and what it is NOT

**This IS** an *effort-estimation* project. "Benchmark" here means a **labelled dataset** used to calibrate and test cost-estimation models — the same sense as the PROMISE software-engineering datasets. It measures two things from each project's public Git repository:

- **Size** — lines of code in the delivered software (`cloc`).
- **Effort** — months of actual development activity (`git` history).

**This is NOT** a performance benchmark. There is **no** throughput/TPS measurement, no transaction load testing, no relayers, no stress-test harness, and no node-performance tooling anywhere in this repo. Performance-benchmark suites like Blockbench or TrustedBench measure how *fast a blockchain runs* — a completely different question — and appear here only as cited related work, never as data.

If you remember one thing: **this measures the effort to *build* the software, not the speed of the *running* blockchain.**

---

## How it works

For each completed grant project, an automated, repeatable pipeline:

1. Finds the delivered code repository and the exact commit that was accepted.
2. Measures its **size** (KSLOC) with `cloc`.
3. Measures the **effort** that went into it (active developer-months from the Git history).
4. Fits and tests a simple estimation model: `Effort = A × Size^E`.

Every number traces back to a public commit. Nothing is typed in by hand.

## Run it yourself

```bash
make quickcheck   # reproduce the headline result + figures (needs Python + numpy only)
make all          # the whole pipeline end-to-end (also needs git + cloc)
make verify       # re-run and confirm the numbers match exactly
```

No `make`? Use `bash run_all.sh`. The same pipeline also runs automatically on GitHub Actions and publishes fresh results to a separate `rolling` branch — the published `main` only changes through a reviewed, tagged release (see `provenance/release_policy.md`).

## Where things live

```
data/calibration/   the project data + the measurements
data/raw/           frozen, hash-stamped copies of the original public sources
scripts/extract/    find repos, measure size + effort, freeze sources
scripts/validate/   environment check + the calibration/estimation model
reports/            results and figures
provenance/         source map, fact sheet, change log, release policy, claims ledger
docs/               method, limitations, and the dataset datasheet
```

## Honest status

This is an early-stage corpus. The pipeline runs end-to-end and has produced its first real, commit-traced measurements, but only a few projects are measured so far and the model is not yet calibrated on enough points to draw conclusions. Results and limitations are reported as they are — see `provenance/claims_ledger.md` and `docs/limitations/`.

## License
Code: MIT. Data is derived from public Web3 Foundation grant repositories.
