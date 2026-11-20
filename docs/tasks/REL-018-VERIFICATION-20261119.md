# REL-018 Verification — non-TWS user acceptance and accessibility boundary

Status: `OWNER_APPROVED / LOCAL_EVIDENCE_RECORDED / CANDIDATE_PENDING_QC`

This report records the owner-approved non-TWS acceptance scope. It does not
claim TWS, iOS, native macOS, Windows-host, or production deployment evidence.

## Identity and owner gate

| Field | Value |
| --- | --- |
| Task | `REL-018` |
| Integration base SHA | `0bcd0678da94f4c8d2a5fb3ed4bde0c81d7dfe37` |
| Builder branch | `feature/astra-rel-018-a1-bc224732` |
| Builder run | `bc224732-90be-4ae7-a97a-b68107d9fb51` |
| Parent payload SHA | `9d1029b8efd1bdada0993b8cc9421cb08fa3ffa22cb19c40176c65ee53fdd72c` |
| Owner decision | `APPROVE` |
| Owner receipt SHA-256 | `60fa0a622835b4d8efdabee223dcfcb71c742be5c05d1e28eb1fd420bb4672dd` |
| Owner signer | `owner` / `ssh-ed25519` |
| Scope amendment | `ARCHON-TWS-OUT-OF-SCOPE-20261119` |

## Scripted non-TWS journeys

The following objective local checks exercise the accepted non-TWS contracts:

| Journey area | Evidence |
| --- | --- |
| Core queue, session, event and control behavior | Root suite, including core queue/replay, sessions, event guards and controls |
| Backend authorization, storage, backup, event bus and provider policy | Root suite, including backend acceptance and storage/backup checks |
| Guardian stop, isolation, restart, rollback and release boundaries | Root suite, including Guardian recovery, fencing, isolation and rollback checks |
| WIC provenance, summaries, alerts and source verification | Root suite, including WIC source, summary, alert and verification checks |
| Finance read-only, paper-only and consent boundaries | Root suite, including finance acceptance, paper, Mira audit and reconciliation checks |
| Installation and controller safety | Foundation and installation-manifest validators |

## Local evidence

| Check | Result |
| --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -q` | exit 0; 568 tests; `OK` |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 tools/verify_foundation.py` | exit 0; ten-module validation passed |
| `PYTHONDONTWRITEBYTECODE=1 python3 infra/verify_installation.py --json` | exit 0; manifest status `ok` |

The root suite emits the repository's existing single-snapshot `--json`
diagnostic while still exiting zero; no remote workflow was triggered.

## Accessibility and platform boundary

The in-scope Linux acceptance has no native TWS/iOS UI surface. The audit
therefore verifies safe interaction boundaries, explicit deferred platform
states, and rejection of unclaimed native journeys. It is not a native
screen-reader, SwiftUI, macOS, iOS, or Windows-host certification.

TWS/iOS work remains deferred and unclaimed. Windows/macOS transfer evidence
remains `NEEDS_VERIFY` under the applicable Linux-first amendments.

## Gate result

The owner decision is cryptographically verified and bound to the current
parent payload and integration SHA. The candidate is ready for independent QC;
no production deployment, remote queue, native-device operation, or protected
branch change was performed.

Required handoff line:

`REL-018 | start SHA 0bcd0678da94f4c8d2a5fb3ed4bde0c81d7dfe37 | branch feature/astra-rel-018-a1-bc224732 | changed files docs/tasks/REL-018-VERIFICATION-20261119.md | checks root suite 568 tests, foundation validator, installation manifest validator, signed owner receipt | evidence this report and owner receipt | state OWNER_APPROVED/LOCAL_EVIDENCE_RECORDED/CANDIDATE_PENDING_QC | blockers TWS/iOS/native platform evidence deferred and unclaimed`
