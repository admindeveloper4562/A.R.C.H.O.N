# SDA-026 Verification — SDA gates A–I

Status: `LOCAL_EVIDENCE_RECORDED / INDEPENDENT_QC_PENDING`

This is a candidate-bound verification report, not an authorization to promote
the runtime or to mark the full SDA gates complete. A local support check is
not substituted for a required host, provider, watchdog, owner or Merger
observation. The deterministic Master remains the authority for task state.

## Identity and scope

| Field | Observed value |
| --- | --- |
| Task | `SDA-026` |
| Execution mode | `verification` |
| Source SHA | `43c8db7de8a5f0277a7db23379019d05f2edd2c6` |
| Integration base SHA | `d05fe5ba794cf9bf26c4b0721c5525ecab720b7c` |
| Candidate SHA | Bound by the canonical Master handoff receipt after commit |
| Parent plan | `247` parents; `1,359` children |
| Workstreams | `14` |
| Architecture modules | `10`; Business excluded |
| Remote CI | Not invoked; hosted-only checks remain `DEFERRED_QUOTA` |
| Production/main promotion | Not attempted |

The source and integration identities above are inputs to this candidate. The
final candidate SHA, changed-file digest, QC receipt and post-merge SHA must be
recorded by the Master; this document does not self-authorize those transitions.

## S01 — acceptance matrix

The table records the strongest supported observation without converting a
support check into full gate acceptance.

| Gate | Observable requirement | Local observation | Current full-gate status | Remaining blocker |
| --- | --- | --- | --- | --- |
| A | Dependency-safe admission preserves the canonical parent/child graph | Full-plan identity and task-type/eligibility tests are present; canonical plan reports 247/1,359 | `NOT_VERIFIED` | Exact candidate-bound real admission evidence is still required |
| B | Isolated builder produces an in-scope diff and leaves source refs unchanged | Main-builder handoff, scope validation and no-op/path rejection coverage pass locally | `NOT_VERIFIED` | A complete real-host builder acceptance packet is not established by this report |
| C | Provider/model/quota decisions are durable and never silently substituted | Control-state tests cover quota denial; no provider call is used here | `NOT_VERIFIED` | Authenticated provider/model evidence for this candidate is absent |
| D | Independent QC reviews the exact candidate and emits reproducible evidence | Local deterministic checks pass | `PENDING_QC` | Independent Docker QC must bind its receipt to the final candidate SHA |
| E | One serialized Merger integrates only an approved, fresh candidate | Integration policy and stale-base tests pass locally | `PENDING_MERGE` | Authorized Merger result and post-merge SHA are not available at authoring |
| F | Restart preserves leases, receipts and idempotent effects | Recovery, retry-generation and duplicate-recovery checks pass locally | `NOT_VERIFIED` | A controlled process-loss/real-host acceptance receipt is still required |
| G | Guardian repair is scoped, deduplicated and independently checked | No new Guardian finding is created by this verification candidate | `NOT_VERIFIED` | Real Guardian/recovery case evidence is absent |
| H | Trusted rollback restores last-known-good state and controls | SQLite backup/restore digest and canonical-unchanged checks pass locally | `NOT_VERIFIED` | Trusted-watchdog canary activation and rollback evidence are absent |
| I | STOP, PAUSE, quota and approval controls survive restart/replay | STOP/PAUSE/PAUSED_QUOTA and disabled autonomous-run checks pass locally | `NOT_VERIFIED` | Provider handoff, Guardian replay and full crash-persistence evidence remain open |

Overall full-gate result: `NOT_VERIFIED`. The open items are preserved as
blockers; none is silently waived or counted as a successful acceptance gate.

## S02 — fixtures and environment

Checks use disposable local repositories/state and sanitized fixed metadata. No
credentials, private prompts, model text, imported legacy execution, network
access or production state is used by the local evidence.

| Observation | Value |
| --- | --- |
| Python | `3.12.3` |
| SQLite | `3.45.1` |
| Host | Linux `7.0.0-43-generic`, x86_64 |
| Docker QC image | `archon-python:3.12-git-20261114` (`sha256:df1ab2bf04e4047fdb56bca2f1eb46e574ce4dc223dfd9a0e0fd7d0493a53ded`) |
| Docker network | `none` for independent QC |
| Fixture policy | deterministic, bounded, no secrets |
| Hardware/device evidence | not exercised; no Windows or Cloudflare claim |

## S03 — executed local checks

`artifact_sha256` values hash bounded metadata (command, exit code, test count
and pinned source/base), not raw output. Raw logs are not retained in this
report.

| Command | Exit | Tests | Artifact SHA-256 |
| --- | ---: | ---: | --- |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=bootstrap/astra-one python3 -m unittest discover -s bootstrap/astra-one/tests -p 'test_*.py' -q` | 0 | 168 | `f83d26b1da72e0c215b5fc32b8da77a32fb5203d32be8952fa2aa0aa9d69a019` |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. python3 -m unittest discover -s tests -p 'test_sda_shadow_handoff.py' -v` | 0 | 3 | `75802ddd2897292c9ce1286b06476d390dabc118cc72b64afee3a723b086d4c1` |
| `python3 bootstrap/astra-one/scripts/verify_manifest.py` | 0 | n/a | `88b8a933e9936d91e20c72e146ac1d0385938057b614cfda7aa8f2ce4d9ef82f` |

The complete Astra suite finished `168` tests with `OK`. The focused ARCHON
shadow-handoff suite finished `3` tests with `OK`. These observations do not
authorize owner gates, device acceptance, remote CI or release promotion.

## S04 — negative and failure evidence

The suite includes deterministic checks for:

- quota and lane controls refusing claims while preserving the marker;
- autonomous `run` refusal, so Astra cannot promote or launch a coding worker;
- restart recovery that interrupts once, does not replay on a second recovery,
  and creates a distinct bounded retry generation;
- checkpoint restore to a new disposable database with matching state digest,
  SQLite integrity and unchanged canonical state/source identity;
- duplicate candidate handoff idempotence, stale leases/bases and protected
  path/scope rejection.

These are local failure-injection observations. They do not claim a physical
host crash drill, provider outage, watchdog canary or Windows/Cloudflare
qualification.

## S05 — handoff and remaining requirements

| Child | Evidence in this candidate |
| --- | --- |
| `SDA-026.S01` | Gate A–I matrix with measurable assertions and explicit status |
| `SDA-026.S02` | Sanitized fixture and environment snapshot |
| `SDA-026.S03` | Exact commands, exit codes, counts and bounded artifact hashes |
| `SDA-026.S04` | Negative/failure-case summary with no fabricated host claims |
| `SDA-026.S05` | This report, source/base-bound and explicit about unresolved gates |

Next authorized stages are independent Docker QC against the exact candidate,
then the serialized Merger. Only the Master may record child receipts and move
the parent to verified completion. Real provider, watchdog, owner, device and
full host-gate evidence remains an explicit prerequisite where listed above.
