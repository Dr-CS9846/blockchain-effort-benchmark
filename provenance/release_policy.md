# Release Policy — keeping the "living benchmark" gated

The benchmark re-measures itself from public commits, but a moving pipeline must
never silently change a published claim. This policy keeps the living aspect
**behind gates and tags**, not on an always-mutating mainline.

## Branch & version model

| Ref | Role | Mutability | Citable? |
|-----|------|-----------|----------|
| `main` | The **published** state | Changes ONLY via a reviewed, tagged release | Yes — but cite the tag, not `main` |
| tags `vX.Y` | Frozen, reviewed releases | Immutable | **Yes — the only thing a paper/deck/grant cites** |
| `rolling` | Latest automated CI snapshot | Reset each CI run via `--force-with-lease` | No — explicitly non-authoritative |

- **GitHub Actions writes measurement outputs to `rolling` only.** It never commits to `main`.
- A result becomes part of the published claim only when a human **promotes** it: review → update `canonical_factsheet.md` + `change_log.md` → merge to `main` → tag `vX.Y`.

## Promotion gate (every release)

A `rolling` snapshot may be promoted to a tagged release only if **all** hold:
1. The pipeline reproduces the numbers deterministically (re-run matches).
2. `canonical_factsheet.md` is updated to the new locked numbers, with provenance.
3. `change_log.md` records what changed and why (append-only).
4. Any claim that changed is reflected in the dataset `datasheet` and DOI version.

## Citation rule
Papers, decks, and grant text cite a **tag** (e.g. `v0.1`) and its Zenodo DOI version —
never "latest" or `main`. This guarantees a reviewer always sees the exact state a
claim was made against, even as the benchmark keeps growing.

## Git push conventions
- **Routine work:** plain `git push` (fast-forward only).
- **Intentional reset to a known-good state** (the bootstrap of the complete set; the CI `rolling` snapshot): `git fetch` first, then `git push --force-with-lease` — it refuses if the remote moved unexpectedly since the fetch.
- **Never** plain `git push --force` — it can silently clobber commits.

## Why
A living benchmark that ages forward is powerful; an ungoverned one drifts from
evidence into maintenance burden and can invalidate a published claim without a
versioned release. Gates + tags give the upside (freshness, reproducibility) without
the downside (claim drift).
