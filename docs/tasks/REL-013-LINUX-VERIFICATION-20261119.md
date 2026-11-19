# REL-013 Linux recovery verification

Status: `LOCAL_SCOPE_VERIFIED / INDEPENDENT_QC_PENDING`

This candidate reuses the recovery, provenance, SQLite restore, STOP fencing,
provider-outage and rollback implementation already present in the reviewed
Git integration. All drills use disposable state; no production route,
protected branch, legacy source or canonical database is modified.

| Field | Value |
| --- | --- |
| Task | `REL-013` |
| Base SHA | `5d1ba5381ae28e733cd0886cd0a70a95a6f9c18e` |
| Existing implementation | `7a521a1` and its descendants in the reviewed integration |
| Candidate SHA | Recorded in the bound Astra Main Codex submission receipt |
| Native macOS/iOS/device evidence | Not required by this task and not claimed |

## Evidence

The focused recovery-drill suite covers source/destination provenance,
create-only migration, dry-run traversal rejection, STOP and provider-outage
fencing, duplicate restart admission, SQLite backup/restore, retained-event
replay and last-known-good rollback. Independent QC must execute the exact
candidate in the no-network Docker lane and bind all seven child receipts to
the candidate SHA.

The prior GitHub implementation report is reference evidence only; this
candidate rebinds the result to the current local integration base and fresh
QC artifacts.
