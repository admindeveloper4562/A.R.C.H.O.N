# MIG-004 Verification — 2026-11-18

Candidate base: `784a2a0df18ee4bac461eba76116981dbc514f80`.

This migration uses a read-only compatibility adapter under
`migration/adapters/`. It maps the pinned legacy Core, Backend and Runtime
contracts to existing ARCHON v2 target modules without importing or executing
staged legacy files. `migration/imported/` remains review-only source material.

## Contract map

| Area | Legacy files | v2 boundary |
|---|---:|---:|
| Core | 2 | queue, dispatch and dependency boundaries |
| Backend | 4 | storage, authorization and routing boundaries |
| Runtime | 5 | service, speech, calendar and email boundaries |

The adapter validates every mapped staged-file SHA-256 and size against
`migration/provenance/import-log.json`, parses Python blobs with `ast.parse`
only, and verifies that each v2 target is a regular file. It returns bounded
metadata and no source contents.

## Evidence

- Legacy source remains the approved private reference checkout and is not
  modified.
- Provenance log SHA-256:
  `5ab2f924a7edae5c114c6b0570454d43c2ed746db8db83e5ea37d1e15e835aef`.
- Source pins remain the five commits recorded by MIG-003.
- Temporary-copy rollback/restore check preserved `src/jarvis_v2/core/queue.py`
  from the base with SHA-256
  `384bfbc205cfa60011ab875ffba6b82d91f29819cc8d1987b323d274bcaa82e4`; no
  live database or production resource was touched.
- `tests/test_migration_compatibility.py`: 4 passed.

The task does not claim production cutover, legacy execution, hosted CI, or
native-device acceptance. Those remain separate gates.
