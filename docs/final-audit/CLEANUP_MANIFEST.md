# ARCHON cleanup manifest — dry run only

Observed 2026-11-19T17:34:11Z. `/home` (`/dev/sda1`) had 849,141,760 bytes free and reported 100% use. The separate root filesystem (`/dev/sdb3`) had 40,568,348,672 bytes free. `/mnt/home-ssd` is the same `/home` filesystem, not additional capacity. `/var/tmp` is on the root filesystem but is temporary storage and is not yet a durable archive. A separate 931.5G `/dev/sdc1` volume labeled `storage` is present but unmounted; it is not used or mounted by this audit.

No files, directories, Git refs, services, containers, or databases were deleted or moved. Actual reclaimed space remains **0 bytes**.

## Staged proposal

| Stage | Treatment | Current decision |
| --- | --- | --- |
| A — confirmed disposable | Generated caches or other individually regenerable artifacts | None approved; no deletion based only on estimates |
| B — archive elsewhere | Migration checkpoint and historical backups, after verified copy to a mode-0700 root-backed archive | Proposal only; owner approval required |
| C — required until native cutover | Astra worktrees/backups/checkpoints/toolchains, old source clones, current migration checkpoint, Docker QC images | Retain |
| D — unrelated/shared | Canonical checkout, fresh native runtime, shared tools, unrelated projects and user data | Untouched |

The largest exact measured components are:

- Astra worktrees: 1,254,942,481 bytes.
- Astra backups: 2,279,029,117 bytes.
- Final-audit checkpoint: 793,628,329 bytes, including the verified current-candidate bundle and private binding.
- Astra checkpoints/toolchains: 774,300,467 bytes combined from the separately listed components; retain until provenance is archived.
- Older `/home/r34p3r/Projects/ARCHON`: 333,180,632 bytes, including untracked evidence and a live read-only monitor reference.
- Docker images: two approximately 318 MB displays; exact reclaim is layer/reference dependent.

The exact paths, byte counts, owners, references, risks, recovery status, and approval requests are in [CLEANUP_MANIFEST.json](CLEANUP_MANIFEST.json). The manifest intentionally does not authorize a recursive deletion of `/home/r34p3r/.local/state/archon-astra` or any broad parent directory.

## Exact approval requests

1. `ARCHON-CLEANUP-ARCHIVE-001`: approve archive-only quarantine of the exact checkpoint and historical-backup paths to `/var/tmp/archon-final-migration-archive-20261120`, subject to per-file SHA-256, byte-count, Git-bundle, SQLite-integrity, restore, permissions, and second-copy verification. No source removal is included in this request.
2. `ARCHON-CLEANUP-DELETE-001`: approve no paths yet. Any later deletion needs separate per-path approval, a verified second recovery copy, a final live-reference check, a fresh native smoke test, and `DELETE-LOGS.md` evidence.

Until those approvals and checks exist, all targets remain preserved. Mounting `/dev/sdc1`, copying to it, or changing its mount configuration is outside this read-only audit and requires a separate owner-approved system operation.
