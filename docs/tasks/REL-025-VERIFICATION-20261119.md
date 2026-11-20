# REL-025 verification — final v2 acceptance and maintenance roadmap

Status: `LOCAL_EVIDENCE_RECORDED / CANDIDATE_PENDING_QC`

This report is a truthful project checkpoint, not a release or production
promotion. It records the current Linux-first state, the GitHub Free residual
risk, the deferred native-platform scope and the remaining work.

## Pinned identities

| Field | Value |
| --- | --- |
| Task | `REL-025` |
| Run | `e0bbab31-8e1c-4aeb-9b41-32af2e475d22` |
| Attempt | `1` |
| Integration base SHA | `dd61427d1eadd407eb9a57468bfdbd70e68e4a92` |
| Source reference | `75582dbf48057e3d5b0e7cf4acfdba2386acfcff` |
| Branch | `feature/astra-rel-025-a1-e0bbab31` |
| Parent payload SHA | `a24310d85c3e00a560ce703be884f43800c6cf0270d8cad2941e09e71aae93b6` |

## Project state at this checkpoint

| Measure | Recorded value |
| --- | ---: |
| Project parents verified complete | 239 / 247 |
| Project parents archived under approved scope | 7 |
| Active REL-025 candidate | 1 |
| Project child records | 1,359 |
| Verified child receipts before this candidate | 1,276 |
| SQLite integrity | `ok` |
| STOP / PAUSE / quota | clear |
| Integration base | `dd61427d1eadd407eb9a57468bfdbd70e68e4a92` |

The seven archived parents are `REL-009` and `TWS-013`, `TWS-014`, `TWS-015`,
`TWS-016`, `TWS-019`, and `TWS-020`, all recorded as `scope_deferred_tws` by
the approved out-of-scope amendment. They are not counted as completed.

## Acceptance matrix

| Requirement | Result | Boundary |
| --- | --- | --- |
| Version and artifacts | PASS locally | Current source, integration and candidate identities are SHA-pinned |
| Tests and foundation | PASS locally | 568 ARCHON tests, 112 Astra tests, ten-module foundation and installation checks passed |
| Host verification | Linux verified | Windows/macOS/native TWS evidence remains deferred and unclaimed |
| GitHub branch enforcement | `DEFERRED_PLAN` | Private GitHub Free returned HTTP 403; local policy is not represented as server enforcement |
| Legacy/Business boundary | PASS locally | Legacy source remains recoverable reference material; Business has no active service |
| Release publication | Not performed | No `main` change, remote tag, production deployment or native SDA cutover |

## Reproducible checks

```text
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -q
  exit 0; 568 tests; OK
PYTHONPATH=src python3 tools/verify_foundation.py
  exit 0; ten-module foundation validation passed
PYTHONPATH=src python3 infra/verify_installation.py --json
  exit 0; installation status ok
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=bootstrap/astra-one python3 -m unittest discover -s bootstrap/astra-one/tests -p 'test_linux_sda.py' -q
  exit 0; 112 tests; OK
```

The native-platform and hosted-enforcement limitations are explicitly recorded
as deferred rather than converted into local passes. The maintenance path is to
retain the deterministic Master, independent QC, serialized Merger, rollback
checkpoints and the seven deferred-scope records until the relevant external
evidence becomes available.

## Child evidence map

| Child | Evidence | Result |
| --- | --- | --- |
| REL-025.S01 | This report maps each acceptance clause to an observed result or explicit deferred boundary. | PASS locally |
| REL-025.S02 | Sanitized source, dependency, platform and controller state are identified by existing SHA-bound records. | PASS locally |
| REL-025.S03 | Root and Astra test suites plus foundation/install checks completed with exit code 0. | PASS locally |
| REL-025.S04 | Existing rollback, denial, migration-guardrail and deferred-platform tests cover negative boundaries. | PASS locally |
| REL-025.S05 | Final result distinguishes verified Linux work, deferred native work, GitHub Free residual risk and unperformed publication. | PASS locally |

## Handoff

`REL-025 | child_receipts pending Master registration | start_sha dd61427d1eadd407eb9a57468bfdbd70e68e4a92 | candidate_sha pending | integration_sha pending | branch feature/astra-rel-025-a1-e0bbab31 | files docs/tasks/REL-025-VERIFICATION-20261119.md | independent_qc pending | merger_result pending | runtime_lane main_builder | retries 0 | blockers Windows/macOS/native TWS evidence deferred; GitHub Free hosted enforcement deferred`
