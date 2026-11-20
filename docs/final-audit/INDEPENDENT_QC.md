# Independent QC receipt

Observed 2026-11-20 against current local HEAD `1c27e2277a7a9f88d9d0dbd9bdac6c7b8f2f80e5` by an independently provisioned, read-only QC subagent. The tested implementation candidate is `4149c1d75eee24880bfacd819342f9c21d05d51a`; the current HEAD is a documentation-only overlay whose source diff contains no production-code changes. The QC did not edit files, commit, push, change services, delete data, or mutate persistent databases.

| Check | Result | Evidence |
| --- | --- | --- |
| Git identity and provenance | PASS | Current HEAD `1c27e22`; implementation `4149c1d` is an ancestor; source branch is 36 ahead of the verified remote and the documentation overlay is 37 ahead; 0 behind |
| Active audit JSON | PASS | Active final-audit JSON parsed; current source and implementation fields bind to `4149c1d`; overlay binding is recorded separately |
| Diff hygiene | PASS | `git diff --check` passed |
| Native executor tests | PASS | Focused native executor suite: 8/8 |
| Resumable inventory tests | PASS | Focused system-inventory suite: 6/6 |
| Native one-shot | PASS | Temporary isolated state returned `idle` / `no_ready_work` |
| Native health | PASS | `healthy`, `native_runtime`, queue 0; SQLite health valid |
| Historical ledger envelope | PASS | Read-only query: 247 parents = 240 completed + 7 archived; 1,359 children; 1,281 receipt rows |
| Native systemd candidate | PASS | `systemd-analyze verify infra/systemd/archon.service` passed |
| Remote publication | PARTIAL | Remote refs verified; local source and documentation overlay remain unpublished |
| Astra boundary | PARTIAL | Timer enabled/active and read-only monitor PID 20774 remains; no service state was changed |
| Native release completeness | PARTIAL | Domain effects, unattended SDA/AEGIS ownership, trusted watchdog activation, and rollback soak remain unproven |

The QC intentionally skipped the full regression rerun and all destructive, archive-move, service-cutover, Astra-retirement, and remote-publication operations. Main-session evidence remains 590/590 at implementation candidate `4149c1d`; the focused independent checks above validate the current exact checkout and its source ancestry.
