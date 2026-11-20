# ARCHON system status

## Project

- Canonical source: `/home/r34p3r/dev/A.R.C.H.O.N`
- Final local/remote feature SHA: `2fec1e3459252f97fe900a6ade2d15e48894c70b`
- Implementation SHA whose production source is unchanged by the final documentation commits: `4149c1d75eee24880bfacd819342f9c21d05d51a`
- Git publication: feature branch is published and matches `origin/feature/astra-linux-integration-c799784769`; `main` remains `5227b91d`, and remote `develop` remains `75582db`
- Git state: clean at last verification; no force-push or history rewrite
- Package version: `0.0.3`
- Exact-current-SHA regression run: 590 passed, 0 failed, 0 errors, 29.365 seconds; log `/home/r34p3r/.local/state/archon/logs/unittest-2fec1e3.log`
- Native import sweep: 106 modules, 0 import errors (prior verified evidence; production source unchanged)
- Search index: FTS5 available, 552 files indexed from 553 cataloged files; 3,920 symbols, 904 functions, 2,448 methods, 568 classes, 0 parser errors

## Historical ledger

The historical Astra SQLite ledger remains separate from fresh runtime state: 247 parents = 240 completed + 7 archived/deferred; 1,359 children; 1,281 verified receipt rows; SQLite integrity previously verified `ok`. The fresh runtime does not load or copy this ledger.

## Fresh native runtime

`/home/r34p3r/.local/state/archon` was reset from zero and initialized from current schemas. Runtime and ATLAS databases each have one migration, zero queue tasks, integrity `ok`, and zero foreign-key violations. Native health is `healthy`; runtime files are mode `600`; historical ledger loading is `false`. The provenance-bound code index and metadata-only host inventory were rebuilt in the fresh state.

The bounded executor exposes eight read-only probes: capability disclosure, module health, runtime health, inventory digest, queue status, named database inspection, SDA handoff readiness, and Guardian readiness. Domain-effect handlers remain fail-closed; unrestricted shell, filesystem-write, network, finance, communication, service-control, and rollback authority is not enabled.

## Module status

| Module | Status | Evidence boundary |
| --- | --- | --- |
| ALFRED / Core | PASS local | Queue, events, registry and native controls verified |
| SMITH / SDA | PARTIAL | Bounded handoff and queue probes pass; native SDA ownership is not enabled |
| CORTEX / Backend | PASS local | Storage, authorization, backup, FTS5 and migration contracts verified |
| IRIS / Runtime | PARTIAL | Local runtime contracts pass; desktop/browser/device execution not run |
| SAGE / Research | PARTIAL | Local research/RAG contracts pass; live providers not run |
| LUMEN / TWS | PARTIAL | Local model/storage contracts pass; Blender/device evidence absent |
| HORIZON / WIC | PARTIAL | Local provenance contracts pass; live feeds not run |
| CROWN / Finance | PASS paper/read-only | No real accounts or transactions initialized |
| PALADIN / Guardian | PARTIAL | Local recovery contracts pass; trusted external watchdog absent |
| RELAY / Automation | PARTIAL | Scheduler/lease/recovery contracts pass; unattended external actions absent |

## Services and Astra boundary

The native systemd unit passes static verification but is not installed or enabled. The legacy Astra timer and service unit are now absent, inactive, and no Astra monitor/batch process remains. Native one-shot and health checks pass without importing or invoking Astra. Historical Astra state and worktrees remain retained for provenance/recovery; native unattended SDA/AEGIS/watchdog cutover has not been claimed.

## Inventory

The private host inventory is metadata-only and bounded at 10,000 root entries. It excludes `/home`, virtual filesystems, unrelated mount traversal, and symlink recursion; it records 17 permission-denied paths, 28 skipped mounts, 4 skipped virtual filesystems, and 3,459 pending continuation frames in `/home/r34p3r/.local/state/archon/host_inventory_cursor.json`. Coverage is intentionally incomplete. Available local model identities are `qwen3:4b`, `qwen2.5-coder:7b`, and `qwen2.5-coder:3b`; NVIDIA inventory reports a GTX 980 with 4,096 MiB and driver 535.309.01.

## Cleanup

The exact cleanup batch reclaimed 2,838,614,016 bytes. It removed only verified legacy Astra backup/checkpoint/toolchain directories, two unreferenced ARCHON Docker images, and obsolete Astra user units. Historical receipts, unique worktrees, the verified final-audit checkpoint, and the byte-for-byte native reset quarantine remain. See `CLEANUP_MANIFEST.json` and `DISK_CLEANUP_REPORT.md`.

## Overall state

The approved local Linux contracts are operational for the tested scope. The final verdict remains **CONDITIONAL**: native side-effecting execution, signed owner-approval transport, unattended SDA/AEGIS ownership, trusted watchdog activation/soak, rollback application, and external-device/provider acceptance remain unverified.
