# JARVIS V2 — 247 Parent Tasks and Worker Subtask Execution Guide

**Project:** ARCHON / JARVIS V2  
**Target repository:** `admindeveloper4562/A.R.C.H.O.N`  
**Integration branch:** `develop`  
**Parent plan:** `docs/tasks/JARVIS_V2_TASK_PLAN.json`  
**Expanded worker plan:** `docs/tasks/JARVIS_V2_SUBTASK_PLAN.json`  
**Parent tasks:** 247 (preserved)  
**Expanded subtasks:** 1359  
**Active modules:** 10; Business excluded  
**Workers:** 5 Codex CLI workers, requested `gpt-5.6-luna`, medium reasoning

## 1. Preserve the parent plan

The original JSON remains the authoritative list of exactly 247 parent tasks. The expansion file adds ordered child checklists keyed by the original parent IDs. It does not renumber, delete, merge, split or replace any parent task. Subtasks are nested under parents and do not inflate the parent task count.

The original dependency DAG is preserved: 247 nodes, 446 dependency edges, zero missing references and zero cycles. Astra One must revalidate these facts when importing.

## 2. How the five workers execute

1. The Supervisor imports exactly 247 parent tasks into the SDA `project_queue`, preserving each task ID, title, module, milestone, priority, acceptance, dependency and owner gate.
2. The Supervisor reads `AGENTS.md`, `CODING_HANDBOOK.md`, `SECURITY.md`, the consolidated architecture, module contract and the relevant parent/subtask packet before dispatch.
3. ATLAS selects only dependency-ready parents, sorting eligible work by P0/P1/P2 and FIFO. A blocked task never blocks unrelated ready work.
4. Up to five parent tasks may be active, one per worker. A worker owns its parent and ordered subtasks in one isolated Git worktree. Do not split one parent across workers unless the Supervisor proves the child steps are independent and file-disjoint.
5. The worker records each subtask's status, output, changed paths, test command, exit code and evidence reference. A child is not complete because the model says it is complete; its `done_when` must be demonstrated.
6. The worker commits one coherent candidate for the parent task and returns the candidate SHA. It never self-approves, merges to `develop`, pushes to `main`, deploys or changes secrets.
7. Independent QC reviews the exact candidate SHA and runs deterministic checks. Failed QC returns actionable bounded feedback to the worker/repairer.
8. The single serialized Merger checks freshness, resolves conflicts in an isolated integration worktree, runs relevant regression tests and updates `develop` only after review passes.
9. Parent completion is recorded only after all required subtasks, owner gates, QC and merge evidence are complete.

## 3. Subtask shape

Every child includes a stable ID such as `CORE-004.S03`, sequence, kind, title, worker/supervisor/owner role, exact instruction, deliverable, completion test, child dependency and evidence requirement. Child steps are sequential by default. Supervisor may parallelize only when file boundaries and logical dependencies prove it safe.

Audit tasks produce source inventories, findings and evidence reports. Design tasks produce contracts, failure models and acceptance matrices. Implementation tasks inspect, design, code, test and hand off. Migration tasks pin source SHAs, inventory provenance, dry-run, apply bounded changes, verify and prove rollback. Verification tasks run a declared test matrix. Owner-gated tasks prepare a decision packet and wait for an explicit owner response.

## 4. Git workflow

- `main`: protected release history only.
- `develop`: serial Merger-controlled integration branch.
- Worker branch: `<kind>/<module>/<TASK-ID>-<kebab-description>`.
- Commit: `<type>(<scope>): <imperative summary> [TASK-ID]`.
- Each parent task uses a dedicated worktree and task branch. Do not reuse a branch for a different parent.
- No worker directly pushes to `develop` or `main`; no force push; no destructive cleanup.
- Preserve unpadded semantic versioning.

## 5. Model and quota behavior

The requested Linux worker profile is Codex CLI `gpt-5.6-luna`, medium reasoning, five workers. Verify actual model entitlement, login and quota before starting. If Codex quota is exhausted, pause safely, persist state and do not burn repair attempts. Do not silently substitute Ollama or a different hosted model.

Do not trigger GitHub Actions while the owner's monthly build quota is exhausted. Run local checks and Docker no-network QC where applicable. Any acceptance that specifically requires hosted GitHub runner execution remains `DEFERRED_QUOTA`, not passed. In particular, BASE-002, BASE-003 and REL-016 must not be marked complete based only on local equivalents.

## 6. Module guardrails

- **BASE:** preserve refs, worktrees, logs and existing data; read-only audit unless the parent authorizes a bounded change.
- **SDA:** one Master, five isolated worktrees, independent QC, serialized Merger.
- **MIG:** SHA-pinned, create-only, provenance-tracked imports; legacy source remains untouched.
- **CORE:** one durable session per task and a separate event session; idempotent effects.
- **BACK:** domain-owned data, least-privilege scopes, secrets never enter prompts/logs.
- **AUTO:** Cloudflare stores durable jobs and minimal progress metadata; it does not run local inference while PCs are offline.
- **WIN:** authenticated outbound Windows agent; Ollama remains loopback-only; lease/reconnect safety.
- **GUARD / AEGIS:** local model gets the next compatible inference slot after current generation finishes safely; never preempt active generation; deterministic STOP remains independent.
- **RUN / ARCHON:** observe -> propose -> authorize -> execute -> verify; sensitive actions require approval.
- **RES:** citations, source provenance, license/access boundaries and uncertainty.
- **TWS:** idempotent XP/rewards, preserve Aurelia and cross-device progress.
- **WIC:** event/fetch timestamps, corrections, retractions and source ranking.
- **FIN:** Mira read-only, partner consent, no broker writes, paper-only trading.
- **REL:** evidence bound to candidate SHA; no mock-only acceptance; explicit owner release gate.

## 7. Existing ARCHON repository — do not create a duplicate

The target repository already exists as `admindeveloper4562/A.R.C.H.O.N`. SDA-027/SDA-028 must verify and use this owner-selected repository rather than creating another repository. Keep `main` protected and use `develop` for serial integration. Confirm the actual current refs and working tree before each run.

## 8. Astra One → native SDA handover

Astra One remains the external trusted builder while native SDA is built and qualified. Native SDA first runs in read-only shadow mode. It cannot claim Astra's live tasks or write to the integration branch while Astra owns the queue. The handover requires real five-worker Codex qualification, independent QC, crash/lease recovery, STOP/PAUSE and quota restoration, duplicate-effect prevention, rollback, one-writer fencing, Guardian/watchdog validation and explicit owner approval. AEGIS/Guardian may stage a verified candidate but cannot approve its own cutover. Keep Astra One and its state as the external rescue path until post-cutover soak and owner authorization are complete.

## 9. Start order and pause behavior

- First run a read-only import validation and host/model/quota preflight.
- Import all 247 parents and their child plans; do not dispatch all tasks simultaneously.
- Begin with eligible P0 tasks, then P1 and P2 as dependencies permit.
- Keep the task queue durable across restarts and preserve every failed attempt and checkpoint.
- Stop early for repeated identical errors, security failures, missing permissions, quota exhaustion or owner gates. The historical 20-attempt limit is a hard upper bound, not a target.
- Do not deploy Cloudflare, change production resources, migrate live queues, promote `main` or switch active SDA without the relevant explicit approvals.

## 10. Required worker handoff receipt

Every parent task must report:

`task_id | parent_sha | start_sha | branch | worker_slot | completed_subtasks | changed_files | tests_and_exit_codes | candidate_sha | QC_receipt | merge_sha | blockers`

The independent ATLAS Monitor remains a separate read-only terminal process. It must not start, stop, schedule or control Astra One.
