# Cleanup manifest — dry run only

No files, directories, Git refs, services, containers, or databases were deleted. This document and CLEANUP_MANIFEST.json are the exact high-impact review list.

The largest candidates are the old Astra state (4.6G including 1.7G worktrees and 2.2G backups), the new 752M migration checkpoint, and the historical project clones. They are not safe to remove yet: the state contains candidate worktrees, a conflicted owner-approval worktree, rollback backups, and receipts that are not reproducible from Git alone.

The home filesystem has only about 955M free. The cleanup stage is blocked on explicit owner approval per target and on a verified archive plan. No unrelated user files or shared toolchains were included.
