# Disk and cleanup report

The authorized exact cleanup batch completed on 2026-11-20. `/home` free space increased from 951,201,792 to 3,789,815,808 bytes immediately afterward, reclaiming 2,838,614,016 bytes. A later test run consumed a small amount of space; the latest observation is 3,788,345,344 bytes free.

| Measurement | Value |
| --- | ---: |
| `/home` available immediately before cleanup | 951,201,792 bytes |
| `/home` available immediately after cleanup | 3,789,815,808 bytes |
| Actual space reclaimed | 2,838,614,016 bytes |
| Latest `/home` available | 3,788,345,344 bytes |
| Latest `/` available | 40,425,947,136 bytes |
| Historical Astra SQLite ledger retained | 7,700,480 bytes |
| Verified final-audit checkpoint retained | 795,522,291 bytes |
| Native reset quarantine retained | 140,377,536 bytes |

Deleted targets were limited to the four legacy Astra backup/checkpoint/toolchain directories, two unreferenced ARCHON Docker images, and the obsolete Astra user timer/service unit files. The timer and monitor were stopped first; no Astra process or Docker container was live.

The canonical checkout, historical ledger and receipts, unique Astra worktrees, provenance/owner evidence, final-audit checkpoint, and native reset quarantine remain intact. The old source clones remain because their untracked or historical contents were not proven disposable. `/dev/sdc1` remains unmounted and untouched.

The fresh native runtime remains healthy after cleanup. No unrelated user data, shared toolchain, other repository, or broad `.local` path was removed.
