# ARCHON final-audit baseline

Observed 2026-11-19 13:19:59 UTC. Machine-readable evidence is in BASELINE.json.

## Canonical source decision

The authoritative local integration checkout is $ARCHON_HOME/.local/state/archon-astra/integration-reconciled-20261114, clean at a2df24261d5ea19e9260f7f6c270b26ea9abdb03. A standalone checkout was created at $ARCHON_HOME/dev/A.R.C.H.O.N from that exact commit and is clean. Its tracked-tree digest is 5073dc4315e1a016c6026d6c18b7feb5ed96633968f36778708c8a23641eb635.

The remote integration/develop ref is 75582dbf48057e3d5b0e7cf4acfdba2386acfcff; the target commit is therefore local-only until publication is separately verified. main is 5227b91d2725bf4be4336a5ad26189fdf1034704.

## Git and worktrees

- $ARCHON_HOME/Projects/ARCHON is a separate development checkout at 46cd0e3883cba73354f372daa9f3d57993c260c9, with 14 untracked session/Serena files and no tracked edits.
- $ARCHON_HOME/Projects/ARCHON-astra-source is 43c8db7de8a5f0277a7db23379019d05f2edd2c6 on develop, with one untracked session file.
- $ARCHON_HOME/Projects/ARCHON-astra-source-clean-20261116 is clean at 6fc168796641dc24eceb07bd306fd65b0f54cb9b.
- The Astra worktree set contains ten listed worktrees plus the primary checkout. owner-approval-signatures has 278 status entries including unresolved conflicts and is preserved untouched.
- The current development checkout has no stash, 317 reachable commits, and 46 git fsck unreachable entries. No broad cleanup or history rewrite was performed.

## Ledger and runtime

The live SQLite ledger is healthy (integrity_check=ok, zero foreign-key violations). The `ARCHON-JARVIS-V2` envelope records 247 parents: 240 completed and 7 archived; and 1,359 subtasks: 1,319 completed and 40 archived. Five additional completed task rows have no project ID and are excluded from the 247-parent envelope. The ledger has 1,281 subtask receipts, empty pending/review/merge queues, three idle supervisor lanes, and 72 resolved supervisor cases. The seven archived parents remain deferred and are not counted as completed.

The legacy archon-astra.timer is enabled and active; its service is inactive. A read-only legacy ATLAS monitor remains running from $ARCHON_HOME/Projects/ARCHON. No STOP, PAUSE, or PAUSED_QUOTA marker was observed in the checked state paths.

## Recovery checkpoint

Checkpoint $ARCHON_HOME/.local/state/archon-final-audit/checkpoints/20261119T125838Z contains verified bundles for both primary Git histories and SQLite backup-API copies. Both canonical database copies passed integrity and foreign-key checks. The checkpoint is retained; it includes additional historical SQLite snapshots copied before a broad read-only discovery scan was interrupted.

The final uncommitted audit working tree is additionally recoverable from `final-working-tree.patch` (SHA-256 `05a49f8edce3fe0324f133d1bae21c3f2101ebbf7a40cc6ca1dee319fc103444`) and `final-untracked-working-tree.tar.gz` (SHA-256 `1be1d3f4890b77e7de83f1586aca5c98259e54590283bde52f838bb59a936e06`) in that checkpoint; both checksums were verified.

## Host and constraints

The home filesystem is critically full: 110G total, 103G used, 975M available. The old Astra state consumes 4.6G; the new ARCHON state currently consumes 7.6M. The host is Ubuntu x86_64 on an Intel i7-7800X with 12 logical CPUs and 15GiB RAM. pytest is unavailable, so standard-library unittest discovery is the executable test runner.

Material risks remain: remote publication is unverified, the legacy timer is active, one conflicted recovery worktree must be preserved, and native unattended SDA/Guardian cutover has not yet been proven. Cleanup therefore remains a dry-run/approval gate.
