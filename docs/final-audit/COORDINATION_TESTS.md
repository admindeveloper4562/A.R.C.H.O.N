# Coordination and end-to-end evidence

Candidate application source: `2e24790c983bf3c8d2d0f99de7a086427355f172`.

## Executed

- Root regression: 637/637; zero failures or skips.
- Astra/ATLAS coordination suite: 191/191 passed in 60.584 seconds; log SHA-256 `88afa35ae7ec2b4551173e017d91e6b514aa75e5dbccdbd8584a96a22ad39505`.
- Container acceptance exercised fresh initialization, health, module registration, signed bounded admission, read-only work, one authorized workspace write, unauthorized admission/effect rejection, cancellation, interrupted-effect reconciliation, restart persistence, SQLite integrity, and graceful stop.
- Saved-image archive reload started a fresh container from the saved image archive and verified health, module registration, persistence databases, and graceful exit.
- Two independent verifier runs passed on the same candidate SHA; manifests and artifact hashes are recorded in the addendum.
- Image-only Compose deployment passed fresh startup, health, ten-key registration, workspace persistence across restart, UID/GID 10001, and SQLite integrity; receipt SHA-256 `b5bce93865595ada53e76f28e59f49f58067582eecbfb1dcac4485b89e27d501`.

## Scenarios not demonstrated

| Scenario | Status | Boundary |
| --- | --- | --- |
| ALFRED personal assistant through CORTEX, SAGE, and HORIZON | NOT RUN end to end | No single user request traversed all modules and produced a persisted, audited answer. |
| SMITH autonomous change, tests, independent QC, PR, and merge | NOT RUN end to end | Unit and bounded execution tests do not prove runtime code-to-merge operation. |
| Independent AEGIS process failure and rollback | NOT QUALIFIED | No independently protected watchdog or verified unattended rollback. |
| Controlled-clock RELAY scheduling and recovery | NOT RUN end to end | No clock-controlled dispatch through ATLAS and restart reconciliation. |
| Multi-hour normal-use operation | NOT RUN | The bounded 72-task local inference/data soak lasted 491.427 seconds on the identical runtime source subtree, not the exact whole-source candidate. |

The tested SQLite task ledger also contains incomplete historical child receipts; see [AEGIS_RECOVERY_REPORT.md](AEGIS_RECOVERY_REPORT.md). Overall verdict remains CONDITIONAL.
