# ARCHON cleanup manifest — executed exact batch

Observed 2026-11-20 after explicit owner authorization. The cleanup was limited to individually verified ARCHON/Astra-owned artifacts; no broad parent directory, unrelated project, shared toolchain, or user-data path was targeted.

## Result

`/home` free space increased from **951,201,792 bytes** to **3,789,815,808 bytes** immediately after cleanup: **2,838,614,016 bytes actually reclaimed**. The filesystem remains at operational risk, but the urgent sub-1 GiB condition was relieved.

## Deleted exact targets

- `$ARCHON_HOME/.local/state/archon-astra/backups` — 2,279,029,117 bytes.
- `$ARCHON_HOME/.local/state/archon-astra/checkpoints` — 477,605,322 bytes.
- `$ARCHON_HOME/.local/state/archon-astra/toolchain` — 79,893,510 bytes.
- `$ARCHON_HOME/.local/state/archon-astra/toolchains` — 216,801,635 bytes.
- `archon-python:3.12-git-20261114` — exact unreferenced Docker image removed.
- `archon-python:3.12-git-20261114-sshkeygen` — exact unreferenced Docker image removed.
- `$ARCHON_HOME/.config/systemd/user/archon-astra.timer` — disabled/stopped, then unlinked.
- `$ARCHON_HOME/.config/systemd/user/archon-astra.service` — unlinked after timer shutdown.

The timer was disabled before deletion, the service was inactive, no Astra monitor/batch process remained, and no Docker containers existed.

## Retained recovery and historical data

- `$ARCHON_HOME/.local/state/archon-astra/sda.sqlite3` and associated ledger evidence.
- `$ARCHON_HOME/.local/state/archon-astra/worktrees` because unique/uncommitted candidate work may exist.
- Astra `private`, `owner`, `provenance`, `reports`, qualification, and integration evidence.
- `$ARCHON_HOME/.local/state/archon-final-audit/checkpoints` — verified Git/SQLite recovery checkpoint.
- `/var/tmp/archon-reset-recovery-20261120T000000Z` — byte-for-byte quarantine of the pre-reset native state.
- Canonical source `$ARCHON_HOME/dev/A.R.C.H.O.N` and historical source clones pending separate provenance review.

These retained paths were not included in the deletion batch. The deleted backup/toolchain contents are not recoverable from a second copy; the Git and runtime recovery paths above remain available.

The machine still has ambiguous/unique historical material under the old source clones and Astra worktrees. Those are intentionally excluded until each untracked file and recovery reference is individually reviewed.
