# Native execution report

Candidate application source: 759e78dc04c61ed7f01a4b714d35ab8c999d2a85. Result: bounded Linux execution PASS; production operation CONDITIONAL.

## Verified operations

- Version 0.0.3 wheel and source distribution were built reproducibly. Duplicate builds had matching hashes; fresh package, CLI, and pip checks passed in the Python 3.12.3 environment.
- The local CI workflow exercised jarvis-v2, atlas-monitor, and archon-native-controller entry points, health, module listing, initialization, bounded admission, and controller operation.
- Clean-container acceptance verified fresh runtime initialization and health; read-only task execution; one approved workspace write; rejection of unauthorized admission and write; cancellation; interrupted-effect recovery; persistence; restart; and graceful shutdown.
- Container databases atlas.sqlite3, effects.sqlite3, and runtime.sqlite3 passed integrity checks.
- Saved image archive reload passed at exact source 759e78dc04c61ed7f01a4b714d35ab8c999d2a85. The ten module names registered, with every state planned.
- The test authorization used an ephemeral test-only signing identity, not a production owner key.
- A focused runbook test executed the backup and restore snippets against disposable state/workspace directories and verified that all three control markers survive with restrictive permissions and force safe_mode. The full verifier for the follow-up candidate is pending.

## Boundaries and gaps

- Local Ollama inference and an extended inference soak were not evidenced for exact source 759e78dc04c61ed7f01a4b714d35ab8c999d2a85.
- The declared Python requirement is >=3.11, but this exact-candidate bundle records verification under Python 3.12.3 only; Python 3.11 install qualification is unavailable here.
- Production signed owner delegation, production approval transport, native SDA cutover, and unattended task execution are not qualified.
- Independent AEGIS watchdog activation and protected rollback are not qualified.
- No host user service was activated by this qualification. Host service status was not refreshed in this evidence bundle.
- Full module workflows and cross-module assistant, autonomous-development, and controlled-clock automation scenarios remain unverified.
