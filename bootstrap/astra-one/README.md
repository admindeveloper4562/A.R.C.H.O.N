# Astra One v0.2.0 — Linux Full SDA Foundation

Astra One v0.2.0 adds a Linux-native, **five-worker Codex cloud SDA orchestrator** to the earlier Windows/Ollama lab. The Linux implementation uses **normal Codex CLI with ChatGPT authentication** (or owner-authorized API credentials), defaulting to **`gpt-5.6-luna` / `medium`**, no `--oss` and no Ollama. All new Linux operations require explicit CLI invocation; there is no install-time daemon.

**Start here:** [`docs/LINUX_FULL_SDA.md`](docs/LINUX_FULL_SDA.md).

## Roles and pipeline

```text
Final JARVIS architecture --import--> owner SHA approval
  -> Supervisor (Codex, read-only) drafts bounded JSON plan
  -> owner checks/enqueues plan
  -> SQLite Master / STOP-PAUSE-QUOTA / durable metadata events
     |-- Worker 1: Codex in isolated feature worktree
     |-- Worker 2: Codex in isolated feature worktree
     |-- Worker 3: Codex in isolated feature worktree
     |-- Worker 4: Codex in isolated feature worktree
     `-- Worker 5: Codex in isolated feature worktree
       -> static diff / syntax / symlink protection
       -> non-networked Docker test container (existing local image)
       -> independent read-only Codex QC agent
       -> owner review, OR explicit --auto-integrate mode
       -> independent read-only Codex Merger check
       -> serialized Git apply --check / local integration commit
       -> prerequisite task becomes runnable
  -> Cloudflare D1: metadata-only progress timeline (optional)
```

Failures can be requeued for bounded **Repairer** Codex attempts in a new branch and worktree, with a maximum 20-attempt hard ceiling. Quota conditions pause. STOP signals terminate Codex process groups. Crashed runs are marked interrupted and require explicit restart/retry. There is no automatic remote push, production deploy, host file deletion, self-restart, or critical service failover.

## Basic Linux preflight

```bash
cd "$HOME/Projects/astra-one-linux/Astra-One"  # after extracting the downloaded ZIP
bash scripts/linux_preflight.sh
python3 -m astra_one.linux_cli doctor --source "$HOME/Projects/astra-jarvis-source"
python3 -m astra_one.linux_cli init --source "$HOME/Projects/astra-jarvis-source"
python3 -m astra_one.linux_cli status
```

Do **not** run `run` until the final architecture is imported/approved, tasks are reviewed/enqueued, and the Docker test image + model entitlement have been checked. Full commands are in the operator guide linked above.

## Tests and claims

- Python standard-library tests: `python3 -m unittest discover -s tests -p 'test_*.py' -v`.
- Cloudflare Worker smoke tests: `cd cloudflare/astra-one-monitor && npm run smoke` (requires TypeScript installed).
- The five-worker end-to-end test uses a **mock Codex executable** and mocked Docker test result; it verifies actual local Git worktree/patch coordination, not model quality or cloud account quotas.
- The first real Linux host test is still pending. Production autonomy is not proven by mock tests.

## Legacy v0.1 Windows lab

The original Windows/Ollama single-worker CLI remains under `python -m astra_one` and `docs/WINDOWS_QUICKSTART.md` for compatibility, but **Linux users must invoke `python3 -m astra_one.linux_cli`**. Linux uses the canonical `~/.local/state/archon-astra` database, not the Windows lab database or old JARVIS Workhorse. The Cloudflare dashboard source is shared with compatible event-schema metadata and has a Linux label in this release.
