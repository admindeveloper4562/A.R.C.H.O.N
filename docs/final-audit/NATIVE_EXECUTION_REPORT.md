# Native execution report

## Current exact-source local model task

Tested source SHA: `fb499facad4447cb6eff7a29071364506ba100f7`; source tree: `35705fe52a47af4dac43526d2627af024905d9bf`. Environment: Python 3.12.3, Ollama 0.40.15, loopback model `qwen3:4b` with digest `359d7dd4bcdab3d86b87d73ac27966f4dbb9f5efdfcc75d34a8764a09474fae7`.

The source-module CLI ran each step as a separate Python subprocess using temporary state. Child environments set `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPATH=<temporary shim>:<checkout>/src`; a temporary `sitecustomize` shim supplied only an ephemeral test-owner public-key fixture. No production key was used. Command templates:

```sh
python -m jarvis_v2.cli init --state <temp>/state
python -m jarvis_v2.cli submit --state <temp>/state --task-file <temp>/task.json --approval-file <temp>/approval.json
python -m jarvis_v2.cli submit --state <temp>/state --task-file <temp>/bad-task.json --approval-file <temp>/bad-approval.json
python -m jarvis_v2.native_controller --state <temp>/state --repository <checkout> --ollama-model qwen3:4b --once
python -m jarvis_v2.cli result --state <temp>/state --task-id <synthetic-id>
```

In order, exit codes were `0, 0, 2, 0, 0`; the forged-signature submission was rejected. The real model marker matched, two conversation turns persisted, and atlas, runtime, and conversations SQLite integrity checks returned `ok`. Total duration was 6.709 seconds. Process-level E2E receipt SHA-256: `83c0dd243eb500ac6bc6d01b0f5522013d3a47d50fd7bd5e8b4146d18fe66c6c`.

### Unsupported-operation denial

On the same source and Python 3.12.3, a separate signed test-fixture CLI task requested the unsupported `shell` operation. The one-shot controller recorded task state `failed` with outcome `executor_failed`; the confined sentinel was not created. Duration was 1.156 seconds; log SHA-256: `14e25861fd41669d3be8f91a8a7bf6b913908274ccd9acdd44049cd9adc020f4`. This is one bounded negative-effect check, not comprehensive effect-security coverage.

### Signed cancellation CLI scenario

A separate source-module CLI flow performed fresh initialization, signed task submission, signed cancellation, and a one-shot controller invocation; each subprocess exited `0`. The persisted task state was `cancelled`, the controller was idle, no conversation turns were created, and atlas/runtime SQLite integrity checks returned `ok`. It used temporary state and an ephemeral test-owner fixture through a temporary shim. Python 3.12.3; duration 1.460 seconds; receipt SHA-256: `2716a517d5e7ca64af848682b53aefa187625deec3351d937c3706d579ab96c7`. This proves this bounded CLI cancellation case only.

The model round trip and bounded effect scenarios verify source-module subprocesses, not an installed-wheel CLI. These tasks used test-fixture keys; they do not establish production owner delegation, full module-to-module E2E, provider failover, or native SDA cutover.

## Prior full-release candidate snapshot (historical)

The following broader operations were recorded for application source `2e24790c983bf3c8d2d0f99de7a086427355f172`; they were not rerun on `fb499facad4447cb6eff7a29071364506ba100f7`. The full-production verdict remains **CONDITIONAL**.

### Verified operations on the prior candidate

- Installed wheel and sdist expose `jarvis-v2`, `atlas-monitor`, and `archon-native-controller` entry points; fresh installation, resource loading, `pip check`, and CLI checks passed on Python 3.12.3 and 3.11.18.
- Authenticated task admission used a disposable Ed25519 test identity and signed approval; caller-provided trust-store substitution was rejected.
- The isolated container completed a read-only task and an allowlisted workspace write, rejected unauthorized admission/write, cancelled a pending task, reconciled an interrupted effect after restart, and preserved state across restart.
- Container runtime used UID/GID 10001, read-only root, dropped all Linux capabilities, no-new-privileges, and network mode `none`.
- SQLite integrity passed for `atlas.sqlite3`, `effects.sqlite3`, and `runtime.sqlite3` in acceptance; the separately reloaded image passed its fresh atlas/runtime integrity checks.
- Saved image archive SHA-256: `b62e2645aef0437ab715a864f05926a3fd97273ec03d6a9c9cbd1f2768473a26`; archive reload report SHA-256: `fd22458aade184599ff2993d75a8fb489142eaca4e4a1b65201a56caa24cf46b`.

### Prior-candidate boundaries

These tests establish bounded controller/executor operations in disposable state, not arbitrary host shell execution or production owner-signing integration. Native SDA cutover, autonomous SMITH development/merge, cancellation under every process-failure timing, and unrestricted external integrations are not qualified. The host user service remains inactive.
