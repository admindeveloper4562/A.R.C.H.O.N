# Module acceptance

Candidate application source: `2e24790c983bf3c8d2d0f99de7a086427355f172`. Container module registration and unit/component tests passed, but the saved image reports every module state as `planned`. No module is fully accepted for end-to-end operational use.

| Module | Key | Evidence | Status |
| --- | --- | --- | --- |
| ALFRED | core | Regression and CLI tests; no end-to-end personal-assistant request across modules. | PARTIAL |
| SMITH | sda | Bounded signed task execution and coordination regression; autonomous code, independent QC, PR, and merge not demonstrated. | PARTIAL |
| CORTEX | backend | Fresh SQLite integrity, persistence and bounded storage tests; full ALFRED-to-RAG workflow not demonstrated. | PARTIAL |
| IRIS | runtime | Allowlisted workspace effect, denial, cancellation and restart recovery passed; browser/desktop/hardware adapters not accepted. | PARTIAL |
| SAGE | research | Component regression passed; no complete sourced research request delivered through ALFRED. | PARTIAL |
| LUMEN | tws | Registration and component tests only; Blender execution and Windows/Apple support not verified. | PARTIAL |
| HORIZON | wic | Registration and component tests only; live-feed provenance/reconnect path not exercised. | PARTIAL |
| CROWN | finance | Paper/read-only boundaries remain; no live account or transaction effect was enabled. | PARTIAL |
| PALADIN | guardian | Rejected unauthorized effects and recovered an interrupted effect; independent AEGIS watchdog and rollback not qualified. | PARTIAL |
| RELAY | automation | Schedule/component tests passed; controlled-clock dispatch through ATLAS and durable restart was not qualified. | PARTIAL |

Evidence and limitations: [QUALIFICATION_ADDENDUM_2E24790.json](QUALIFICATION_ADDENDUM_2E24790.json). The ten keys are core, sda, backend, runtime, research, tws, wic, finance, guardian, and automation.
