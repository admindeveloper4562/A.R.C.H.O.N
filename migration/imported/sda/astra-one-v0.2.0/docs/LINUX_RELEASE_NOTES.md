# Astra One Linux v0.2.0 — Development handoff

## Built

- Deterministic Linux SQLite control plane, architecture hash gate, DAG task queue, separate 0600 local database and private 0700 state.
- Five truly concurrent worker slots, each launching normal authenticated Codex CLI `gpt-5.6-luna` `medium`, isolated branch/worktree, without `--oss`; native child-agent spawning disabled so worker count is bounded.
- Read-only Supervisor task proposal via Codex; plans must be explicitly queued after owner review.
- Independent QC agent, fail-closed source safeguards, Docker `--network none --read-only` test command, read-only Merger agent and serialized local Git integration.
- Bounded Repairer retry attempts, STOP/PAUSE/PAUSED_QUOTA, lock-based single Master, interrupted-run recovery, Cloudflare metadata-only event outbox.
- Existing compatible D1 dashboard rebranded for Linux Codex. It cannot command a PC.

## Known limitations

- Actual model subscription entitlement, five parallel ChatGPT Codex sessions, real Docker runtime and live GitHub source integration have **not been tested in this environment**.
- Candidate acceptance relies on test quality and independent reviews, which may miss defects. No forced cloud deployment/push is possible through this runner.
- Docker requires secure host configuration. An unprivileged VM/runner is strongly recommended.
- Model switch continuity, automated critical mirror/failover, OS-level recovery, and production self-updates are **not implemented**.
- Final JARVIS v2 architecture must be supplied, imported, explicitly approved and converted to reviewable task plans before work starts.
