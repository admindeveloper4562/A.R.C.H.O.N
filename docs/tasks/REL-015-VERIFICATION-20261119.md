# REL-015 — in-scope backup/restore and data-retention verification

Status: `LOCAL_EVIDENCE_RECORDED / INDEPENDENT_QC_PENDING`

This candidate validates the existing bounded Backend backup/restore path in a
clean-room disposable destination. It does not modify the canonical database,
production state, `main`, the legacy source, or any TWS artifact. The TWS/iOS
scope amendment is an explicit residual-risk boundary for this release.

## Pinned identities

| Field | Value |
| --- | --- |
| Task | `REL-015` |
| Task payload SHA-256 | `2c430a79f33cb0a43cc68b2f4ed3dd0184a21de2c38e5b64905a32902142755d` |
| Start/integration SHA | `a0d706a8ed223dd1223016c992360312c788282d` |
| Source branch/SHA | `develop` / `f1ffcdd3c1cb76b805cc768e446385fcd67ea850` |
| Task-plan SHA-256 | `10cb1ed53eace6af1c5d052ef0ad0a85eaf9f535db5ae0be794cc7d12752b154` |
| Scope amendment | `ARCHON-TWS-OUT-OF-SCOPE-20261119` |
| Scope amendment SHA-256 | `ec8eb9d28adb55828eb68aba94f1ef5b9137c0792a8c62a495d61bf754d3bef4` |
| Candidate branch | `feature/astra-rel-015-a1-7506132b` |
| Candidate SHA | pending Main Codex handoff |
| Protected branches | `main` was not checked out or modified |

## Acceptance matrix

| Child | Result | Evidence |
| --- | --- | --- |
| `REL-015.S01` | PASS | The attempt is bound to the source `develop` SHA, start/integration SHA, task-plan SHA and current task payload SHA above. The destination is a temporary clean-room fixture. |
| `REL-015.S02` | PASS | Reviewed `src/jarvis_v2/backend/backup.py`, `src/jarvis_v2/backend/storage.py`, `src/jarvis_v2/backend/event_bus.py` and `src/jarvis_v2/automation/recovery_drill.py`; migration/provenance tests preserve source commits and reject unsafe or incomplete imports. |
| `REL-015.S03` | PASS | The backup/restore drill writes only to a temporary destination, leaves the source state digest unchanged, rejects an incorrect backup digest, and uses no live or personal data. |
| `REL-015.S04` | PASS | The existing bounded implementation uses the SQLite backup API, exclusive destination creation, owner-only `0600` artifacts, schema binding and an explicit cipher boundary. No canonical or production destination was changed. |
| `REL-015.S05` | PASS | Backup, migration, private-data-boundary, storage, event-bus, queue-session and recovery tests all passed; receipt output is digest/metadata-only. |
| `REL-015.S06` | PASS | The clean-room restore returned SQLite integrity `ok`, preserved the synthetic domain row and WAL-visible state, and corruption/digest-fence tests rejected unsafe restores without creating a destination. |
| `REL-015.S07` | PENDING_QC | This report is the bounded handoff artifact. Independent QC must review the exact candidate SHA and the serialized Merger must bind the final integration SHA. |

## Reproducible checks

```text
PYTHONPATH=src:bootstrap/astra-one python3 -m unittest -q \
  tests.test_backend_backup tests.test_rel013_recovery_drills \
  tests.test_migration_guardrails tests.test_migration_compatibility \
  tests.test_acceptance_evidence tests.test_backend_storage \
  tests.test_backend_event_bus tests.test_core_queue_replay \
  tests.test_core_sessions
Ran 40 tests — OK (exit 0)

PYTHONPATH=src:bootstrap/astra-one python3 -m unittest discover -s tests -q
Ran 561 tests — OK (exit 0)
```

The full suite emits the repository's expected read-only monitor argparse
diagnostic while exercising that entry point; the command still exits zero.
No hosted workflow, external provider, credential store, live user data,
Cloudflare resource, iOS device or TWS implementation was accessed.

The independent disposable drill returned only these bounded observations:

```text
backup_integrity=ok
restore_integrity=ok
schema_version=12
source_state_unchanged=true
restored_rows=1
backup_mode=0600
receipt_digest_only=true
backup_sha256=1c8d7d9c02933bd5ac47f8b54762ce7c93551fa96726e2f0549f51c6fcaa5085
restored_sha256=1c8d7d9c02933bd5ac47f8b54762ce7c93551fa96726e2f0549f51c6fcaa5085
source_state_sha256=e4609d6c18ee2c885631baa2f7ac443d03a34c7046d27f69657166ed4862b683
```

## Retention and release boundary

The evidence proves that this candidate does not add raw private values to
backup/restore receipts or public task evidence, and that the restored
in-scope state remains isolated in a new destination. Domain data remains
owned by its module; this candidate does not invent a deletion window or purge
private records without an owner-approved retention policy. Hosted retention
and any TWS/iOS state remain outside this release and are not claimed complete.

The candidate performs no production cutover, no main promotion, no source
retirement and no TWS work. Independent QC and serialized merge remain
required before REL-015 can transition to verified completion.

## Required handoff line

`REL-015 | child_receipts pending Master registration | start_sha a0d706a8ed223dd1223016c992360312c788282d | candidate_sha pending | integration_sha a0d706a8ed223dd1223016c992360312c788282d | branch feature/astra-rel-015-a1-7506132b | files docs/tasks/REL-015-VERIFICATION-20261119.md | test_evidence 40 focused tests + 561 full local tests + disposable clean-room backup/restore drill | independent_qc pending | merger_result pending | runtime_lane normal/main_builder | retries 0 | blockers independent QC and serialized merge; no owner-approved hosted retention window supplied`
