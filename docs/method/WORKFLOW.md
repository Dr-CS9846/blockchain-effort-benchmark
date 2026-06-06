# Measurement Workflow — Real, Reproducible Size→Effort Benchmark

**Purpose.** Replace the circular `PM = f(FTE, Cost)` setup with the genuine COCOMO core — **effort predicted from independently‑measured size** — using only quantities that trace to a public commit. Runs as a **13‑project pilot** and scales **unchanged to 150+** by growing one CSV.

**Scientific contract (read once).**
- **Size (independent variable):** measured KSLOC via `cloc` on the *delivered commit*.
- **Effort (dependent variable):** measured **active person‑months** from `git log` authorship; *planned* `FTE × duration` kept only as a labelled cross‑check.
- **Every row is reproducible** from `(repo_url, resolved_commit, cloc version, git version, query window)`. Nothing enters the benchmark that cannot be re‑derived from a pinned commit.
- **Estimator is deterministic** (closed‑form log‑space MLE = lognormal MLE). No seeds, identical re‑runs.

---

## 0. Prerequisites

```bash
# System tools
git --version            # any recent git
cloc --version           # https://github.com/AlDanial/cloc  (brew install cloc | apt install cloc | choco install cloc)

# Python
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt                      # numpy only
```

Files in this folder:

| File | Role |
|------|------|
| `projects_manifest.csv` | **The scalable input.** One row per project. Grow this 13 → 150. |
| `resolve_repos.py` | Step 1 — suggests delivered‑repo URLs from local application/delivery `.md`. |
| `measure_repos.py` | Step 2 — measures KSLOC + active person‑months → `measurements.csv`. |
| `calibrate_size_effort.py` | Step 3 — fits `PM = A·KSLOC^E`, LOOCV, planned‑vs‑measured check. |
| `WORKFLOW.md` | This runbook. |

---

## 1. Resolve repositories and complete the manifest

The manifest ships pre‑seeded with the **real planned values** (FTE, duration, planned PM, cost) for the 13 verified projects. You must add, per row, **where the code lives** and **which commit to measure**.

```bash
python resolve_repos.py \
  --apps  ../01_raw_applications/Grants-Program/applications \
  --deliv ../02_raw_deliveries/Grant-Milestone-Delivery/deliveries
# -> repo_candidates.csv  +  projects_manifest.suggested.csv (review, then copy good rows in)
```

Fill these columns in `projects_manifest.csv`:

- `repo_url` — the team's delivered GitHub repo (not the W3F grants repo).
- **one of** `commit_sha` (exact delivered commit — best) **or** `cutoff_date` (`YYYY-MM-DD` of the final milestone acceptance — the script resolves it to the unique commit at/just before that date).
- `since_date` *(optional)* — development start, to bound the effort window.
- `subdir` *(optional)* — path within a monorepo (measures only that module).

> **Traceability rule:** prefer `commit_sha`. Use `cutoff_date` only when a SHA is not recoverable; it still resolves deterministically. Record the milestone‑delivery PR URL in `notes`.

---

## 2. Measure size and effort

```bash
python measure_repos.py                 # all rows, sequential, resumable
# options:
python measure_repos.py --only AdMeta,Roloi      # subset while you test
python measure_repos.py --jobs 4                 # parallel across repos (safe)
python measure_repos.py --min-commits-per-month 2  # stricter "active month" threshold
python measure_repos.py --force                  # re-measure everything
```

Outputs:
- `measurements.csv` — `ksloc_code`, `ksloc_all`, `active_person_months`, `total_commits`, `distinct_authors`, `resolved_commit`, planned fields, `status`.
- `measurement_provenance.json` — tool versions + parameters (the reproducibility stamp).

The script **clones into `repo_cache/`, checks out the resolved commit, runs `cloc` (code languages only, excluding vendored/build/test dirs), and counts distinct `(author, month)` pairs** (merge commits and bot accounts excluded; `.mailmap` respected). It is **row‑independent and resumable** — already‑measured `OK` rows are skipped on re‑run.

---

## 3. Calibrate the size→effort core

```bash
# Primary: effort = MEASURED active person-months
python calibrate_size_effort.py --effort measured --size ksloc_code

# Reference: effort = PLANNED FTE x duration (your old target)
python calibrate_size_effort.py --effort planned  --size ksloc_code
```

Outputs `size_effort_params.json` (A, E, σ, Duan) and `size_effort_results.json` (in‑sample + LOOCV MMRE / PRED(25)/(30), Conte verdict, and `corr(planned, measured PM)`).

---

## 4. Interpret — the decision gate

Read three things from the report:

1. **Does size predict effort?** Look at **LOOCV MMRE / PRED(25)** and the **Conte (1986)** verdict (`MMRE < 25% AND PRED(25) ≥ 75%`).
2. **Is the effort target sound?** Look at **`corr(planned, measured PM)`**. High correlation ⇒ planned `FTE×duration` is validated by independent git evidence and the *planned‑vs‑actual* objection is retired. Low correlation ⇒ an important, publishable finding about how grant plans diverge from delivered work.
3. **Is the exponent sane?** `E` near the COCOMO range (~0.9–1.2) is reassuring; wildly off suggests size mis‑measurement (check `top_langs`, `subdir`, test exclusion).

**Gate:**
- **Core holds** (or is close) → proceed to layer the 7 blockchain effort multipliers + 5 scale factors, then expand to 150.
- **Core fails even with measured size** → that is itself a legitimate result; pivot the thesis emphasis to the *dataset + pipeline* contribution and the honest characterisation of blockchain‑effort predictability.

Either outcome is real, reproducible, and defensible — which is the whole point.

---

## 5. Scaling 13 → 150 (no code changes)

The pipeline was built to scale by **data, not code**:

- **Grow the manifest.** Append rows (same columns) from the full W3F set and template‑fork ecosystems (Moonbeam, etc.). The feasibility memo establishes ≥30 verified projects are reachable; 150 is the target.
- **Throughput.** Use `--jobs 4..8`; `repo_cache/` is reused across runs so re‑measurement is cheap. For very large batches, **shard** the manifest (`split`), run shards on separate machines/CI, then concatenate `measurements.csv` files.
- **Resumability.** Re‑running continues where it stopped; only `ERROR`/new rows are recomputed.
- **Determinism at scale.** Because each row pins a commit, a 150‑row run is as reproducible as a 13‑row run.
- **Rate limits.** Cloning is plain `git` (no API token needed). If you later resolve commits via the GitHub API, add a token and back‑off; measurement itself needs none.

---

## 6. Quality controls & pitfalls (do not skip)

- **Monorepos:** set `subdir` so you measure the funded module, not the whole org repo.
- **Squashed/rewritten history** understates effort — note it; prefer repos with real history, or measure the development fork.
- **Generated/vendored code** inflates size — the default `--exclude-dir` list handles common cases; extend it if `top_langs` shows noise.
- **Author aliasing:** add a `.mailmap` to a repo to merge one person's multiple emails (git applies it automatically).
- **Bot noise:** filtered by default (`[bot]`, `github-actions`, `dependabot`, `renovate`, `noreply`).
- **Language scope:** `ksloc_code` counts blockchain/code languages only; `ksloc_all` is every code language. Decide once and keep it fixed across the whole dataset.

---

## 7. Publishability & traceability

- Commit `projects_manifest.csv`, `measurements.csv`, `measurement_provenance.json`, and all scripts to a public repo.
- Release the dataset with a **Zenodo DOI** + a one‑page **datasheet** (sources, definitions, exclusions, known limits). This is the "PROMISE/ISBSG for blockchain" artifact.
- Because every figure traces to a pinned commit and a named tool version, a reviewer can reproduce the entire benchmark from scratch.

---

## 8. Running this with Claude in VS Code

Give Claude this folder and these instructions:

> Read `WORKFLOW.md`. Verify `git` and `cloc` are installed. Run `resolve_repos.py`, then open `repo_candidates.csv` and help me confirm each `repo_url` and a `commit_sha` or `cutoff_date` in `projects_manifest.csv` (cross‑check against the milestone‑delivery PRs). Then run `measure_repos.py`, inspect `measurements.csv` for any `ERROR`/`SKIP` rows and fix their manifest entries, and re‑run until all 13 are `OK`. Then run `calibrate_size_effort.py` for both `--effort measured` and `--effort planned`, and summarise the LOOCV MMRE/PRED(25), the Conte verdict, and `corr(planned, measured)`. Do not edit any measured number by hand; if something looks wrong, fix the manifest or the exclusion settings and re‑measure.

Claude should **never** hand‑enter results — only resolve inputs, run scripts, and read the JSON/CSV outputs.
