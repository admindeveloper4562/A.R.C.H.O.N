# SDA-001 Astra One v0.2.0 provenance recovery

Task: `SDA-001`
Generation: `2`
Source commit: `5227b91d2725bf4be4336a5ad26189fdf1034704`
Candidate base: `b2fb308501bad992ecdb84baac313fae812d0f7f`
Branch: `recovery/sda/SDA-001-provenance-recovery-g2`

## Result

The exact Astra One Linux v0.2.0 source is verified from the immutable ARCHON
Git commit and staged as a review-only candidate under
`migration/imported/sda/astra-one-v0.2.0/`. The current Astra One v0.3.0
runtime under `bootstrap/astra-one/` is unchanged. This candidate is not a
runtime install, native SDA cutover, task completion, or production release.

## Evidence

- Recovered staging directory:
  `/home/r34p3r/.local/state/archon-astra/provenance/SDA-001/git-v0.2.0-digQmVpl/`.
- Commit object type and resolution: `commit`, exact SHA
  `5227b91d2725bf4be4336a5ad26189fdf1034704`.
- `VERSION` and `MANIFEST.json` both report `0.2.0`.
- All 32 manifest file hashes match the recovered staging files and the Git
  blobs at `5227b91:bootstrap/astra-one/<path>`.
- The Git tree contains those 32 manifest files plus the expected
  `MANIFEST.json` metadata file. Nine pre-existing `.pyc` files in the staging
  directory are excluded from the candidate and were not deleted.
- Historical Python suite: `PYTHONDONTWRITEBYTECODE=1 python3 -B -m
  unittest discover -s tests -p 'test_*.py' -q`; `Ran 49 tests in 7.500s`,
  `OK`.
- High-confidence credential-pattern scan found no embedded secrets; matches
  were documentation placeholders and environment-variable names. License
  classification remains `unclassified_requires_legal_review`.

## Compatibility comparison

The current base is Astra One v0.3.0. Compared with the v0.2.0 manifest:

- 23 common manifest files are hash-identical.
- 9 common files changed: `README.md`, `VERSION`,
  `astra_one/linux_cli.py`, `astra_one/linux_runtime.py`,
  `astra_one/linux_sda.py`, `cloudflare/astra-one-monitor/tsconfig.json`,
  `docs/LINUX_FULL_SDA.md`, `docs/LINUX_RELEASE_NOTES.md`, and
  `tests/test_linux_sda.py`.
- 4 files are additive in v0.3.0: `astra_one/full_plan.py`,
  `astra_one/supervisor.py`, `tests/test_full_plan.py`, and
  `tests/test_supervisor_v3.py`.
- No file under `bootstrap/astra-one/` is downgraded or overwritten by this
  candidate.

## Isolated migration dry run

The planned destination was absent before the dry run. The read-only plan had
33 entries: the 32 manifest files plus `MANIFEST.json`. It found zero unsafe
paths, zero case-fold collisions, zero symlinks, and zero existing destination
collisions; it performed zero writes. The apply step copied only those 33
regular files and excluded the staging directory's generated `.pyc` artifacts.

## Rollback and review boundary

Rollback target is the candidate base SHA above. The rollback probe must verify
that the v0.3.0 runtime remains available at that SHA and that restoring the
candidate commit reproduces the imported package hashes. The candidate remains
review-only until independent QC and the serialized Merger bind their receipts
to the final candidate SHA. No canonical SQLite transaction or task-status
transition is performed by this preparation step.

Required handoff receipt fields:

`SDA-001 | child_receipts pending Master registration | start_sha b2fb308501bad992ecdb84baac313fae812d0f7f | candidate_sha pending commit | integration_sha pending Merger | branch recovery/sda/SDA-001-provenance-recovery-g2 | files migration/imported/sda/astra-one-v0.2.0/**, migration/provenance/SDA-001-astra-one-v0.2.0.json, docs/tasks/SDA-001-PROVENANCE-RECOVERY-20261115.md | test_evidence 32 manifest hashes + 49 historical Python tests + dry-run | independent_qc pending | merger_result pending | runtime_lane recovery | retries 1 prior generation, current generation 2 | blockers license review, independent QC, serialized merge and deterministic Master reconciliation`
