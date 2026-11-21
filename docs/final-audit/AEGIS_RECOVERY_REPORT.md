# AEGIS and recovery report

Candidate application source: 0ae26d563e5998a9390588feb58eb3d5c0081ffb. Result: PARTIAL; unattended Guardian recovery is not qualified.

## Verified recovery evidence

- PALADIN/Guardian and recovery component contracts are included in the 626-test passing suite.
- Clean-container acceptance completed a bounded allowlisted workspace effect, interrupted a separate effect, reconciled it after restart, and verified persistence and SQLite integrity.
- Saved-image reload acceptance completed one signed task, stopped gracefully, restarted with the same two persistent volumes, preserved the completed task, and reported atlas/runtime integrity ok.
- Canonical Astra SQLite state was inspected read-only. SQLite integrity was ok, foreign-key violations were zero, and SQLite backup-API backup plus restore-copy integrity passed.
- Backup receipt SHA-256: 6a37810719d1e93a9ecca14cc6aebd2e992f721be17ab5dc722ea1d39e947fc0. The canonical database was not changed.

## Canonical ledger snapshot

- 247 project parents: 240 recorded completed, 7 archived.
- 1,359 subtasks: 1,319 recorded completed, 40 archived.
- 1,281 subtask-receipt rows cover 1,276 distinct child IDs. 1,276 completed children have receipts; 43 other completed children lack receipts. Archived children are not counted as verified.
- Three owner-subtask receipt rows cover three child IDs.
- 404 historical runs: 244 completed, 146 failed, 13 interrupted, and 1 blocked. No active run or lease was present.
- Three recorded supervisor lanes were idle. The project queue had one pending item. Worker process liveness is unknown without trusted heartbeats.

## Not qualified

- No separately protected AEGIS watchdog was activated to monitor ARCHON process crash, failed boot, host reboot, or repeated crash loops.
- Trusted rollback application, signed deployment identity, failback, and rollback soak were not run.
- No production owner-signed delegation/trust anchor was provisioned. Disposable test signing keys do not meet this requirement.
- STOP, PAUSE, and quota controls were observed without clearing them; the host user service and timers remain inactive or absent.
- Do not enable unattended recovery, cut over native SDA, or activate the host service based on these tests. Astra One remains the external rescue path.
