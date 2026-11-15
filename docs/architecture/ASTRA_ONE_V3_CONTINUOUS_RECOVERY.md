# Astra One v3 — Continuous Engineering, Recovery, and Batch Self-Improvement

**Status:** implementation proposal and ATLAS read-only monitor extension, **not** a deployed control plane.
**Build target:** 247 parent tasks / 1,359 subordinate checklist steps in ARCHON-JARVIS-V2.
**Source of truth:** the canonical SDA SQLite ledger and Git commit/QC receipts.
**Active repository:** `admindeveloper4562/A.R.C.H.O.N`; `main` stays owner-protected, `develop` is the serial integration target.

## Executive design

Astra One runs as a durable, systemd-managed orchestration process. Its interactive Codex Supervisor is an **ephemeral reasoning session**, not a single unbounded process promised to survive weeks of work. The durable controller checkpoints state, creates bounded Supervisor sessions with verified context packets and resumes them after quota, process restart or context exhaustion. Completion of the 247 parents requires actual acceptance receipts, relevant external tests, owner decisions and a safe release gate; neither model output nor a deadline creates authority.

### Roles and permissions

| Role | Logical slots | Access | Responsibility |
| --- | ---: | --- | --- |
| Primary Supervisor | 1 | Read-only project inspection; submits signed proposals to Master | Diagnose, prioritize, spawn bounded subagents, compile improvement and recovery plans |
| Deterministic Master | 1 singleton | Exclusive SQLite state and lease authority | Dispatch, queue transitions, claim ownership, approvals, receipt validation, fencing |
| Normal Codex coding workers | 5 | Own isolated worktree, scoped write | Implement eligible parent tasks and subtasks; never approve or merge |
| Supervisor recovery coders | 2 | Own isolated repair worktrees, scoped write | Implement bounded fixes for actionable blocked cases |
| Upgrade auditor / canary tester | 1 | Read-only production state + disposable test environment | Deduplicate failure signatures, reproduce and test architecture upgrades |
| Independent QC | Shared separate bounded lane | Read-only candidate checkout and isolated tests | Return structured evidence-backed pass/reject; not a coder or Merger |
| Merger | 1 serialized lane | Isolated integration worktree; scoped write | Resolve **Git integration conflicts only**; revalidate and integrate accepted candidates |
| AEGIS/watchdog | Separate out-of-process | Protected control plane | Enforce STOP, upgrade rollback, one-writer fencing and service health |
| ATLAS Monitor | Separate read-only process | SQLite query-only | Show observed state; no dispatch or control |

**Concurrency:** 5+2+1 are maximum logical role slots, not eight unconditional concurrent model sessions. The scheduler enforces a global resource/token/quota budget based on real model entitlement, host RAM/CPU and Guardian non-preemptive priority. Supervisor subagents count against the same resource budget and cannot multiply privileges. Start with fewer simultaneous slots and raise only after qualification.

## Canonical queues and blocked-case overlay

Maintain exactly five canonical SDA queues: `project_queue`, `pending_queue`, `rebuild_queue`, `review_queue`, and `merge_queue`. The **blocked queue** is a transactional *view of actionable blocked cases* (`supervisor_cases`) backed by task state; it is not a sixth competing task queue. Any case must retain original task ID, dependency edges, owner gates, attempt history, source/base SHA and final candidate/QC/merge receipts.

Block classification is mandatory:

1. `code_defect`, `qc_rejection`, `semantic_incompatibility`: recovery coder may claim once lease and scope are proven.
2. `merge_conflict`: Merger may rebase/replay **without semantic edits**, then rerun tests; semantic conflicts return to coding.
3. `infrastructure`, `provider_quota`, `sandbox`, `resource_pressure`: infra repair or pause, **not** repeated coding attempts.
4. `dependency_wait`: keep waiting, not sent to recovery.
5. `approval_required`, `credential_required`, `device_unavailable`, `privilege_required`: issue owner/device dependency and continue unrelated work. Never self-approve.
6. `suspected_engine_bug`: upgrade auditor builds a reproduction for a staged control-plane fix.

Do not conflate ordinary dependency-blocked tasks with failed implementation tasks.

## Normal worker → QC → Merger

A worker receives a pinned parent, a bounded child checklist, source SHA, allowlisted paths, acceptance matrix, prior failure fingerprint and short relevant code/context. It implements in a dedicated worktree and emits a candidate SHA and test receipts.

Independent QC runs deterministic syntax, tests, type and security gates **before** model-level code review. A rejection must give `failure_class`, `finding_id`, `file`, `location`, `observed`, `expected`, `reproduction`, `test_sha` and a bounded repair suggestion, excluding sensitive payloads. Do not accept unsupported generic "integration risk" findings. QC must review a fixed candidate SHA and cannot self-approve.

Merger checks QC receipt, freshness, dependencies and patch safety, then attempts a serial integration. It may perform nonsemantic three-way merges, rename-aware conflict resolution and deterministic regeneration of purely derived files, with mandatory post-merge tests and fresh QC when the diff changed. It MUST NOT change application semantics, weaken tests/policies, invent APIs or cure implementation bugs. Those cases become actionable supervisor recovery cases.

Exactly one integration writer may advance `develop`; use a lease/fencing generation and a fast-forward-only remote push. Pushing is not equivalent to a completed product acceptance test.

## Supervisor recovery protocol (runs alongside normal development)

```
BLOCKED (actionable only)
 -> TRIAGED
 -> EVIDENCE_PINNED
 -> SUPERVISOR_DIAGNOSIS
 -> RECOVERY_ASSIGNED (R1 or R2)
 -> RECOVERY_CODING
 -> INDEPENDENT_QC
 -> REVIEW_QUEUE
 -> MERGE_QUEUE
 -> SERIAL_MERGE
 -> COMPLETED
 -> LESSON_PROPOSED
```

Failed QC returns to `RECOVERY_CODING` with a specific, new failure reproduction. An integration conflict returns to the Merger for a bounded nonsemantic retry; semantic changes return to the recovery coder. The Supervisor retains the case until both its task and merge receipt are confirmed. The original task is never run simultaneously by a normal worker and recovery worker.

The Supervisor's **main agent** inspects live systems read-only. Project-scoped Codex subagents may explore distinct components, code scoped patches, or run independent review in parallel. They inherit the parent's permissions/provider; use role-specific `.codex/agents/*.toml`, bound task context, worktree assignments and a max-thread budget. The human-facing interactive session must not be the only persistent controller.

## Honest task/subtask completion

Each of the 1,359 subtasks needs its own:
`subtask_id, parent_id, state, dependency_receipts, evidence_ref, test_ref, candidate_sha, qc_receipt, updated_at`.

**Never mark all children `completed` merely because the parent merged.** Child criteria may be recorded individually during the worker run; the parent completes only after all required child receipts exist, independent QC verifies them and the corresponding candidate is serially integrated. Until this is implemented, the monitor must label child statuses **recorded, not independently verified**.

## Keep five workers meaningfully occupied

Run a rolling READY reservoir with admission checks: dependencies completed, architecture/owner gates satisfied, task acceptance test available, file scope resolved, source SHA pinned, no duplicate active lease. Refill before a worker finishes, not only after a batch ends.

When the DAG offers fewer than five genuinely ready parent tasks, idle coding slots may work on **separate approved and dependency-safe preflight** tasks (test fixtures, documentation contracts, index preparation, independently mergeable support work). Do not invent unrelated code or misreport blocked work as completed. Deduplicate overlapping file scopes and avoid redundant speculative planning.

Measure `slot_idle_reason`: `no_eligible_work`, `resource_budget`, `provider_quota`, `owner_gate`, `integration_lock`, `worker_startup`. Display utilization with both **allocated** and **eligible** denominators.

## Batch boundary and upgrade protocol

A development batch is a cohort of admitted parent tasks with a fixed queue epoch. It is DRAINED when all tasks in the cohort are merged or are classified owner/device/privilege-blocked with durable receipts; ordinary software defects must be resolved or explicitly deferred with an actionable Supervisor case, **not** silently waived.

The upgrade auditor continuously mines failed/rejected attempts and performs a preflight similarity scan of pending task packets to prevent repeated known mistakes. Proposed improvements are versioned `upgrade_batches`, with a reproducible regression test and impact/risk analysis. Do not hot-patch the running Master.

```
AUDIT -> PROPOSED -> PATCH_IN_ISOLATION -> TESTED
      -> DRAIN_NEW_CLAIMS -> SAVEPOINT & VERIFIED BACKUP
      -> STAGED_CANARY -> EXTERNAL_WATCHDOG_APPROVAL
      -> ATOMIC_POINTER_SWITCH -> HEALTH_SOAK
      -> COMMITTED or ROLLED_BACK
```

Normal work continues through audit, proposal, code and tests. During activation, stop **new claims**, allow in-flight workers to complete or checkpoint, reconcile all leases and outstanding tool effects, then switch verified binaries/schema. Keep the last-known-good controller and database snapshot. Restore STOP/PAUSE/quota markers on restart. Do not automatically update Guardian/watcher policy or protected access rules.

If the batch is temporarily blocked by owner inputs, Supervisor continues preparing ready successors and upgrades but cannot counterfeit completion. Shutdown after 247 real completions is separate from owner-approved migration and release.

## Learning / coding handbook

After a repair merges, create a `lesson_proposal` with:
`failure_fingerprint, affected_task_ids, root_cause, wrong_approach, verified_fix_sha, regression_test_sha, applicability, counterexamples`.

Deduplicate and compare with existing handbook rules. Generalizable nonsecurity engineering lessons may be accepted by authorized independent QC under reviewed version control. Guardian owns its restricted recovery lessons; Research owns sourced tips. Ordinary coding workers may only propose handbook edits. New safety rules, privilege changes, test exceptions or global constitution updates require owner approval. No model may change its own approval policy.

Before dispatch, preflight only the most relevant accepted lessons and affected task signatures, using a bounded context packet—never the entire handbook and 1,359-child plan.

## Monitor: optional additive SQLite telemetry schema

These tables are proposed; they **do not yet exist in every Astra One database**. Create them only through a tested additive migration in a separately approved SDA task. The read-only ATLAS Monitor recognizes them if present:

```sql
CREATE TABLE supervisor_cases(
  case_id TEXT PRIMARY KEY,
  parent_id TEXT NOT NULL,
  state TEXT NOT NULL,
  category TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  -- other private evidence/receipt refs may be stored but never displayed
  FOREIGN KEY(parent_id) REFERENCES tasks(id)
);

CREATE TABLE supervisor_lanes(
  lane_id TEXT PRIMARY KEY
    CHECK(lane_id IN ('repair_1','repair_2','upgrade_auditor')),
  role TEXT NOT NULL,
  task_id TEXT NOT NULL DEFAULT '',
  state TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE upgrade_batches(
  batch_id TEXT PRIMARY KEY,
  state TEXT NOT NULL,
  candidate_sha TEXT NOT NULL DEFAULT '',
  rollback_sha TEXT NOT NULL DEFAULT '',
  updated_at TEXT NOT NULL
);
```

Required future extensions: `failure_fingerprints`, `review_receipts`, `merge_receipts`, `subtask_receipts`, `batch_epochs`, `lane_leases`, and `upgrade_health_checks`. All writes go through the deterministic Master or trusted migration. Personal content, raw prompts, private failure details and credentials must not enter monitor tables.

ATLAS Monitor reads these as **recorded state**, not confirmed process liveness. Future runners should additionally emit heartbeats, with explicit stale/unknown presentation. It must never control the runner or implicitly issue recovery commands.

## Main engineering hazards

| Hazard | Mitigation |
| --- | --- |
| Two Masters claiming/merging same task | Exclusive DB and Git leases with fencing generations; idempotency keys |
| Recovery workers duplicating normal jobs | One task owner per active generation, atomic transfer/lease revocation |
| 8+ Codex calls exhausting quota/resources | Global concurrency/CPU/RAM/token budget and backpressure |
| Misclassified owner/dependency gate | Explicit failure taxonomy; owner gates never auto-repaired |
| Merger "fixing" code | Restrict to nonsemantic Git integration; independent re-review after conflict resolution |
| Repeat QC false negatives or wasted attempts | Evidence-backed findings, stable failure fingerprint, early escalation after 2 identical rejections |
| Supervisor infinite prompt/context exhaustion | Durable state; bounded spawned Codex sessions; systemd watchdog and session renewal |
| Failed self-upgrade disables recovery | Independent trusted watchdog, verified rollback, monotonic fencing token and tested DB restoration |
| Parent falsely completes all children | Individual child receipts and dependency validation |
| Long-running batch never drains | Cohort snapshots, separate blocked cases, clear escalation and external-gate statuses |
| Workers idle due to DAG bottleneck | Ready-work reservoir, independent support tasks, honest idle reasons |
| Handbook poisoned by model-generated rules | Append-only reviewed evidence, section-scoped authorship and owner security gates |
| Main/develop/local integration diverge | Snapshot and ancestry checks; never force push/reset; reconcile before automatic publication |
| Host powers off or Codex quota expires | Durable continuation and STOP/PAUSE/PAUSED_QUOTA preservation; resume when authorized and available |

## Qualification and delivery milestones

**M0:** audit actual local controller, database schema and branch SHAs; reproduce the current subtask auto-completion flaw.
**M1:** atomic blocked-case triage, failure signatures, one-owner leases, 2 independent recovery slots and accurate child receipts.
**M2:** independent recovery QC, restricted nonsemantic Merger, serial Git reconciliation, ready-work reservoir.
**M3:** upgrade auditor, batch epochs, staged canary, trustworthy external rollback and handbook lesson proposal flow.
**M4:** persisted Supervisor lifecycle and restart-safe bounded multiagent sessions, quota-aware resource scheduling.
**M5:** real-host canary with normal five workers plus recovery/audit tasks, failure injection, DB restore, owner gates, monitoring and honest test outcomes.
**M6:** staged enablement of full 247-parent autonomous build; no protected release or native SDA cutover until explicit approval.

Success metrics: first-pass QC rate, attempts per accepted parent, cases resolved without interrupting normal workers, meaningful slot utilization, merge conflict recovery rate, subtask receipt coverage, recurrence rate of known failure signatures, upgrade canary rollback time, and verified `develop` publication lag. Count all attempts, failures and rejected work—not just passing runs.
