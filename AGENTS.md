# ARCHON / AEGIS / ATLAS — Codex / SDA Agent Contract

ARCHON = main AI (intelligent Core/Runtime); AEGIS = local Guardian; ATLAS = deterministic Core/Backend/SDA/Cloudflare infrastructure. See docs/architecture/IDENTITIES.md.

Read `docs/architecture/JARVIS_V2_CONSOLIDATED.md`, `CODING_HANDBOOK.md`, `SECURITY.md`, the relevant module contract, and the current reviewed task before changing code. The old `personal-jarvis` repository is reference source, never a production write target.

SDA's five Codex workers operate in isolated Git worktrees. Supervisor prepares a bounded plan, deterministic Master owns the task ledger and locks, QC independently validates, and one serialized Merger integrates only proven compatible changes into `develop`. Workers **cannot** approve their own code, CI, handbook exceptions, deployments, secrets, or protected branch changes.

Astra One is the external bootstrap controller. Native JARVIS v2 SDA can be switched to only after independently verified real coding, recovery, STOP/PAUSE, rollback, and owner approval. The new Guardian is an independent local intelligence process backed by deterministic trusted watchdog. In-flight model generation is not forcibly interrupted for Guardian scheduling.

Do not delete files, modify live databases, send external messages, execute trades, turn off safeguards, bypass STOP/PAUSE/quota, create model fallbacks without permission, push protected branches, deploy, or change access scope without the required approvals. No bulk file deletion approvals. Keep per-file deletion audits in `DELETE-LOGS.md`.

Do not claim an implementation is complete on the basis of mock tests or model text. Report `task ID | start SHA | branch | changed files | checks | evidence | state | blocker`. Use `tests/` and service-specific checks. Preserve source attribution and security boundaries when importing legacy code.

ATLAS Monitor (`python3 tools/atlas_monitor.py`) is a **separate read-only process**. Do not make it a runner dependency, change its side-effect-free contract, or let it reconstruct fabricated worker slots.
