# AEGIS Guardian recovery and safe redeployment policy

Guardian consists of: (a) **deterministic trusted recovery/deployment controller**, (b) local AI diagnostic model at next available inference slot, (c) **external minimal watchdog** outside the mutable JARVIS process and its worker credentials. A model is *never* the sole controller of startup, STOP, production writer fencing or deployment permissions.

## Non-preemptive priority
On Guardian incident, reserve the next compatible idle inference slot after ongoing bounded generation finishes. Prevent new lower-priority model requests while waiting. Deterministic P0 safety isolation, when specifically preauthorized, does not wait for a model. This is not permission to kill a healthy coding worker or bypass owner STOP.

## Update protocol (blue/green)
1. SDA builds candidate in isolated worktree with pinned sources and signed/checksummed artifact manifest.
2. Independent QC and static/security checks pass; target ABI/schema compatible with current state, or a reversible migration is tested.
3. Owner explicitly approves sensitive production promotion, especially Guardian itself, SDA and canonical DB.
4. External trusted deploy controller confirms approval, no other deploy in progress, and immutable last-known-good rollback artifact.
5. Stage candidate in inactive `blue`/`green` slot; start it with read-only mirrored state; health/readiness + task checkpoint smoke tests pass.
6. Fence old writer and verify a single lease authority; atomically route new work to healthy slot. Track exact artifact digest.
7. During soak, verify audit/heartbeat/checkpoints and user STOP/PAUSE. On failure, deterministic watchdog fences new slot, reverses traffic, restores previous compatible state and emits a recovery incident.
8. Never delete old artifacts or records merely because an upgrade succeeded.

## Guardian updating *itself*
The Guardian AI cannot directly redeploy its own watchdog or alter its own approval policy. An **immutable or separately managed bootstrap watchdog**, installed by an owner using OS service manager permissions, validates a trusted release, deploys an inactive Guardian slot, health-checks and switches. If both Guardian versions fail, enter safe degraded mode and alert owner. New Guardian code cannot mark its own tests/approvals true.

The current seed includes **candidate inspection and policy tests only**, not production systemd units, artifacts signature verification, atomic symlink switching, leader-election fencing or real rollback. Those are standalone reviewed SDA tasks and must pass fault-injection acceptance before activation.
