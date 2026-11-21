# Module acceptance

Candidate application source: 0ae26d563e5998a9390588feb58eb3d5c0081ffb. The clean container registered ten configured modules. The root suite passed 626 tests, but it does not emit stable per-module counts. “Contract pass” means the module-level tests in that suite passed; it does not mean every production connector or cross-module workflow was exercised.

| User-facing module | Registered module | Result | Evidence and limit |
|---|---|---|---|
| ALFRED | core | Contract PASS; full workflow PARTIAL | Core planning, task admission, queue, and response contracts passed. No single user goal traversed all requested modules and produced a persisted audited answer. |
| SMITH | sda | Contract PASS; autonomous release flow NOT RUN | SDA tests and local REL-016 workflow checks passed. No runtime task generated a change, requested independent QC, opened a PR, and merged it end to end. |
| CORTEX | backend | Contract PASS; integrated RAG PARTIAL | Storage, migration, conversation persistence, integrity, backup/restore, and database-inspection tests passed. No complete ALFRED-to-SAGE retrieval scenario was run. |
| IRIS | runtime | Contract PASS; optional adapters DEFERRED | Capability and sandbox contracts, cancellation, local inference adapter, and native task path passed. Browser/desktop automation and hardware adapters were unavailable or not exercised. |
| SAGE | research | Contract PASS; live research NOT RUN | Research, provenance, sanitization, and retrieved-content safety contracts passed. No live external research connector was used. |
| LUMEN | tws | Contract PASS; Blender execution NOT RUN | TWS module contracts and registration passed. Blender asset/animation execution and Windows/Apple compatibility were not verified. |
| HORIZON | wic | Contract PASS; live feeds NOT RUN | Provenance and information-handling contracts passed. Feed ingestion/reconnect with an authorized live source was not tested. |
| CROWN | finance | Paper/read-only contracts PASS | Finance calculation and boundary tests passed. No external account, trade, transfer, or live financial action was used. |
| PALADIN | guardian | Local contracts PASS; independent watchdog NOT QUALIFIED | Guardian, health, control, and recovery contracts passed. No separately protected AEGIS process, trusted watchdog activation, or rollback soak was demonstrated. |
| RELAY | automation | Contract PASS; cross-module schedule PARTIAL | Schedule and queue contracts passed. A controlled-clock schedule through ATLAS dispatch, module execution, and restart was not run end to end. |

No module uses Astra One as a runtime dependency. Local inference is optional; the core container starts without Ollama and reports that capability as unavailable. Windows, Apple, GPU-specific Blender, external provider, live feed, financial, and communications integrations remain separate validation targets.
