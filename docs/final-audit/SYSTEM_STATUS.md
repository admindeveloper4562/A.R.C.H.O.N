# Current system status

Snapshot date: 2026-11-21 UTC. Application qualification source: 0ae26d563e5998a9390588feb58eb3d5c0081ffb.

- Canonical SQLite integrity: ok; foreign-key violations: 0. SQLite backup-API backup and restore-copy integrity passed; source was not modified.
- Project ledger: 247 parents, 1,359 children. 240 parents and 1,319 children are recorded completed; 7 parents and 40 children are archived. 1,276 distinct completed child IDs have receipt evidence; 43 other completed children lack receipts.
- Runs: 404 historical, none active. Three supervisor lanes idle. Project queue has one pending item. No active lease observed; worker liveness unknown without trusted heartbeats.
- STOP/PAUSE/PAUSED_QUOTA markers were absent at the read-only snapshot and were not changed.
- ARCHON/Astra user service and timers were inactive or absent. No host service was enabled.
- Tested source SHA: 0ae26d563e5998a9390588feb58eb3d5c0081ffb. Current qualification result: CONDITIONAL.

See AEGIS_RECOVERY_REPORT.md for the ledger/backup snapshot and FULL_SYSTEM_RUN.md for the tested runtime.
