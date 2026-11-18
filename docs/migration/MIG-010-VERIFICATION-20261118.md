# MIG-010 Verification — approved single-builder pipeline

Status: `LOCAL_EVIDENCE_RECORDED / INDEPENDENT_QC_PENDING`

This report replaces the obsolete five-coding-worker acceptance through the
owner-authorized MIG-010 plan amendment. It qualifies one Main Codex builder
with deterministic Master admission, isolated Git state, independent QC,
serialized integration, durable receipts, restart recovery and rollback
controls. Astra's retired W1–W5/R1–R2 coding dispatch is not started.

## Identity and scope

| Field | Observed value |
| --- | --- |
| Task | `MIG-010` |
| Execution mode | `verification` |
| Source SHA | `43c8db7de8a5f0277a7db23379019d05f2edd2c6` |
| Integration base SHA | `2d0203dab621bd2c1ac754c6b56e25ecf621c70f` |
| Candidate SHA | Bound by the canonical Master handoff receipt after commit |
| Parent plan | `247` parents; `1,359` children |
| Architecture | Ten modules; Business excluded |
| Remote CI | Not invoked; hosted-only checks remain `DEFERRED_QUOTA` |
| Protected branches | Not modified; no publication attempted |

The source and integration identities are inputs to this candidate. The final
candidate SHA, changed-file digest, independent QC receipt and post-merge SHA
are recorded by the Master; this document does not authorize those transitions.

## Acceptance matrix

| Clause | Observable evidence | Result at authoring |
| --- | --- | --- |
| Deterministic admission | Real `builder-claim` admitted generation 2 for this parent and recorded the Main Codex run/worktree in SQLite | PASS |
| One coding authority | The claimed run uses role `main_builder`; no Astra coding worker process or competing Master was active | PASS |
| Isolated implementation | The candidate worktree is a separate branch rooted at the recorded integration SHA | PASS |
| Independent QC | `process_candidate_queue`/`qc-merge` must run Docker no-network checks against the exact candidate SHA | PENDING_QC |
| Serialized integration | The Merger must verify QC, base ancestry, scope and receipts before changing the integration worktree | PENDING_MERGE |
| Durable child evidence | Five ordered child receipts must bind the candidate, acceptance evidence and independent verifier | PENDING_MERGE |
| Restart recovery | Existing deterministic recovery tests cover interruption, lease fencing and idempotent replay prevention in disposable state | PASS |
| Rollback verification | Existing checkpoint/watchdog tests cover verified backup, last-known-good identity and failed-release fencing in disposable state | PASS |
| Owner/security gates | No owner gate is waived; STOP/PAUSE/quota controls and protected-branch policy remain active | PASS |

No historical five-worker host qualification is claimed. The amended
single-builder contract is the governing acceptance for this generation.

## Fixtures and environment

Checks use disposable test state where destructive failure injection is needed.
No credentials, private prompts, model output, imported legacy execution or
production state is included.

| Observation | Value |
| --- | --- |
| Python | `3.12.3` |
| SQLite | `3.45.1` |
| Docker QC image | `archon-python:3.12-git-20261114` |
| Docker network | `none` |
| Active coding lanes | Main Codex only; W1–W5/R1–R2 not launched |

## Reproducible checks

The candidate is evaluated with the following bounded checks:

```text
PYTHONPATH=bootstrap/astra-one python3 -m unittest discover \
  -s bootstrap/astra-one/tests -p 'test_*.py' -q
PYTHONPATH=src:. python3 -m unittest discover \
  -s tests -p 'test_*.py' -q
docker run --rm --network none archon-python:3.12-git-20261114 \
  python3 -m unittest discover -s tests -p 'test_*.py'
```

The deterministic suite includes real state-machine coverage for the Main
Codex handoff, duplicate submission idempotence, independent QC queueing,
serialized Merger integration, interrupted-run fencing, checkpoint restore,
rollback controls and rejection of autonomous coding dispatch. The independent
QC receipt, exit code, test count and artifact digest are bound to the final
candidate by the Master.

The pre-submission local run produced these results on the recorded base:

| Suite | Exit | Tests | Result |
| --- | ---: | ---: | --- |
| `PYTHONPATH=src:. python3 -m unittest discover -s tests -p 'test_*.py' -q` | 0 | 522 | `OK` |
| `PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_*.py' -q` from `bootstrap/astra-one` | 0 | 177 | `OK` |

The raw command output remains outside the candidate source tree; the
independent QC receipt is the durable candidate-bound result and must include
its own artifact digest.

## Child evidence contract

| Child | Required evidence |
| --- | --- |
| `MIG-010.S01` | Measurable acceptance matrix and amended-contract binding |
| `MIG-010.S02` | Sanitized fixture and environment snapshot |
| `MIG-010.S03` | Exact commands, exit codes, test counts and artifact hashes |
| `MIG-010.S04` | Restart, duplicate, denial, rollback and control-marker evidence |
| `MIG-010.S05` | This source/base-bound report and explicit remaining risks |

Only the Master may record the five child receipts and move the parent to
verified completion. A candidate submission or local test result alone is not
completion.
