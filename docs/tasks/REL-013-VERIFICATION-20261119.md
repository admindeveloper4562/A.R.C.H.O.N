# REL-013 Verification — recovery, provenance and rollback drills

Status: `LOCAL_EVIDENCE_RECORDED / INDEPENDENT_QC_PENDING`

This candidate exercises the existing bounded recovery controls with disposable
state. It records provenance, verifies a create-only migration dry run and
apply, replays a retained event after SQLite restore, fences a simulated
provider outage and STOP control, and restores a verified last-known-good
artifact. It does not modify `main`, publish code, retire the legacy source,
or switch a production route.

## Pinned identities

| Field | Value |
| --- | --- |
| Task | `REL-013` |
| Source checkpoint recorded by Astra | `43c8db7de8a5f0277a7db23379019d05f2edd2c6` |
| Integration base for this generation | `e2893056a18f3bccb01020c6612add4eb4e4569e` |
| Destination | Disposable Git repository created by the test fixture |
| Legacy source | Disposable Git fixture with the approved legacy-origin pattern |
| Candidate SHA | Bound by the Main Codex handoff and independent QC receipts |
| Protected branches | `main` was not checked out or modified |

The fixture pins a full source commit and records its source blob digest in the
provenance log. No external legacy checkout, credentials, private data, or
network access is required for the drill.

## Acceptance matrix

| Child | Observable evidence | Result |
| --- | --- | --- |
| `REL-013.S01` | Source commit, destination base commit and candidate artifact identities are captured by the test and task handoff. | PASS |
| `REL-013.S02` | Create-only apply records source ref, commit, path, blob SHA-256 and target; fixture contains no private payload. | PASS |
| `REL-013.S03` | Dry run leaves the destination untouched; unsafe traversal is rejected before any write. | PASS |
| `REL-013.S04` | The drill covers STOP fencing, simulated provider outage, duplicate restart admission, corrupted backup and rollback input rejection. | PASS |
| `REL-013.S05` | Backup and restore return `integrity=ok`; retained event replay is delivered once after restore. | PASS |
| `REL-013.S06` | Failed-canary rollback restores the last-known-good artifact while preserving the failed candidate and state checkpoint. | PASS |
| `REL-013.S07` | The tested candidate consists only of the recovery drill and this evidence report; handoff is bound to the exact commit and receipt hashes by Master/QC. | PENDING_QC |

## Reproducible checks

```text
PYTHONPATH=src:. python3 -m unittest discover -s tests -p 'test_rel013_recovery_drills.py'
PYTHONPATH=src:bootstrap/astra-one python3 -m unittest discover -s tests -p 'test_*.py'
PYTHONPATH=bootstrap/astra-one python3 -m unittest discover -s bootstrap/astra-one/tests -p 'test_*.py'
docker run --rm --network=none --read-only --tmpfs /tmp:rw,exec,nosuid,nodev,size=256m \
  --cap-drop=ALL --security-opt=no-new-privileges --user=65534:65534 \
  archon-python:3.12-git-20261119 python3 -m unittest discover -s tests -p 'test_*.py'
```

The focused test performs real file, Git, SQLite, event-bus and rollback
operations in temporary directories. The provider outage uses a failing local
runner at the controller boundary; it records a failed attempt and never
claims that a provider was available. Native macOS/iOS/Xcode or physical
device evidence is outside this task and is not asserted.

## Safety boundary

| Check | Result |
| --- | --- |
| Legacy source writes | None; source remains clean after the dry run and apply |
| Destination writes | Only the allowlisted create-only migration files in disposable state |
| Backup/restore | New destination only; existing artifacts are never overwritten |
| Rollback | Atomic target replacement; failed candidate and state checkpoint preserved |
| Controls | STOP is observed and preserved; recovery never clears it |
| Remote publication | Not attempted |
| Production cutover | Not attempted |

Independent QC must run the exact candidate through the isolated Docker suite,
record child receipts, and pass the serialized Merger before this parent is
considered complete.
