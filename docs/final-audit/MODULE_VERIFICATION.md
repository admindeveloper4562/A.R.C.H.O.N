# Module verification

Status meanings: PASS is real local functionality verified; PARTIAL means local contracts pass but required external or release evidence is incomplete; BLOCKED means the required environment was unavailable; N/A is outside the approved Linux scope.

| ID | Agent | Functional status | Security | Integration | Evidence |
| ---: | --- | --- | --- | --- | --- |
| 01 | ALFRED / Core | PASS local | PASS | PASS local queue/events | Core transition, fault, session, and registry tests |
| 02 | SMITH / SDA | PARTIAL | PASS shadow handoff | PARTIAL | Candidate `4149c1d` adds bounded queue/database probes and resumable inventory; domain-effect execution and complete unattended native SDA cutover remain unproven |
| 03 | CORTEX / Backend | PASS local | PASS | PASS local storage/contracts | Backend tests, FTS5 index, migration and restore |
| 04 | IRIS / Runtime | PASS local | PASS | PARTIAL | Runtime tests and imports; no real desktop/browser/device run |
| 05 | SAGE / Research | PASS local | PASS | PARTIAL | Research and RAG tests; no live provider run |
| 06 | LUMEN / TWS | PARTIAL | PASS local | PARTIAL | Model/lifecycle/storage tests; Blender/device evidence absent |
| 07 | HORIZON / WIC | PASS local | PASS | PARTIAL | Provenance, source, alert and world tests; live feeds not run |
| 08 | CROWN / Finance | PASS paper/read-only | PASS | PARTIAL | Finance tests; real accounts and transactions excluded |
| 09 | PALADIN / Guardian | PASS local | PASS local | PARTIAL | Guardian fault/recovery tests; trusted external watchdog cutover absent |
| 10 | RELAY / Automation | PASS local | PASS | PARTIAL | Scheduler/lease/recovery tests; no unattended external action |

## Supporting systems

- ATLAS: PASS for native queue schema, read-only monitor, and the native controller's one-shot, fencing, marker, receipt, eight bounded read-only probes, resumable inventory cursor, and restart checks; no live native service is installed and domain-effect handlers remain unconfigured. Evidence is bound to `4149c1d`.
- AEGIS: PASS for local Guardian recovery contracts; external trusted watchdog activation/soak not demonstrated.
- ASEL: PASS for local policy, secret, path, and command-boundary tests.
- Model gateway: PASS for registry/routing/fallback contracts; no real provider call.
- Persistent memory/RAG: PASS for local storage/retrieval fixtures; no live corpus/provider acceptance.
- Event bus: PASS local idempotency and persistence tests.
- Tool/MCP integrations: PARTIAL; typed local boundaries pass, live external tools were not invoked.
- Service management: PARTIAL; the native unit candidate passes systemd verification but is not installed, while the legacy timer remains active. Service qualification is reversible/read-only only; no watchdog activation or cutover was performed.
- Database persistence: PASS for fresh databases, migration, integrity, foreign keys, and backup/restore.
