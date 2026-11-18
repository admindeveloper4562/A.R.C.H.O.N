# MIG-011 Verification — checkpoint, receipts and restart reconciliation

Status: `LOCAL_EVIDENCE_RECORDED / INDEPENDENT_QC_PENDING`

This audit uses the canonical Master state and the serial integration checkout.
It does not alter the task plan, rewrite history or infer owner approval.

## Pinned identity

| Item | Value |
| --- | --- |
| Task | `MIG-011` |
| Source SHA | `43c8db7de8a5f0277a7db23379019d05f2edd2c6` |
| Integration SHA at audit start | `96f350fb3cc1bbec465fc87d93d706973108c86e` |
| Parent-plan SHA-256 | `10cb1ed53eace6af1c5d052ef0ad0a85eaf9f535db5ae0be794cc7d12752b154` |
| Project graph | `247` parents / `1,359` children |
| SQLite integrity | `ok` |
| Candidate SHA | Bound by the Master after commit |
| Remote publication | Not attempted |

## Acceptance findings

| Requirement | Evidence | Result |
| --- | --- | --- |
| Checkpoint restoration | Existing deterministic checkpoint export/restore tests verify integrity, state digest and preserved controls on a disposable copy | PASS locally |
| Idempotent receipts | Main-builder handoff tests reject malformed child evidence, accept one submission and return the same receipt on replay | PASS locally |
| Persistent session identity | Run records retain task, generation, role, model and bounded tool metadata; task leases fence stale generations | PASS locally |
| Owner approval state | Owner-gated records remain separate from completed tasks; no approval is created by this audit | PASS locally |
| Duplicate work rejection | Duplicate candidate generation/submission and stale leases are rejected or returned idempotently by the Master | PASS locally |
| Current ledger consistency | Integrity is `ok`; 209 project parents are completed, 1,154 children are marked completed and 1,116 independent-QC receipts exist | PASS locally |

The counts above distinguish completed rows from receipts. Any completed child
without an independent receipt remains legacy/unverified and is not silently
backfilled by this audit.

## Reproducible local evidence

The following existing checks are the relevant bounded evidence set:

```text
PYTHONPATH=src:. python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_*.py' -q
```

The checks cover checkpoint restore, receipt replay, stale-generation fencing,
owner-gate persistence, duplicate candidate handling and serial integration.
Independent QC must rerun the exact candidate in the isolated Docker lane and
bind its exit code, test result and artifact digest to the candidate SHA.

## Child evidence contract

| Child | Evidence |
| --- | --- |
| `MIG-011.S01` | Pinned repository, plan, database and integration identities above |
| `MIG-011.S02` | Acceptance matrix with fact/inference separation and receipt semantics |
| `MIG-011.S03` | This versioned migration audit in `docs/migration/` |
| `MIG-011.S04` | Independent QC must re-check the hashes and candidate-bound result |

Only the Master may record child receipts and complete the parent after QC and
serialized merge. No production cutover or owner-gated action is implied.
