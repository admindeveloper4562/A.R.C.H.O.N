# ARCHON system status

## Project

- Canonical source: `/home/r34p3r/dev/A.R.C.H.O.N`
- Exact candidate/source/implementation SHA: `4149c1d75eee24880bfacd819342f9c21d05d51a`
- Git state: tested source candidate is 36 commits ahead of `origin/feature/astra-linux-integration-c799784769`; latest documentation overlay `0d6658b` is 38 ahead; both are 0 behind and unpublished
- Package version: `0.0.3`
- Full regression: 590 passed, 0 failed, 27.762 seconds; log `/home/r34p3r/.local/state/archon/logs/unittest-4149c1d.log`
- Native import sweep: 106 passed, 0 errors
- Search index: FTS5 available, 552 files indexed from 553 cataloged files; 347 source files, 3,920 symbols, 904 functions, 2,448 methods, 568 classes, 0 parser errors
- Index provenance: rebuilt from latest evidence snapshot `0d6658b0aa2449c4071c0ca05ddda0aad3609bd2`; implementation source remains `4149c1d75eee24880bfacd819342f9c21d05d51a`
- Historical ledger: SQLite integrity `ok`; 247 parents = 240 completed + 7 archived/deferred; 1,359 children; 1,281 receipt rows

## Native runtime and modules

The fresh native state root is `/home/r34p3r/.local/state/archon`. It contains the native runtime and ATLAS databases, the provenance-bound code index, private host metadata, logs, cache, run and control directories. Historical Astra state and personal/financial records were not copied. Native health reports `healthy`, queue total 0, integrity `ok`, zero foreign-key violations, and historical ledger loading `false`.

The bounded executor supports eight read-only probes: `native_capabilities`, `module_health`, `runtime_health`, `inventory_digest`, `queue_status`, `database_inspect`, `sda_handoff_status`, and `guardian_readiness`. Queue leases, stale-lease rejection, idempotent completion, process fencing, STOP/PAUSE/PAUSED_QUOTA admission, failure receipts, and restart behavior are exercised by the current test suite. Side-effecting domain handlers remain fail-closed.

| Module | Current status | Evidence boundary |
| --- | --- | --- |
| ALFRED / Core | PASS local | Queue, events, registry and native controls verified |
| SMITH / SDA | PARTIAL | Shadow handoff and bounded queue probes pass; live native SDA ownership is not enabled |
| CORTEX / Backend | PASS local | Storage, authorization, backup, FTS5 and migration contracts verified |
| IRIS / Runtime | PARTIAL | Local runtime contracts pass; desktop/browser/device execution not run |
| SAGE / Research | PARTIAL | Local research/RAG contracts pass; live providers not run |
| LUMEN / TWS | PARTIAL | Local model/storage contracts pass; Blender/device evidence absent |
| HORIZON / WIC | PARTIAL | Local provenance contracts pass; live feeds not run |
| CROWN / Finance | PASS paper/read-only | No real accounts or transactions initialized |
| PALADIN / Guardian | PARTIAL | Local recovery contracts pass; trusted external watchdog absent |
| RELAY / Automation | PARTIAL | Scheduler/lease/recovery contracts pass; unattended external actions absent |

## Services and legacy boundary

`infra/systemd/archon.service` passes `systemd-analyze verify` but is not installed or enabled. Native service activation remains gated on independent recovery/watchdog qualification and owner-approved cutover. `archon-astra.timer` remains active and enabled; `archon-astra.service` is inactive at the observation, and read-only Astra monitor PID 20774 remains. No Astra service, timer, database, or process was modified.

## Inventory

The root filesystem inventory is metadata-only, bounded at 10,000 entries, and recorded 17 permission-denied paths, 28 mount boundaries, and four skipped virtual filesystems without following symlinks. A fresh private cursor at `/home/r34p3r/.local/state/archon/host_inventory_cursor.json` records 1,328 pending directory frames for resumable continuation. Root coverage is therefore explicitly incomplete.

## Overall state

The approved local Linux contracts are operational for the tested scope. The installation is not yet a fully retired standalone release: native unattended SDA/Guardian cutover, trusted watchdog soak, independent exact-SHA QC, remote publication, external-device acceptance, and owner-approved disk cleanup remain open.
