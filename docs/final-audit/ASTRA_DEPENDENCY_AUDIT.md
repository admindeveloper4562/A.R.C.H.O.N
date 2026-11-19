# Astra dependency and retirement audit

Observed against `/home/r34p3r/dev/A.R.C.H.O.N` on 2026-11-19. The native source path was tested with `PYTHONPATH=src` only; Astra modules were not placed on `sys.path`.

## Findings

| Dependency surface | Current references | Native disposition | Status |
| --- | --- | --- | --- |
| Python imports | `bootstrap/astra-one/`, `migration/imported/`, and legacy verification/tests import `astra_one`; native `src/jarvis_v2` imports do not | Native package imports, queue/controller, health, inventory, and local Guardian contracts | PASS for native import isolation |
| Subprocess/CLI entry points | `tools/archon_bootstrap.sh`, `tools/archon_resume.sh`, `tools/astra_batch_cycle.sh`, and profile verification invoke Astra for rescue/development workflows | Retained as explicitly legacy procedures; native controller is `python3 -m jarvis_v2.native_controller` | PARTIAL; rescue paths intentionally retained |
| User services/timers | `infra/systemd/archon-astra.service` and `.timer` point at the historical Astra state and source | `infra/systemd/archon.service` is a native unit candidate using only `jarvis_v2.native_controller` and `~/.local/state/archon` | PARTIAL; native unit is not installed, legacy timer remains enabled, and the latest Astra service attempt failed with status 143 |
| Runtime databases/state | Legacy `~/.local/state/archon-astra/sda.sqlite3`, worktrees, backups, and receipts remain in place | Fresh `runtime.sqlite3`, `atlas.sqlite3`, `code_index.sqlite3`, and private inventory under `~/.local/state/archon`; no legacy DB was copied | PASS for separation |
| Monitor compatibility | `src/jarvis_v2/monitor.py` retains read-only fallback paths for historical Astra databases | Native ARCHON state is preferred; legacy fallback is read-only compatibility | PASS with retirement dependency |
| Watchdog/recovery | Historical Astra watchdog and handover documents remain available | Native queue fencing and local Guardian contracts exist; trusted out-of-process AEGIS/watchdog deployment and rollback soak are not yet proven | BLOCKED at release gate |

## Controlled native-without-Astra checks

- Imported all 106 native `jarvis_v2` modules with only `PYTHONPATH=src`: 0 errors.
- Ran the fresh-state native controller one-shot: idle with `executor_unconfigured`; it claimed no work.
- Verified process-lock fencing, STOP/PAUSE/PAUSED_QUOTA admission, digest-only success/failure receipts, and terminate/restart behavior on disposable state.
- Verified the native systemd unit with `systemd-analyze verify`; it is not installed or enabled.

These checks demonstrate that the native local slice does not require Astra to import or start. They do not demonstrate a complete native task executor, unattended SDA/AEGIS cutover, trusted watchdog activation, or rollback soak.

## Current legacy-service observation

At the final direct observation, `archon-astra.timer` was enabled and active, `archon-astra.service` was failed with exit status 143, and PID 20774 remained the read-only legacy monitor. The user journal records the legacy monitor rejecting simultaneous `--json` and `--watch` arguments before systemd terminated the batch cycle. This is preserved as evidence; no service state was changed.

## Retirement decision

Astra One remains a preserved, separately controlled recovery path. Do not disable its active timer, remove its state, or delete its source/worktrees until the native executor and watchdog acceptance evidence is complete and the owner approves the exact transition and cleanup targets.
