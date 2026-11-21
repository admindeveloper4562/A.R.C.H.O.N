# AEGIS and recovery report

Candidate application source: 759e78dc04c61ed7f01a4b714d35ab8c999d2a85. Result: bounded container recovery evidence PASS; independent Guardian recovery is not qualified.

## Verified recovery evidence

- Clean-container acceptance covered cancellation, restart, persistent volumes, interrupted-effect recovery, fresh health, and SQLite integrity.
- Saved-image archive reload returned healthy status at the exact candidate SHA.
- These checks exercise bounded ARCHON controller/runtime behavior. They do not establish an independent AEGIS process or trusted watchdog.

## Current canonical host state

Read-only snapshot at 2026-11-22 03:03:40 +07; the canonical database was not modified. PRAGMA integrity_check and quick_check returned ok; foreign_key_check found zero violations. ARCHON-JARVIS-V2 had 247 parents (240 completed, 7 archived) and 1,359 subtasks (1,319 completed, 40 archived). There were 1,281 receipt rows covering 1,276 distinct children; 43 completed children lacked receipts, with archived children excluded from that missing-receipt count. The project queue had one item and zero pending/review/merge items; no active, blocked, or queued controller task was present. Three recorded supervisor lanes were idle; process liveness was unknown. No STOP/PAUSE/PAUSED_QUOTA markers were present. The host user service and Astra runner/timer were inactive.

## Not qualified

- Independent AEGIS/watchdog survival when the monitored controller fails.
- Unattended restart after repeated crash or host reboot.
- Lease fencing under independent Guardian recovery.
- Trusted rollback application, signed deployment identity, failback, and rollback soak.
- Production signed owner approval and native SDA cutover.

Do not interpret bounded container recovery as permission to enable unattended recovery.
