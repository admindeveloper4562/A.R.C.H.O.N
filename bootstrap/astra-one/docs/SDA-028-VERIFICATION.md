# SDA-028 Verification — Existing ARCHON Repository and Controlled Policy

Status: `LOCAL_EVIDENCE_RECORDED / REMOTE_PROTECTION_UNVERIFIED`

This candidate verifies the existing ARCHON repository and its local migration
guardrails. It does not create a second repository, write to GitHub, apply
legacy source files, promote `main`, or retire the legacy reference checkout.
The deterministic Master remains the authority for task state and completion.

## Identity and scope

| Field | Observed value |
| --- | --- |
| Task | `SDA-028` |
| Execution mode | `migration` |
| Source repository | `admindeveloper4562/A.R.C.H.O.N` |
| Source/develop SHA | `43c8db7de8a5f0277a7db23379019d05f2edd2c6` |
| Destination base SHA | `a0e72fcab0b2e5167b40d545e87a53e05594ae2f` |
| Destination checkout | `integration-reconciled-20261114` |
| Candidate branch | `feat/sda/SDA-028-implementation-a1-47ec7bff` |
| Protected main reference | `5227b91d2725bf4be4336a5ad26189fdf1034704` |
| Remote develop reference | `43c8db7de8a5f0277a7db23379019d05f2edd2c6` |
| Parent/child plan | `247` parents; `1,359` children |
| Hosted CI | Not invoked; hosted quota remains deferred |
| Production/main promotion | Not attempted |

The destination is the existing ARCHON repository requested by the owner. The
legacy `personal-jarvis` checkout was not modified; its pre-existing dirty
state was preserved. No duplicate repository was created.

## S01 — source and destination pin

The candidate source checkout and its `origin/develop` both resolve to
`43c8db7de8a5f0277a7db23379019d05f2edd2c6`. The isolated task worktree was
claimed by the Master from destination base
`a0e72fcab0b2e5167b40d545e87a53e05594ae2f`. The root ARCHON `main` and
`origin/main` remain at `5227b91d2725bf4be4336a5ad26189fdf1034704`.

## S02 — inventory and provenance

The destination contains `199` tracked files. The bounded filename inventory
found no tracked database, environment, secret, credential, checkpoint, raw
conversation or raw-prompt paths, and no case-folding collisions. The tracked
CI workflow is `.github/workflows/ci.yml` with SHA-256
`dbcc492abf3ca6c6e3cdcf49900616d09891b343027c63ba9b55dfe46df8ec79`.

The legacy manifest contains `23` create-only candidate entries. A disposable
clone fetched the five referenced remote heads and ran the existing
`tools/import_legacy.py` dry-run. The importer recorded per-entry source ref,
source commit, source path, blob SHA, content SHA, size and staged-unreviewed
status. No destination write or execution occurred. The observed remote heads
were:

| Source ref | Source commit | Entries |
| --- | --- | ---: |
| `develop` | `58ab827a0dfe7e884ca9dbe2cc368459e8e82470` | 12 |
| `feature/jarvis-v2-expanded-architecture-20261113` | `14080d9a897494b17fad89dd6a02f942348d1fb2` | 3 |
| `feature/workhorse-context-engine-4way-20261109` | `4f37407ec177c30f9efaee2746c0b454a63931e2` | 1 |
| `feature/twelve-winged-m001` | `351f713db748afa542806819e6ed27e4b715be22` | 4 |
| `feature/cloudflare-overnight-inference-coordinator-20261112` | `8ba98707b2bffb3a04c49b3022db983239a267e6` | 3 |

Those entries remain staged-unreviewed only. They were not imported because
this task's approved scope is the existing ARCHON repository and policy; the
legacy repository remains reference material. The source checkout has no root
`LICENSE` or `NOTICE` path in its pinned tree, so no license claim is inferred
for unimported legacy candidates.

## S03 — read-only dry run

The existing importer was run without `--apply` against a disposable clone.
It returned `dry_run=true` and `count=23`. The real legacy checkout was not
used as a write target and its dirty files remained untouched. The importer
rejects traversal, symlink, case-only collision, non-blob, oversized and
non-create-only entries; its focused tests cover those boundaries.

## S04 — bounded destination change

The only destination changes in this candidate are this verification record
and the package-manifest hashes required to make the already tracked
`SDA-027-VERIFICATION.md` and this record verifiable. No legacy file was
copied, deleted, overwritten, executed or renamed. The local branch/commit
policy, CODEOWNERS and fast-forward-only serialized Merger remain the
repository controls for `main` and `develop`.

## S05 — verification result

| Command/check | Result |
| --- | --- |
| ARCHON root unit suite | PASS — 85 tests |
| Astra One suite | PASS — 168 tests |
| Legacy importer tests | PASS — 2 tests |
| Migration guardrail tests | PASS — 4 tests |
| Git branch/commit policy | PASS |
| Dependency scan | PASS |
| Secret scan | PASS |
| Workflow security scan | PASS |
| Candidate `git diff --check` | PASS |
| Tracked sensitive-name inventory | PASS — no matches |
| Case-folding collision inventory | PASS — no collisions |
| Clean-tree Astra package manifest check | Bound to the final candidate |

GitHub identifies the repository as private with default branch `main`. The
GitHub branch-protection endpoint returned HTTP 403 because the current plan
does not expose that API. Therefore remote enforcement is explicitly
`UNVERIFIED_EXTERNAL`; this candidate does not claim that GitHub protection is
enabled. Local branch/commit policy evidence is present and independently
testable.

## S06 — rollback and restore

Checkpoint:
`/home/r34p3r/.local/state/archon-astra/checkpoints/pre-sda028-claim-20261116T155828Z/`

The checkpoint database SHA-256 is
`c8cbcf42ec2fca4cd504738dd95fa90a9c5438ef10e5f355735ebcc74bb1a6f4`.
SQLite backup/restore was exercised to a disposable database using the SQLite
backup API. The restored copy passed `PRAGMA integrity_check` and retained
`247` project parents and `1,359` project children. The canonical database and
integration checkout were not replaced.

## S07 — handoff

This candidate is a real Git commit submitted through the deterministic Master
with the exact changed-file list, source/base SHA, bounded test evidence and
child evidence. Independent Docker QC and the serialized Merger must bind
their receipts to the final candidate SHA. Only the Master may record child
receipts or mark the parent verified complete.

## Open boundary

The local repository policy is verified. The GitHub-plan limitation prevents
independent observation of remote branch-protection settings; no claim is
made beyond that fact. Hosted CI was not run because the project policy
defers exhausted remote quota. These are recorded limitations, not silently
converted into passes or used to authorize a release.
