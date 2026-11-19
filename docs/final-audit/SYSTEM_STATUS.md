# ARCHON system status

## Project

- Canonical source: /home/r34p3r/dev/A.R.C.H.O.N
- Source SHA: eef1e3c8d1bfd3ea6a3dc7e1b06ac2daa3e21767
- Git origin: https://github.com/admindeveloper4562/A.R.C.H.O.N.git; target SHA is not published to GitHub; direct refs observed: main=5227b91d2725bf4be4336a5ad26189fdf1034704, develop=75582dbf48057e3d5b0e7cf4acfdba2386acfcff
- Git state: local migration commit is present; the evidence refresh is being consolidated locally and is not published to GitHub
- Version in package metadata: 0.0.3
- Full regression: 579 passed
- Native import sweep: 106 passed
- Fresh runtime DBs: integrity and restore checks passed
- Search index: FTS5 available, 546 files indexed from 547 cataloged files, four representative queries returned results including deployment files

## Runtime

The native state root is /home/r34p3r/.local/state/archon. It contains empty runtime and ATLAS queue databases, private host inventory metadata, the code index, empty logs/cache directories, and private controller lock/control directories. It does not contain the historical 247-task ledger or personal/financial data. Native health reports the runtime healthy with zero queue tasks and historical ledger loading false. The native controller passed fresh one-shot, fencing, marker, receipt, terminate/restart, and systemd verification checks; its default domain executor is unconfigured and its unit is not installed.

The historical Astra state remains active enough to require controlled retirement: archon-astra.timer is enabled and active, while archon-astra.service is inactive and a read-only legacy monitor process is running.

## Inventory

The bounded inventory scanned 10,000 metadata entries from the root filesystem, recorded 17 permission-denied paths, skipped 28 mount boundaries, skipped /dev, /proc, /run, and /sys, did not follow symlinks, and stopped at its explicit bound. It captured Ollama models `qwen3:4b`, `qwen2.5-coder:7b`, and `qwen2.5-coder:3b`, plus NVIDIA GeForce GTX 980 acceleration with driver 535.309.01; unavailable VA-API, ROCm, and OpenCL probes were recorded. It is private at mode 0600 and contains metadata only.

## Overall state

The Linux native code and local contracts are operational for the tested scope. The installation is not yet a clean fully retired standalone release because native unattended SDA/Guardian cutover, remote publication, external-device acceptance, and owner-approved cleanup remain open.
