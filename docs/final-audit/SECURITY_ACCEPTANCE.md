# Security acceptance

Candidate application source: 759e78dc04c61ed7f01a4b714d35ab8c999d2a85. Result: source scans and tested container boundaries PASS; release security acceptance remains CONDITIONAL.

## Checks passed

- Dependency, secret, and source security scans passed. pip-audit 2.10.1 reported zero known vulnerabilities.
- The clean container ran as UID/GID 10001 with a read-only root filesystem, all capabilities dropped, no-new-privileges, and network mode none.
- Container-internal fixed paths include /app, /var/lib/archon, and /workspace. These are image/container paths, not host or user-specific paths.
- Fresh container SQLite integrity passed. Unauthorized task admission created no queue entry; unauthorized workspace write was rejected. Caller-supplied trust-store override was rejected by an expected-negative installed-CLI check.
- The exact-candidate source/privacy checks reported no host/user-specific path patterns or matched credential patterns. Fixed container-internal paths such as /app, /var/lib/archon, and /workspace are container paths, not host/user-specific paths.
- The backup/restore runbook now archives the three native control markers and restores them with restrictive permissions before startup. A focused test executes both embedded snippets and confirms the restored controller stays in safe_mode while any marker remains.

## Limits

- The ephemeral test signing key was used only for disposable qualification state; production owner signing and approval transport remain unqualified.
- No live financial or communications effects were enabled.
- Independent AEGIS watchdog, unattended rollback, native SDA cutover, and external GitHub enforcement are not accepted.
- GitHub Actions was not run because billing was unavailable. Local verification is not equivalent to hosted enforcement.
- Independent QC passed for root source 759e. The follow-up runbook/test candidate still needs exact-source full verification and QC; its report hashes remain pending.
