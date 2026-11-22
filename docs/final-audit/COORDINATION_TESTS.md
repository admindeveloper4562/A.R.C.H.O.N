# Coordination and end-to-end evidence

## Current targeted evidence on develop

All current runs below used exact source SHA `fb499facad4447cb6eff7a29071364506ba100f7`, tree `35705fe52a47af4dac43526d2627af024905d9bf`.

- Native source-module CLI E2E: separate Python subprocesses performed fresh init (0), signed submit (0), forged-signature submit (2/rejected), native controller `--once` (0), and persisted result readback (0). The actual `qwen3:4b` marker matched; two conversation turns persisted; atlas/runtime/conversations SQLite integrity was `ok`. Python 3.12.3, Ollama 0.40.15, model digest `359d7dd4bcdab3d86b87d73ac27966f4dbb9f5efdfcc75d34a8764a09474fae7`; 6.709 seconds. A temporary `sitecustomize` shim injected only an ephemeral test-owner public-key fixture. This was source-module CLI execution, not an installed-wheel CLI or production owner delegation. Receipt SHA-256: `83c0dd243eb500ac6bc6d01b0f5522013d3a47d50fd7bd5e8b4146d18fe66c6c`.
- Unsupported-operation denial: a separate signed test-fixture task requested `shell`; the one-shot controller recorded state `failed`, outcome `executor_failed`, and a confined sentinel was not created. Duration 1.156 seconds. This is one bounded negative-effect check, not comprehensive effect-security coverage. Log SHA-256: `14e25861fd41669d3be8f91a8a7bf6b913908274ccd9acdd44049cd9adc020f4`.
- Signed cancellation: source-module CLI subprocesses performed fresh init, signed submit, signed cancel, and one-shot controller invocation with exit `0` for each. Persisted state was `cancelled`, controller idle was true, conversation turns were zero, and atlas/runtime SQLite integrity was `ok`. Temporary state and ephemeral test-owner shim; Python 3.12.3; 1.460 seconds. This is only the bounded cancellation case. Receipt SHA-256: `2716a517d5e7ca64af848682b53aefa187625deec3351d937c3706d579ab96c7`.
- Cross-module contracts: `python3 -m unittest tests.test_rel_cross_module_contracts -v`; 2/2 passed in 0.287 seconds using a temporary fixture database. Coverage is limited to manifest, permission, and event-contract fixtures; it is not module-operation E2E. Log SHA-256: `5abbda4639efe0487c5d9ef8335ce87174b95b2f8f797765a39efed7550dc7eb`.

These targeted runs do not constitute a full regression, release, or independent-QC result for this source. The results below belong to a prior candidate and remain historical.

## Prior full-release candidate evidence (historical)

Candidate application source: `2e24790c983bf3c8d2d0f99de7a086427355f172`.

### Executed on the prior candidate

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
