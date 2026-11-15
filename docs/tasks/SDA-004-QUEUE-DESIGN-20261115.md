# SDA-004 — Durable Five-Queue Design

Design timestamp: `2026-11-15T22:44:00+07:00`

Task: `SDA-004`

Execution mode: `design`

Candidate base: `1645781b9f91c0c69a6cd846b4d418776c5529be`

## 1. Purpose and boundaries

This design defines the durable state and transaction contract for the five
existing Astra One queues:

1. `project_queue`
2. `pending_queue`
3. `rebuild_queue`
4. `review_queue`
5. `merge_queue`

The existing SQLite database remains authoritative. The design does not create
a second task database, rename queues, change the 247-parent/1,359-child plan,
implement feature code, or authorize publication to `main`.

The design separates durable state transitions from long-running model and
Docker work. The deterministic Master owns SQLite transactions and leases; the
Main Codex owns feature implementation; independent QC owns review evidence;
the serialized Merger owns the single integration writer position.

## 2. Requirements and non-goals

| Requirement | Design response | Evidence target |
|---|---|---|
| Exact five queues | Preserve the five existing table names and queue roles. | Schema inspection and queue-count monitor |
| Atomic transitions | Update the task row, queue rows, run row and relevant receipt inside one `BEGIN IMMEDIATE` transaction. | Transactional unit tests and SQLite integrity check |
| Restart safety | Never infer completion from a process exit. Reconcile `preflight`, `coding` and `verifying` leases as interrupted and require a bounded resume/retry path. | Crash/restart fixture with preserved run history |
| Dependency safety | Admit only parents whose dependencies are completed and whose owner/device/credential gates are satisfied. | DAG and claim tests |
| One writer | Fence Master writes with the existing file lock and short SQLite write transactions. Do not hold the lock during inference or Docker. | Concurrent claim and Merger tests |
| Independent QC | Candidate submission is distinct from `approved`, `merged` and `completed`; QC evidence is bound to the exact candidate SHA. | Candidate/QC receipt test |
| Child correctness | Parent completion requires every required child receipt for the exact candidate. | Child-evidence negative and positive tests |
| Recovery | Preserve failed generations and put actionable failures in `rebuild_queue`; external blockers remain durable and are not retried as code defects. | Failure/retry and external-blocker tests |

Non-goals are autonomous coding dispatch, retrying quota/device/owner blockers,
changing security policy, direct remote GitHub publication, and native SDA
cutover.

## 3. Durable ownership model

### 3.1 Project envelope

`projects` stores one project envelope. `project_queue` contains at most one
row for that project and records its admission/status ordering. It is a project
index, not a second parent-task queue.

### 3.2 Parent task authority

`tasks` stores the parent identity, immutable task packet, dependency list,
priority, owner gate, current status, current generation, current lease/run,
candidate/base/integration SHAs and bounded error category. The task status is
the state authority; queue rows are indexed work views and must agree with it.

### 3.3 Queue roles

| Queue | Admission condition | Payload | Removal condition |
|---|---|---|---|
| `project_queue` | The imported project is registered. | Project ID, status and enqueue sequence. | Project archival through an authorized transition. |
| `pending_queue` | Parent is dependency-ready, authorized, not externally blocked, and has no active lease. | Parent/project IDs, enqueue sequence and availability time. | Atomic claim, terminal completion, external block or explicit bounded retry/reopen. |
| `rebuild_queue` | A generation failed or was rejected with a bounded category. | Parent/project IDs, failed generation and reason code. | Explicit retry/reopen claim, external classification, or verified completion. |
| `review_queue` | A real candidate was submitted and awaits independent QC. | Parent/project IDs and candidate SHA. | QC rejection, QC approval, or controlled external block. |
| `merge_queue` | Independent QC approved the exact candidate and all required evidence is present. | Parent/project IDs and candidate SHA. | Serialized Merger completion, conflict return, or controlled rejection. |

`parent_id` is unique in each per-parent queue. Queue rows are not history;
`runs`, `events`, `candidate_submissions`, `subtask_receipts` and failure
records preserve history.

### 3.4 Candidate handoff extension

The live Main Codex handoff adds `candidate_submissions` as an append-oriented
submission ledger. It records task/generation, builder session, base/candidate
SHAs, branch/worktree, changed-file manifest, bounded test/acceptance metadata
and QC/Merger state. It does not replace the five queues. A submission enters
`review_queue`; it becomes a completed parent only after QC, serial merge and
child receipts succeed.

The baseline integration used for this design predates that additive handoff
table. The schema-4 migration and its release-manifest update are therefore a
required implementation checkpoint before any queue-schema code change is
treated as integrated.

## 4. State and transition contract

```text
waiting --(dependencies/authorization satisfied)--> pending
pending --(Master claim)--> preflight --> coding --> verifying
verifying --(candidate submitted)--> awaiting_review
awaiting_review --(QC PASS)--> approved --> merge queue
awaiting_review --(QC rejection)--> failed + rebuild queue
approved --(serialized Merger PASS)--> completed
approved --(nonsemantic conflict)--> conflict + rebuild queue
any eligible state --(external prerequisite)--> blocked
preflight/coding/verifying --(restart without verified receipt)--> interrupted
```

The following rules are mandatory:

- A parent cannot be `completed` while a required child is not completed or
  lacks an independent receipt bound to the candidate SHA.
- `candidate_submissions.status=queued` is not QC approval and is not task
  completion.
- QC rejection preserves the candidate worktree, run and receipt and creates a
  bounded rebuild reason. It does not erase the prior generation.
- A quota, owner, credential, privilege, device or dependency wait is not sent
  to a coding retry loop.
- A Merger conflict is semantic if application behavior must change; semantic
  conflicts return to Main Codex coding and independent QC.
- A failed or interrupted generation cannot retain a live worker lease.

## 5. Transaction and locking rules

### 5.1 Writer fence

The deterministic Master acquires the existing file lock for short state
transactions. SQLite uses foreign keys and `BEGIN IMMEDIATE` for transitions.
The lock and transaction cover selection, fencing, queue mutation, run/event
metadata and commit. They do not cover Codex inference, Docker tests or a
network call.

### 5.2 Admission and claim

Inside one transaction the Master:

1. selects a `pending_queue` row by dependency, priority/FIFO, owner gate,
   control markers and active-lease checks;
2. validates the complete task type and ordered child packet;
3. increments the generation, writes the run/lease and sets `preflight`;
4. removes the parent from `pending_queue` and any stale `rebuild_queue` row;
5. records the first running child; and
6. commits or rolls back all of those changes together.

If the transaction fails, the queue and task remain at the pre-claim state.
The worker worktree is created only after the lease is committed; preparation
failure records a bounded failure and releases the generation through the
Master.

### 5.3 Candidate submission and QC

The Main Codex submits only a real commit from the leased worktree. The Master
rechecks lease identity, base SHA, branch, worktree boundary, candidate HEAD,
changed-file scope and bounded evidence in one transaction. It inserts one
idempotent `candidate_submissions` row, sets `awaiting_review`, updates the run
and inserts `review_queue` together.

QC first verifies the exact candidate and runs deterministic checks in an
isolated environment. A pass writes a bounded QC receipt, marks the submission
passed and invokes the authorized approval transition. A rejection writes only
an allow-listed category and leaves the candidate/history available for a
changed repair strategy.

### 5.4 Approval and serialized Merger

The approval transition removes `review_queue` and inserts the exact candidate
into `merge_queue` atomically. The Merger verifies current integration HEAD,
candidate ancestry, QC/child evidence, protected paths and clean worktrees.
Only then does it apply the reviewed patch, rerun required checks, commit the
integration result and update `integration_sha` under the Master fence.

Completion removes all active queue rows, writes the integrated SHA and child
receipts, updates the batch member and refreshes dependency-ready parents in
the same transaction. If any completion predicate fails, the transaction rolls
back and the parent is not marked complete.

### 5.5 Restart and crash behavior

On controller restart, the Master reconciles persisted `preflight`, `coding`
and `verifying` tasks against their run/lease records. Unknown process liveness
does not become success. The safe result is an `interrupted` record with the
original generation preserved; a later explicit bounded retry/reopen may create
a new generation. Submitted candidates remain in `candidate_submissions` and
are processed idempotently by `(task_id, attempt, candidate_sha)`.

## 6. Safety and permission boundaries

- The Main Codex is the only implementation writer for this profile.
- QC is read-only over application source; the Merger is the only integration
  writer.
- `main` is protected. No force push or remote publication is implied.
- STOP, PAUSE, PAUSED_QUOTA and owner gates are checked before claims and
  integration; none can be cleared by a worker assertion.
- Changed paths are validated against task type, scope, protected paths,
  generated artifacts, file count and size limits.
- Reports and receipts contain bounded metadata, hashes and categories, never
  secrets, private prompts, raw model conversations or unbounded logs.
- Historical candidates, runs, failed generations and backups are retained.

## 7. Acceptance test matrix

| Test | Expected result | Evidence |
|---|---|---|
| Claim with incomplete dependency | No claim; pending state remains durable. | Existing dependency claim test |
| Concurrent claims for one parent | One lease; no duplicate run or queue row. | Master-lock concurrency fixture |
| Failed generation | `failed` plus one rebuild row; review/merge rows absent. | Existing failed/retry test |
| Retry/reopen | New bounded generation; prior run and candidate history remain. | Retry/reopen receipt test |
| Candidate idempotency | Re-submitting the same generation/SHA returns the existing submission. | Candidate submission test |
| QC rejection | Rejection category is recorded; no completion. | QC rejection test |
| QC pass | Review row becomes merge row only after exact candidate evidence. | Approval transition test |
| Merger conflict | Integration remains unchanged; task is conflict/recovery, not completed. | Serial Merger conflict test |
| Successful merge | One integration commit, matching DB SHA, all child receipts, no stale queue rows. | Local Merger test |
| Crash before commit | SQLite rolls back the partial transition; no phantom claim. | Isolated SQLite interruption fixture |
| Restart after committed claim | Lease is reconciled as interrupted unless verified evidence exists. | Recovery test |
| STOP/PAUSE/quota | New claims/integration are refused; deterministic read-only telemetry may continue where policy allows. | Control-marker tests |
| Design scope | Documentation under `docs/` is accepted; source/executable changes are rejected. | Scope validator regression test |

The focused implementation commands for the runtime checkpoint are:

```text
cd bootstrap/astra-one
PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_*.py' -q
python3 scripts/verify_manifest.py
```

The design itself is not a claim that every future runtime test has passed; the
implementation and migration checkpoints must provide those receipts.

## 8. Supervisor review and allowed-path proposal

The proposed implementation scope for a later code task is limited to the
existing `bootstrap/astra-one/astra_one/` queue/state code and its focused
tests. Documentation and migration artifacts belong under `docs/` and the
release manifest must be updated whenever packaged Astra files change.

The Supervisor should approve the design when the five queue names, state
machine, lock scope, crash semantics, child receipt predicate and protected
operations above are preserved. No unresolved architecture or security
conflict is identified by this design. Any implementation that changes queue
names, weakens child evidence, holds the Master lock during inference, or
clears controls automatically must be rejected.

## Child evidence map

- `SDA-004.S01`: Sections 1–3 extract requirements, dependencies, queue roles,
  non-goals and open migration compatibility.
- `SDA-004.S02`: Sections 3–5 define ownership, schema payloads, interfaces,
  state transitions, versioning and transaction sequence.
- `SDA-004.S03`: Section 6 defines permissions, privacy, failure, retry,
  idempotency, rollback and STOP behavior.
- `SDA-004.S04`: Section 7 maps every acceptance clause to deterministic or
  manual evidence and identifies the focused commands.
- `SDA-004.S05`: Section 8 records the Supervisor review boundary and allowed
  paths against the architecture and security contract.

## Handoff

`SDA-004 | child_receipts pending until QC | start_sha 1645781b9f91c0c69a6cd846b4d418776c5529be | candidate_sha pending | integration_sha 1645781b9f91c0c69a6cd846b4d418776c5529be | files docs/tasks/SDA-004-QUEUE-DESIGN-20261115.md | independent_qc pending | merger pending | no owner gate | no external blocker`
