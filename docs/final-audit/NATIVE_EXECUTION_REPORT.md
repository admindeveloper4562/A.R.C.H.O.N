# Native execution report

Candidate application source: `2e24790c983bf3c8d2d0f99de7a086427355f172`. Result: bounded Linux execution **PASS**; full production operation **CONDITIONAL**.

## Verified operations

- Installed wheel and sdist expose `jarvis-v2`, `atlas-monitor`, and `archon-native-controller` entry points; fresh installation, resource loading, `pip check`, and CLI checks passed on Python 3.12.3 and 3.11.18.
- Authenticated task admission used a disposable Ed25519 test identity and signed approval; caller-provided trust-store substitution was rejected.
- The isolated container completed a read-only task and an allowlisted workspace write, rejected unauthorized admission/write, cancelled a pending task, reconciled an interrupted effect after restart, and preserved state across restart.
- Container runtime used UID/GID 10001, read-only root, dropped all Linux capabilities, no-new-privileges, and network mode `none`.
- SQLite integrity passed for `atlas.sqlite3`, `effects.sqlite3`, and `runtime.sqlite3` in acceptance; the separately reloaded image passed its fresh atlas/runtime integrity checks.
- Saved image archive SHA-256: `b62e2645aef0437ab715a864f05926a3fd97273ec03d6a9c9cbd1f2768473a26`; archive reload report SHA-256: `fd22458aade184599ff2993d75a8fb489142eaca4e4a1b65201a56caa24cf46b`.

## Boundaries

These tests establish bounded controller/executor operations in disposable state, not arbitrary host shell execution or production owner-signing integration. Native SDA cutover, autonomous SMITH development/merge, cancellation under every process-failure timing, and unrestricted external integrations are not qualified. The host user service remains inactive.
