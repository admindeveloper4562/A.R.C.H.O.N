# Git branches, commits, and release convention

## Protected branches
- `main` — immutable accepted releases only, tagged `v2.0.0` etc.
- `develop` — single serial Merger-controlled integration branch; CI and review required.
- `release/2.0.0` — release hardening only, never bypasses main approvals.

## Worker branches
**Pattern:** `<kind>/<module>/<TASK-ID>-<kebab-description>`

Kinds: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `recovery`, `experiment`, `hotfix`.
Modules: `core`, `sda`, `backend`, `runtime`, `research`, `tws`, `wic`, `finance`, `guardian`, `automation`, `platform`, `migration`.

Examples:
- `feat/core/CORE-004-durable-task-sessions`
- `feat/sda/SDA-014-codex-worker-receipts`
- `fix/guardian/GUARD-006-model-slot-fairness`
- `refactor/runtime/RUN-005-stream-cancellation`
- `recovery/sda/SDA-020-checkpoint-resume`
- `docs/migration/MIG-003-source-provenance`

Do not create branch names with spaces, owner names, dates unless needed, or ambiguous `worker1`/`final` suffixes. Never reuse a task branch for a different task. Auto-created workspace names use a stable task ID plus generation `-g2`, not untraceable timestamps.

## Commit format
**Conventional Commit:** `<type>(<scope>): <imperative summary> [TASK-ID]`

Examples:
- `feat(core): persist task event sessions [CORE-004]`
- `fix(sda): prevent duplicate task claims [SDA-006]`
- `test(guardian): cover non-preemptive priority [GUARD-006]`
- `docs(migration): record legacy Workhorse source SHA [MIG-003]`

Allowed types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `build`, `ci`, `revert`. Scope should match a module or `repo`, `security`, `migration`. Summary starts lowercase, uses imperative wording, no trailing period, max 72 characters before task suffix. Breaking APIs add `!` and migration docs. Initial repository commit may use `chore(repo): establish clean foundation [MIG-001]`.

## PR title
`[TASK-ID] <Module>: <Short outcome>` e.g. `[CORE-004] Core: durable task sessions`. Use PR template; no squash-only assumption—preserve source provenance and reviewer receipt.

## Versioning
Semantic versions `2.0.0`, `2.0.1`, `2.1.0` (no zero padding); tag `v2.0.0`. Do not label scaffold `2.0.0` before full release gates.
