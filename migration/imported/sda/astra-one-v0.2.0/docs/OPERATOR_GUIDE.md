# Operator controls and milestones

**Milestone A0 (this package):** local install, offline tests, manual architecture import/approval, SQLite queue, one worktree per task, Codex via Ollama, static QC gate, authenticated progress dashboard, metadata replay and STOP/PAUSE. Full integration with legacy SDA draft PRs and the future JARVIS v2 architecture remains outside A0.

**Milestone A1 (after final architecture):** turn the provided blueprint into a reviewed dependency DAG; define modules, tests, acceptance criteria and permissions in exact owner-approved task JSON. Store source references, sanitized handoffs and stage checkpoints. Run a real single-task canary; review the diff and tests. Baseline task and milestone planning must not be guessed from an unfinished blueprint.

**Milestone A2:** independent acceptance tests in a separately isolated execution environment (container/VM), structured QC receipts, serialized feature integration with merge-conflict handling and rollback. Do NOT treat the current static QC as this capability.

**Milestone A3:** guarded self-repair, limited restart/rollback canaries, fault isolation and an independent fail-safe supervisor. Each release requires evidence, owner-approved high-impact changes, and security evaluation.

## CLI

```text
python -m astra_one doctor --source <clean-checkout>
python -m astra_one init --source <clean-checkout>
python -m astra_one architecture import --file <final.md>
python -m astra_one architecture status
python -m astra_one architecture approve --sha256 <full-hash>
python -m astra_one plan --focus <Markdown-heading> --count 4
python -m astra_one enqueue-plan --file <reviewed-plan.json>
python -m astra_one enqueue --file <task.json>
python -m astra_one tasks
python -m astra_one status
python -m astra_one run-once --model qwen3:8b --context 16384
python -m astra_one start --max-tasks 2
python -m astra_one approve-task ASTRA-101
python -m astra_one integrate ASTRA-101 --confirm
python -m astra_one retry ASTRA-101
python -m astra_one recover
python -m astra_one sync
python -m astra_one pause
python -m astra_one stop
python -m astra_one resume
```

All commands operate on `%LOCALAPPDATA%\AstraOne` unless `ASTRA_ONE_HOME` or `--home` is explicitly set. `init` refuses existing state. The source checkout must be clean and pinned to its original commit; if that commit changes, use a reviewed migration or a new state (never silently reset the old one).

`run-once` takes one queued task. `start --max-tasks N` works sequentially for up to N tasks then exits. There is no perpetual background service, and installation/deployment cannot invoke `start` on its own. Dependent tasks wait until prerequisites are reviewed and locally integrated as completed. Interruption does not automatically replay a task. `recover` only marks stale tasks interrupted, with no restart.

The `approve-task` review gate does not touch Git. A human inspects the worktree and generated tests, then may approve a candidate. **Only the separate explicit** `integrate TASK-ID --confirm` operation creates local commits: one on the disposable candidate branch, one on an isolated `feature/astra-integration-*` worktree. It advances the next task base while leaving the original source checkout and `main`/`develop` unchanged. Git conflicts fail closed. No remote push, production deployment or release is performed. Full independent QC in a restricted VM/container is still a separate acceptance milestone.

## Stop and pause

While SDA is running, from a second PowerShell window:

```powershell
Set-Location "$HOME\Projects\Astra-One-Test\Astra-One"
python -m astra_one stop
```

This writes `%LOCALAPPDATA%\AstraOne\STOP`. The Codex wrapper checks it twice per second and requests termination of its direct child process. Child processes spawned by Codex may need additional OS-level cleanup; this is not yet a hardened kill switch. `pause` similarly blocks new runs. Only the owner should issue `resume`, which clears those markers but **does not start any task**.

If your process crashes, manually inspect the active process and worktree before `recover`. Never call `recover` while an actual SDA process is still alive—it only marks database state and does not terminate workers.
