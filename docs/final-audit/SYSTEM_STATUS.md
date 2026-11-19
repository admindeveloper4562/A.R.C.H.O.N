# ARCHON system status

## Project

- Canonical source: /home/r34p3r/dev/A.R.C.H.O.N
- Source SHA: 239e10154e1c81b4ff463cdd796e04f0dbc68407
- Implementation SHA: eef1e3c8d1bfd3ea6a3dc7e1b06ac2daa3e21767
- Git origin: https://github.com/admindeveloper4562/A.R.C.H.O.N.git; target SHA is not published to GitHub; direct refs observed: main=5227b91d2725bf4be4336a5ad26189fdf1034704, develop=75582dbf48057e3d5b0e7cf4acfdba2386acfcff
- Git state: tested tree 239e101; implementation commit eef1e3c8; final documentation refresh is local-only and not published to GitHub
- Version in package metadata: 0.0.3
- Full regression: 579 passed
- Native import sweep: 106 passed
- Fresh runtime DBs: integrity and restore checks passed
- Search index: FTS5 available, 548 files indexed from 549 cataloged files, four representative queries returned results including deployment files

## Runtime

The native state root is /home/r34p3r/.local/state/archon. It contains empty runtime and ATLAS queue databases, private host inventory metadata, the code index, empty logs/cache directories, and private controller lock/control directories. It does not contain the historical 247-task ledger or personal/financial data. Native health reports the runtime healthy with zero queue tasks and historical ledger loading false. The native controller passed fresh one-shot, fencing, marker, receipt, terminate/restart, and systemd verification checks; its default domain executor is unconfigured and its unit is not installed.

The historical Astra boundary remains active and requires controlled retirement: archon-astra.timer is enabled and active; the latest transient archon-astra.service run exited 0 and is now inactive, but its journal recorded the legacy monitor rejecting incompatible `--json` plus `--watch` arguments before the legacy batch completed; and the read-only legacy monitor process remains running as PID 20774 at the final observation.

## Inventory

The bounded inventory scanned 10,000 metadata entries from the root filesystem, recorded 17 permission-denied paths, skipped 28 mount boundaries, skipped /dev, /proc, /run, and /sys, did not follow symlinks, and stopped at its explicit bound. It captured Ollama models `qwen3:4b`, `qwen2.5-coder:7b`, and `qwen2.5-coder:3b`, plus NVIDIA GeForce GTX 980 acceleration with driver 535.309.01; unavailable VA-API, ROCm, and OpenCL probes were recorded. It is private at mode 0600 and contains metadata only.

## Overall state

The Linux native code and local contracts are operational for the tested scope. The installation is not yet a clean fully retired standalone release because native unattended SDA/Guardian cutover, remote publication, external-device acceptance, and owner-approved cleanup remain open.
