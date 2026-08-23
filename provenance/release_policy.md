# Release policy: keeping the living benchmark gated

The benchmark re-measures itself from public commits, but a moving pipeline must never silently
change a published claim. This policy keeps the living, self-updating part of the project behind
gates and tags, not on an always-mutating mainline.

## Branch and version model

| Ref | Role | Mutability | Citable? |
|-----|------|-----------|----------|
| `main` | The published state | Changes only through a reviewed, tagged release | Yes, but cite the tag, not `main` |
| tags `vX.Y` | Frozen, reviewed releases | Immutable | Yes, the only thing a paper, deck, or grant should cite |
| `census` | Automated CI measurement artifacts | Machine-written on every CI run | No, explicitly non-authoritative |

- GitHub Actions writes measurement outputs to `census` only. It never commits to `main`.
- A result becomes part of the published claim only when a human promotes it: review the
  result, update `canonical_factsheet.md` and `change_log.md`, merge to `main`, then tag `vX.Y`.

## Promotion gate, every release

A `census` snapshot may be promoted to a tagged release only if all of the following hold.

1. The pipeline reproduces the numbers deterministically; a re-run matches.
2. `canonical_factsheet.md` is updated to the new locked numbers, with provenance.
3. `change_log.md` records what changed and why, as an append-only entry.
4. Any claim that changed is reflected in the dataset's datasheet and its DOI version.

## Citation rule

Papers, decks, and grant text cite a tag (for example `v0.1`) and its Zenodo DOI version, never
"latest" or `main`. This guarantees a reviewer always sees the exact state a claim was made
against, even as the benchmark keeps growing after that point.

## Git push conventions

- Routine work: a plain `git push`, fast-forward only.
- An intentional reset to a known-good state, such as the bootstrap of the complete set or a CI
  `census` snapshot: `git fetch` first, then `git push --force-with-lease`, which refuses if the
  remote moved unexpectedly since the fetch.
- Never a plain `git push --force`. It can silently overwrite commits.

## Why this exists

A living benchmark that keeps growing is useful, but an ungoverned one drifts away from its own
evidence and can invalidate a published claim without a versioned release to point to. Gates and
tags keep the upside, freshness and reproducibility, without the downside of a claim quietly
drifting out from under a citation.
