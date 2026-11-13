# Linux: ARCHON foundation, external Astra One, and background SDA

## What is actually deployed

- **GitHub:** one initial code commit to `main`; `develop` starts from the exact same SHA.
- **External builder:** independent `bootstrap/astra-one/` source, `~/.local/state/archon-astra` SQLite WAL, isolated `~/Projects/ARCHON-astra-source` clone of `develop` pinned at first SHA, and `~/.local/state/archon-astra/integration` independent Git worktree.
- **Concurrency:** maximum five separate authenticated Codex CLI coding workers, independent QC and serial Merger. Hosted Codex (preferred `gpt-5.6-luna`, Medium); no Ollama in this process.
- **Output:** verified local integration commits pushed non-force/fast-forward-only to remote `develop` after a second full local test pass. CI still must be checked on GitHub. Main is never updated by the service.
- **Queue:** five explicitly scoped independent kickoff tasks at `config/astra_kickoff_tasks.json`. More tasks are not auto-generated or auto-approved. The complete GitHub planning backlog is stored at `docs/tasks/JARVIS_V2_TASK_PLAN.json` and requires a reviewed conversion to runnable task specs.

## Commands

```bash
systemctl --user status archon-astra.timer archon-astra.service
journalctl --user -fu archon-astra.service
python3 ~/Projects/ARCHON/tools/atlas_monitor.py --source astra \
  --db "$HOME/.local/state/archon-astra/sda.sqlite3" --watch --interval 2
cd ~/Projects/ARCHON/bootstrap/astra-one
python3 -m astra_one.linux_cli --home "$HOME/.local/state/archon-astra" tasks
```

### Suspend and resume

```bash
cd ~/Projects/ARCHON/bootstrap/astra-one
python3 -m astra_one.linux_cli --home "$HOME/.local/state/archon-astra" pause
# Pending work will not begin; active job drains.
# To signal a stop of running coding processes:
python3 -m astra_one.linux_cli --home "$HOME/.local/state/archon-astra" stop
# Stop future timer dispatches independently of STOP markers:
systemctl --user disable --now archon-astra.timer
# When safe and ready to resume:
python3 -m astra_one.linux_cli --home "$HOME/.local/state/archon-astra" resume
systemctl --user enable --now archon-astra.timer
systemctl --user start --no-block archon-astra.service
```

**STOP vs PAUSE:** STOP terminates active Codex children as their 0.3s polling detects the marker; PAUSE drains active jobs. A batch time limit may set STOP; operator must inspect and explicitly clear it before running new tasks. Do not clear PAUSED_QUOTA to evade a provider limit.

## Failure modes

- An empty queue makes the worker exit without a push. The timer may wake later, but it will not invent tasks.
- If a source checkout is dirty, a model alias unavailable, Docker missing, or the model request fails, the task is blocked/retried only within the configured bounds. Inspect failures via the monitor or CLI.
- If `origin/develop` advances independently and cannot fast-forward to the local integration HEAD, the publisher sets `PAUSE` and refuses to force-push. Merge/rebase conflicts require human review.
- GitHub Actions may fail even when local tests pass. There is a historical **legacy repo** runner-allocation issue; new repo CI needs independent acceptance. Do not treat a successful push as a release.
- User-level systemd may stop at logout unless linger is enabled by the owner. If desired, run `sudo loginctl enable-linger "$USER"` deliberately after considering the privilege/power impact.
- The Docker socket is privileged; run this on a dedicated development machine/VM with no production credentials, not a shared production host.
- The initial clean `main` commit is a foundation snapshot, **not** JARVIS v2.0.0 release.

## Resuming an interrupted bootstrap

If the initial GitHub push succeeded but Codex login, Docker, or the user service setup later failed, **do not rerun** `archon_bootstrap.sh`: it intentionally refuses an existing Git checkout. Instead run:

```bash
cd "$HOME/Projects/ARCHON"
bash tools/archon_resume.sh
```

This checks `main`, `develop`, the private remote and clean source; it never rewrites or force-pushes Git refs. It retains existing SQLite task history and refuses a changed architecture. If any existing state or checkout is dirty/inconsistent it fails closed and asks for operator inspection.
