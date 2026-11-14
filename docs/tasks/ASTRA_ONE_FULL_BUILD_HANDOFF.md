# JARVIS V2 — 247 Parent Tasks and Worker Subtask Execution Guide

**Project:** ARCHON / JARVIS V2  
**Target repository:** `admindeveloper4562/A.R.C.H.O.N`  
**Integration branch:** `develop`  
**Parent plan:** `docs/tasks/JARVIS_V2_TASK_PLAN.json`  
**Subtask index:** `docs/tasks/JARVIS_V2_SUBTASK_PLAN.json`  
**Parent tasks:** 247 (preserved)  
**Expanded subtasks:** 1359  
**Active modules:** 10; Business excluded  
**Workers:** 5 Codex CLI workers, requested `gpt-5.6-luna`, medium reasoning

## 1. Preserve the parent plan

The original JSON remains authoritative and contains exactly 247 parent tasks. The expansion is split into one JSON file per module under `docs/tasks/subtasks/`. Each module file contains the original parent IDs and ordered child checklists. No parent is renumbered, deleted, merged, split or replaced. Child steps do not increase the parent task count.

The original dependency DAG is preserved: 247 nodes, 446 dependency edges, zero missing references and zero cycles. Astra One must revalidate these facts at import.

## 2. How the five workers execute

1. The Supervisor imports exactly 247 parent tasks into SDA `project_queue`, preserving IDs, title, module, milestone, priority, acceptance, dependencies and owner gates.
2. It loads the subtask index, then only the relevant module file for the parent being planned. Read `AGENTS.md`, `CODING_HANDBOOK.md`, `SECURITY.md`, consolidated architecture and module contract before dispatch.
3. ATLAS selects only dependency-ready parents, sorting eligible work by P0/P1/P2 and FIFO. A blocked task never blocks unrelated ready work.
4. Up to five parent tasks may be active, one per worker. A worker owns its parent and ordered subtasks in one isolated Git worktree. Do not split one parent across workers unless the Supervisor proves the child steps independent and file-disjoint.
5. Record each subtask status, output, changed paths, test command, exit code and evidence reference. A child is not complete because the model says so; its `done_when` must be demonstrated.
6. Worker commits one coherent candidate for the parent and returns candidate SHA. Worker never self-approves, merges to `develop`, pushes to `main`, deploys or changes secrets.
7. Independent QC reviews exact candidate SHA and deterministic evidence. Failed QC returns bounded actionable feedback.
8. One serialized Merger checks freshness, integrates in an isolated worktree, runs relevant regressions and updates `develop` only after review passes.
9. Parent completion requires all child steps, owner gates, QC and merge evidence.

## 3. Child task execution

Each child has a stable ID such as `CORE-004.S03`, sequence, kind, role, instruction, deliverable, completion test and dependency. Child steps are sequential by default. Audit tasks produce inventories/findings; design tasks produce contracts and test matrices; implementation tasks inspect/design/code/test; migrations pin source SHA, inventory provenance, dry-run, apply bounded changes, verify and prove rollback; verification tasks execute a declared matrix. Owner-gated tasks wait for explicit owner response. The expanded plan flags manual owner gates on BASE-008, BASE-016, SDA-027, FIN-001, FIN-016, REL-018, REL-020, REL-021 and MIG-012; do not auto-satisfy them.

The JSON index is only a manifest. The original parent plan remains the parent definition, and Astra One's SQLite ledger is the canonical live state after import. Do not create a second independent queue.

## 4. Git workflow

- `main`: protected release history only.
- `develop`: serial Merger-controlled integration.
- Worker branch: `<kind>/<module>/<TASK-ID>-<kebab-description>`.
- Commit: `<type>(<scope>): <imperative summary> [TASK-ID]`.
- One worktree and task branch per parent by default. No worker directly updates `develop` or `main`; no force push or destructive cleanup.

## 5. Model and quota behavior

Requested Linux worker profile: Codex CLI `gpt-5.6-luna`, medium reasoning, five workers. Verify actual entitlement, authentication and quota before starting. If Codex quota is exhausted, pause safely, persist state and do not consume repair attempts. Do not silently substitute Ollama or another hosted model.

Do not trigger GitHub Actions while the owner's monthly build quota is exhausted. Run available local checks and Docker no-network QC. Hosted-runner acceptance remains `DEFERRED_QUOTA`, not passed. Specifically BASE-002, BASE-003 and REL-016 cannot be marked complete from local equivalents alone.

## 6. Module guardrails

- **BASE:** preserve refs, worktrees, logs and data; read-only audit unless bounded change is authorized.
- **SDA:** one Master, five isolated worktrees, independent QC, serialized Merger.
- **MIG:** SHA-pinned create-only imports; legacy source untouched.
- **CORE:** durable per-task session plus separate event session; idempotent effects.
- **BACK:** domain-owned data, least privilege, secrets excluded from prompts/logs.
- **AUTO:** Cloudflare durable coordination and metadata only; no local inference while PCs are offline.
- **WIN:** authenticated outbound Windows agent; Ollama loopback-only; lease/reconnect safety.
- **GUARD / AEGIS:** local model receives next compatible inference slot after active generation finishes safely; no preemption; deterministic STOP independent.
- **RUN / ARCHON:** observe -> propose -> authorize -> execute -> verify; sensitive actions require approval.
- **RES:** citations, provenance, licensing and uncertainty.
- **TWS:** idempotent XP/rewards, preserve Aurelia and cross-device progress.
- **WIC:** timestamps, corrections, retractions and source ranking.
- **FIN:** Mira read-only, partner consent, no broker writes, paper-only trading.
- **REL:** candidate-SHA-bound evidence; no mock-only acceptance; explicit owner release gate.

## 7. Existing ARCHON repository

The target repository already exists as `admindeveloper4562/A.R.C.H.O.N`. SDA-027/SDA-028 must verify and use it rather than create a duplicate. Keep `main` protected and use `develop` for serial integration.

## 8. Astra One to native SDA handover

Astra One remains the external trusted builder while native SDA is built and qualified. Native SDA first runs read-only shadow mode and cannot claim Astra's live tasks or write the integration branch while Astra owns the queue. Handover requires real five-worker Codex qualification, independent QC, crash/lease recovery, STOP/PAUSE and quota restoration, duplicate-effect prevention, rollback, one-writer fencing, Guardian/watchdog validation and explicit owner approval. AEGIS cannot approve its own cutover. Keep Astra One and its state as the external rescue path until post-cutover soak and owner authorization.

## 9. Start order and pause behavior

- Run read-only import validation and host/model/quota preflight first.
- Import 247 parent tasks and attach child checklists; do not dispatch everything simultaneously.
- Begin with eligible P0 tasks, then P1 and P2 as dependencies permit.
- Preserve queue state, failed attempts and checkpoints across restarts.
- Stop early for repeated identical failures, security failures, missing permissions, quota exhaustion or owner gates. Twenty attempts is a hard upper bound, not a target.
- No production deployment, live queue migration, main promotion or active SDA switch without explicit approval.

## 10. Required handoff receipt

`task_id | parent_sha | start_sha | branch | worker_slot | completed_subtasks | changed_files | tests_and_exit_codes | candidate_sha | QC_receipt | merge_sha | blockers`

ATLAS Monitor remains a separate read-only terminal process. It must not start, stop, schedule or control Astra One.
