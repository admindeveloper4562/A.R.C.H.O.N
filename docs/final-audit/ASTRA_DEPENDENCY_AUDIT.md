# Astra dependency and retirement audit

Observed against `$ARCHON_HOME/dev/A.R.C.H.O.N` on 2026-11-19. The native source path was tested with `PYTHONPATH=src` only; Astra modules were not placed on `sys.path`.

## Findings

| Dependency surface | Current references | Native disposition | Status |
| --- | --- | --- | --- |
| Python imports | `bootstrap/astra-one/`, `migration/imported/`, and legacy verification/tests import `astra_one`; native `src/jarvis_v2` imports do not | Native package imports, queue/controller, health, inventory, and local Guardian contracts | PASS for native import isolation |
| Subprocess/CLI entry points | `tools/archon_bootstrap.sh`, `tools/archon_resume.sh`, `tools/astra_batch_cycle.sh`, and profile verification invoke Astra for rescue/development workflows | Retained as explicitly legacy procedures; native controller is `python3 -m jarvis_v2.native_controller` | PARTIAL; rescue paths intentionally retained |
| User services/timers | Historical `infra/systemd/archon-astra.service` and `.timer` pointed at the legacy state and source | `infra/systemd/archon.service` is a native unit candidate using only `jarvis_v2.native_controller` and `~/.local/state/archon` | PARTIAL; native unit is not installed, legacy timer/service units were disabled and unlinked, and no Astra process remains |
| Runtime databases/state | Legacy `~/.local/state/archon-astra/sda.sqlite3`, worktrees, backups, and receipts remain in place | Fresh `runtime.sqlite3`, `atlas.sqlite3`, `code_index.sqlite3`, and private inventory under `~/.local/state/archon`; no legacy DB was copied | PASS for separation |
| Monitor compatibility | `src/jarvis_v2/monitor.py` retains read-only fallback paths for historical Astra databases | Native ARCHON state is preferred; legacy fallback is read-only compatibility | PASS with retirement dependency |
| Watchdog/recovery | Historical Astra watchdog and handover documents remain available | Native queue fencing and local Guardian contracts exist; trusted out-of-process AEGIS/watchdog deployment and rollback soak are not yet proven | BLOCKED at release gate |

## Controlled native-without-Astra checks

- Imported all 106 native `jarvis_v2` modules with only `PYTHONPATH=src`: 0 errors.
- Ran the fresh-state native controller one-shot: idle with `no_ready_work`; the built-in executor claimed no work because the queue was empty.
- Verified process-lock fencing, STOP/PAUSE/PAUSED_QUOTA admission, digest-only success/failure receipts, and terminate/restart behavior on disposable state.
- Verified the native systemd unit with `systemd-analyze verify`; it is not installed or enabled.

These checks demonstrate that the native local slice does not require Astra to import or start. The built-in executor is limited to read-only control-plane operations; these checks do not demonstrate domain-effect execution, unattended SDA/AEGIS cutover, trusted watchdog activation, or rollback soak.

## Follow-up default-boundary correction

Commit `2070829` corrected the monitor's database selection boundary after a
live check found that `--source auto` selected the historical Astra database
whenever both state roots existed. Auto mode now prefers native
`~/.local/state/archon/atlas.sqlite3`; `--source astra` remains an explicit
read-only historical mode. The monitor and supervision tests passed (`12/12`
and `3/3`), and the installed-style launcher returned the native ATLAS engine
for its default JSON snapshot.

## Historical legacy-service observation before authorized cleanup

At the pre-cleanup direct observation, `archon-astra.timer` was enabled and active, the latest `archon-astra.service` run had exited 0 and was inactive, and PID 20774 remained the read-only legacy monitor. The user journal records the legacy monitor rejecting simultaneous `--json` and `--watch` arguments before the legacy batch completed its own 568-test run. This remains historical evidence.

## Current post-authorization state

The timer was disabled/stopped before the exact cleanup batch. The user unit files were then unlinked, the monitor was terminated, and a live process check found no Astra monitor, batch, or service process. Historical `sda.sqlite3`, receipts, worktrees, provenance, and recovery evidence remain retained. Fresh native one-shot and health checks pass without Astra.

## Retirement decision

Astra One is now retired from user startup, but its historical state and unique worktrees remain a separately preserved recovery/provenance path. Native unattended SDA/AEGIS execution, trusted watchdog activation/soak, and rollback application remain release-gated.
