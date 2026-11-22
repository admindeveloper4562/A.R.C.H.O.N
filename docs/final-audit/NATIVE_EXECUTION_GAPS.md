# Native execution gaps

## Current exact-source evidence

On source `fb499facad4447cb6eff7a29071364506ba100f7` (tree `35705fe52a47af4dac43526d2627af024905d9bf`), a process-level source-module CLI flow initialized disposable state, admitted a valid signed test-fixture task, rejected a forged-signature task, ran the native controller once against real loopback Ollama `qwen3:4b`, and read back persisted output. All expected subprocess exit codes and SQLite integrity checks passed. See [NATIVE_EXECUTION_REPORT.md](NATIVE_EXECUTION_REPORT.md) for command templates and the receipt hash. This does not establish installed-wheel CLI behavior or production owner delegation.

A separate signed test-fixture task requested the unsupported `shell` operation. The one-shot controller recorded state `failed` with outcome `executor_failed`, and a confined sentinel was not created (1.156 seconds; log SHA-256 `14e25861fd41669d3be8f91a8a7bf6b913908274ccd9acdd44049cd9adc020f4`). This is one bounded unsupported-operation denial check, not comprehensive effect-security qualification.

A separate signed-cancellation CLI scenario completed init, submit, cancel, and one-shot controller subprocesses with exit `0`; the task remained `cancelled`, the controller was idle, no model turns were written, and atlas/runtime integrity was `ok`. This demonstrates that bounded cancellation scenario only (1.460 seconds; receipt SHA-256 `2716a517d5e7ca64af848682b53aefa187625deec3351d937c3706d579ab96c7`).

The same exact source passed two cross-module manifest/permission/event-contract fixture tests (0.287 seconds, temporary fixture database); these checks do not establish operational module coordination. The test command and log hash are recorded in [COORDINATION_TESTS.md](COORDINATION_TESTS.md).

## Still unqualified

Production owner-delegation transport, arbitrary agent/module operation, autonomous SMITH code-to-merge, independent AEGIS, trusted rollback, service activation, and external side effects remain unqualified. No full release suite or independent QC was reported for source `fb499facad4447cb6eff7a29071364506ba100f7` as part of this targeted update.

## Prior candidate snapshot (historical)

Application source `2e24790c983bf3c8d2d0f99de7a086427355f172` previously qualified bounded authenticated task admission, signed test approval, allowlisted workspace effects, rejection, cancellation, idempotent receipt handling, and restart reconciliation in disposable Linux/container state. Those results are not transferred to the current source. See [AEGIS_RECOVERY_REPORT.md](AEGIS_RECOVERY_REPORT.md) for recovery boundaries.
