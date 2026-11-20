# REL-015 in-scope backup/restore verification

Status: `LOCAL_SCOPE_VERIFIED / INDEPENDENT_QC_PENDING`

This candidate reuses the reviewed clean-room backup/restore, migration,
storage, event-bus and recovery implementation. It tests only disposable
destinations and synthetic records; the canonical database, production state,
legacy source and protected branches are untouched. TWS/iOS artifacts remain
excluded under the existing scope amendment.

| Field | Value |
| --- | --- |
| Task | `REL-015` |
| Base SHA | `96ecf922652471786436875f1e13725c36367265` |
| Scope amendment | `ARCHON-TWS-OUT-OF-SCOPE-20261119` |
| Candidate SHA | Recorded in the bound Astra Main Codex submission receipt |

## Evidence

The focused checks cover SQLite backup API use, clean-room restoration,
schema/data binding, WAL-visible state, provenance, source immutability,
corruption/digest rejection, event replay and recovery behavior. All outputs
are digest/metadata-only. Independent QC must execute the exact candidate in
the no-network Docker lane and bind all seven child receipts to its SHA.
