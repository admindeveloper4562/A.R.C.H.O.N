# Disk and cleanup report

Observed 2026-11-19T17:14:02Z. The `/home` filesystem is operationally critical at 100% use with 854,982,656 bytes free. The separate root filesystem has 40,592,805,888 bytes free and is the only evaluated local archive destination with meaningful spare capacity. `/mnt/home-ssd` is a bind view of `/home`, not extra storage. No cleanup action has been performed.

| Measurement | Current value |
| --- | ---: |
| `/home` available | 854,982,656 bytes |
| `/home` use | 100% |
| `/` available | 40,592,805,888 bytes |
| Legacy Astra root | 4,341,176,473 bytes |
| Astra worktrees | 1,254,942,481 bytes |
| Astra backups | 2,279,029,117 bytes |
| Astra checkpoints | 477,605,322 bytes |
| Astra toolchain/toolchains | 296,695,145 bytes |
| Migration checkpoint | 792,690,155 bytes |
| Canonical source | 43,338,002 bytes |
| Fresh native runtime | 117,660,564 bytes |
| Actual space reclaimed | 0 bytes |

The fresh native host inventory now has a private continuation cursor at `/home/r34p3r/.local/state/archon/host_inventory_cursor.json` with mode 0600, representing 1,328 pending directory frames after a new 10,000-entry metadata-only page. Root coverage remains intentionally incomplete; no contents of private files were read.

The cleanup manifest is still a dry-run proposal. Stage C data remains required until native recovery, watchdog qualification, owner-approved Astra cutover, and verified archival complete. Stage B proposes a local archive under `/var/tmp`, but that location is temporary and no move is authorized. Stage A has no approved targets. Unrelated files and shared installations remain excluded.
