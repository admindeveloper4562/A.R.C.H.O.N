# Security status

## Passed

- Local security, secret, and dependency scans all returned exit code 0.
- The full test suite passed path traversal, command restriction, authorization, secret redaction, approval, lease, rollback, and Guardian boundary tests.
- Native inventory does not read arbitrary file contents or environment-variable values; its private output is mode 0600 under a mode 0700 state root.
- Runtime and index databases are mode 0600. Fresh database checks found zero foreign-key violations.
- Native imports with only the src path do not require bootstrap/Astra modules; the exact candidate is `4149c1d75eee24880bfacd819342f9c21d05d51a`.
- The built-in executor exposes eight explicit read-only operations, restricts database inspection to named native files, binds inventory continuation to the root/device, and rejects shell, network, provider, finance, communication, model, service-control, filesystem-write and rollback-application classes.
- No external messages, financial transactions, deployments, or service cutover actions were performed.

## Open security/release concerns

- The legacy Astra timer remains enabled and is an external controller boundary; its latest transient run exited 0 but logged the legacy `--json`/`--watch` argument conflict.
- The host filesystem is critically full, increasing write-failure and recovery risk.
- Root inventory metadata includes names of sensitive system paths by design, but no contents were read; access remains private.
- Trusted out-of-process watchdog activation, native recovery cutover, and rollback soak were not executed.
- Hosted CI and external-provider security evidence were not available.
- The Codex Security diff-scan tool did not produce a scan artifact: both launch attempts rejected the target as a non-bare worktree with no resolvable HEAD. Repository-local dependency, secret, and workflow security scans are the evidence claimed here; the plugin scan is not claimed as passed.
- The root inventory remains truncated at 10,000 metadata entries; the continuation cursor is mode 0600 and no file contents were read, but complete root coverage is not claimed.

No security PASS is promoted to a complete release PASS while these release-boundary items remain unresolved.
