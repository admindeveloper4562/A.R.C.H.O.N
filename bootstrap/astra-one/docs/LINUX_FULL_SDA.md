# Astra One Linux — Full SDA orchestration (v0.2.1)

## Scope and status

This Linux edition uses **normal authenticated OpenAI Codex**, NOT Ollama, with the requested default **`gpt-5.6-luna` at `medium` reasoning** and **five concurrent coding-worker slots**. It is a standalone lab orchestrator, not the released JARVIS v2 runtime. Every Codex role is a separate CLI invocation and is constrained to an isolated Git worktree where applicable. The AI model must be accessible to the account signed in with `codex login`; the launcher does not silently switch to another model or an API key.

**Implementation:** local SQLite task DAG, Supervisor planning, a five-slot parallel Master, fresh worker worktrees and retries, separate read-only QC Codex invocations, tests in a Docker container with network disabled, separate read-only Merger Codex review, Git apply/check + serialized local integration, owner STOP/PAUSE/PAUSED_QUOTA, crash recovery, no remote Git push, and optional metadata-only Cloudflare progress events.

**Verification so far:** unit tests, deterministic failure/recovery tests, and an end-to-end **mock Codex** pipeline on Linux. Actual CLI account entitlements, cloud quota, the Docker daemon, the JARVIS repository's full tests, failure handling under real network loss, and long-run scheduling must be verified on the target Linux host before unattended use. It is not a production-ready self-updater and does not autonomously restart host services.

## 1. System requirements

Ubuntu 24.04 or another recent Linux distribution, Python **3.11+**, Git, Node/npm only if deploying the Cloudflare monitor, **Codex CLI** signed in with ChatGPT or intentionally authorized API credentials, and a locally available test container image (Docker CLI + daemon). A test image is deliberately not automatically pulled or built by SDA. Prefer an unprivileged, dedicated OS user or VM with no browser profiles, production credentials or personal files accessible to generated code. Access to the Docker socket or Docker group can be equivalent to high host privilege: use an appropriate isolated runner. **Never run SDA as root.**

Install/check Codex using the official CLI docs, then:

```bash
codex --version
codex login
codex login status

# Preflight requested model and effort, not Ollama:
mkdir -p "$HOME/Projects/astra-model-check"
cd "$HOME/Projects/astra-model-check"
codex exec --ephemeral --sandbox read-only -m gpt-5.6-luna \
  -c model_reasoning_effort=medium "Reply with exactly ASTRA_READY"
```

On Ubuntu 24.04, verify the Codex bubblewrap/user-namespace prerequisite before starting a Master:

```bash
python3 -m astra_one.linux_cli doctor
```

The doctor must report `sandbox.available: true`. If it reports `user_namespace_unavailable`, stop and install/load the distribution's supported bubblewrap AppArmor profile according to the official Codex sandbox guidance; do **not** disable the system-wide AppArmor restriction. Astra now fails closed before claiming a task when this prerequisite is unavailable.

For a temporary, manually supervised development run in a **disposable state and source clone**, `run --danger-bypass` can be used to continue implementation while the host profile is repaired. The flag is rejected for the live `~/.local/state/archon-astra` state, the pinned live source clone and systemd, and it does not bypass deterministic path validation, Docker QC, STOP/PAUSE/quota controls or serial integration. Because every Codex role in that run has host-level access, it is not an unattended mode and must be removed once the sandbox fix is deployed.

The configured Docker test image must contain every tool required by the selected test command. In particular, `python:3.12-slim` does not include Git, while the repository's importer tests invoke Git; use a reviewed local image containing Git for the complete suite, or select a narrower command whose dependencies are present. Astra does not install packages or pull/build images automatically.

If the model is unavailable to your account, stop. Don't edit the package to claim it's running Luna when the backend uses another model. Codex uses the account's normal usage limits and/or API charges depending on how you signed in.

## 2. Install the ZIP locally and run tests

Save `Astra-One-Linux-v0.2.0.zip` to `~/Downloads` and run:

```bash
set -euo pipefail
mkdir -p "$HOME/Projects/astra-one-linux"
unzip -n "$HOME/Downloads/Astra-One-Linux-v0.2.0.zip" -d "$HOME/Projects/astra-one-linux"
cd "$HOME/Projects/astra-one-linux/Astra-One"
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m astra_one.linux_cli doctor
```

The package does **not** change your existing Windows Astra instance, its database, or the legacy Ubuntu Workhorse. No background service is installed and no agents start during these steps.

## 3. Create a separate clean Linux source checkout

```bash
mkdir -p "$HOME/Projects"
git clone --single-branch \
  --branch feature/jarvis-v2-expanded-architecture-20261113 \
  https://github.com/admindeveloper4562/personal-jarvis.git \
  "$HOME/Projects/astra-jarvis-source"

cd "$HOME/Projects/astra-one-linux/Astra-One"
python3 -m astra_one.linux_cli doctor --source "$HOME/Projects/astra-jarvis-source"
python3 -m astra_one.linux_cli init --source "$HOME/Projects/astra-jarvis-source"
python3 -m astra_one.linux_cli status
```

Use a fresh path if the clone already exists; don't clean/reset the existing checkout. The new Linux DB lives at `~/.local/state/astra-one-linux/sda.sqlite3` (mode 0600), outside Git, with private architecture and review artifacts. The primary Git checkout remains unchanged. Astra creates a *separate local integration worktree* only when the Master starts. The legacy `~/.local/state/jarvis/workhorse-v2` Master is not launched or altered. Ensure that you have not already started another Workhorse targeting the same underlying Git repository and shared state.

## 4. Final architecture and owner approval

**SDA stays stopped until the final architecture is provided and approved.** After saving the architecture in a local UTF-8 Markdown file:

```bash
cd "$HOME/Projects/astra-one-linux/Astra-One"
python3 -m astra_one.linux_cli architecture import --file "$HOME/Downloads/JARVIS-V2-FINAL.md"
# Copy the exact printed sha256 after inspecting the document:
python3 -m astra_one.linux_cli architecture approve --sha YOUR_EXACT_SHA256

# Supervisor drafts a plan; does not enqueue or start it.
python3 -m astra_one.linux_cli supervise --focus 'SDA foundation milestone' --count 5 \
  --output "$HOME/Projects/astra-plan-001.json"

# Review the proposed JSON first. Enqueue only approved concrete tasks:
python3 -m astra_one.linux_cli enqueue --file "$HOME/Projects/astra-plan-001.json"
```

Supervisor planning rejects architecture files larger than a bounded first-pass context packet (30,000 characters): split oversized documents into owner-approved milestone task plans and enqueue explicit JSON packets; the full architecture SHA remains the authoritative state. Do not bypass approval.

Example task JSON is in `examples/linux-tasks.sample.json` (do not enqueue it unless the objective truly matches your approved architecture).

## 5. Prepare tests and start the five-worker Master

Prepare a locally trusted Docker image intentionally (e.g. `docker pull python:3.12-slim`) and verify `docker image inspect python:3.12-slim` succeeds. Work out dependency installation in a **reviewed, pinned, non-networked test image**; SDA never automatically `pip install`s untrusted code on the host. A local Docker daemon and image are required by this strict acceptance path.

```bash
cd "$HOME/Projects/astra-one-linux/Astra-One"

# Default: five active worker slots, separate Codex QA, no automatic integration.
python3 -m astra_one.linux_cli run --workers 5 --max-tasks 20 --max-minutes 120 \
  --model gpt-5.6-luna --effort medium \
  --test-image python:3.12-slim --max-repairs 3

# Inspect candidate worktrees and results:
python3 -m astra_one.linux_cli tasks
python3 -m astra_one.linux_cli status

# After manual inspection of one accepted task:
python3 -m astra_one.linux_cli approve-task ASTRA-001
python3 -m astra_one.linux_cli integrate ASTRA-001 --confirm
```

To opt into automatic **local integration only** of independent-QC-approved changes, use the same `run` command with `--auto-integrate`. This creates commits on `feature/astra-linux-integration-*` only, not on `develop` or `main`, and never pushes to GitHub or deploys. It can introduce defective code despite review; use a disposable VM / source clone and independent oversight. Dependency tasks can begin only after predecessors become **completed** in the local integration branch. If patches conflict, the task is blocked for supervised rework. No `reset --hard`, `clean`, automatic deletion, force-push, or service restart occurs.

The five-worker cap includes worker and repair attempts; QC and Merger use separate Codex sessions. Each worker has subagent spawning disabled to prevent multiplying concurrent agents beyond the configured pool. Model requests still count toward your ChatGPT/Codex rate and usage limits.

## 6. Owner controls, recovery and quotas

Use **a second terminal** while the Master runs:

```bash
cd "$HOME/Projects/astra-one-linux/Astra-One"
python3 -m astra_one.linux_cli pause         # do not launch new jobs, let active work drain
python3 -m astra_one.linux_cli stop          # signal active Codex process groups to terminate
python3 -m astra_one.linux_cli status
python3 -m astra_one.linux_cli resume        # owner clears STOP/PAUSE; does not auto-start
python3 -m astra_one.linux_cli clear-quota   # owner-only; does not auto-resume work
python3 -m astra_one.linux_cli recover       # mark interrupted, do not replay automatically
python3 -m astra_one.linux_cli retry ASTRA-001
```

Repeated failures are bounded by `--max-repairs` (defaults to 3 repair retries; hard ceiling 20 total attempts). A quota/rate-limit signal creates `PAUSED_QUOTA`; there is no paid-provider fallback. Preserve failed worktrees and error codes; review them before retrying. A runner restart requires explicit human action. A live master lock blocks concurrent Master or recovery, including after interruptions; the underlying `flock` is released on process exit.

## 7. Cloudflare monitoring (reuse the existing D1)

The package includes `cloudflare/astra-one-monitor/`: the same privacy-preserving D1 event API as the Windows v0.1 foundation. No new D1 database is required. **Do not create a new database if your account has reached the quota.** Your existing `astra-one-monitor` can be reused after verifying its schema and binding.

```bash
cd "$HOME/Projects/astra-one-linux/Astra-One/cloudflare/astra-one-monitor"
npm install
npx wrangler login
npx wrangler d1 list
cp -n wrangler.toml.example wrangler.toml
nano wrangler.toml
# Set the existing D1 UUID, confirm name/main/binding, remove accidental assets bindings.
npm run typecheck
npm run smoke
npx wrangler d1 execute astra-one-monitor --remote --file=./schema.sql
npx wrangler secret put ASTRA_INGEST_TOKEN
npx wrangler secret put ASTRA_VIEW_TOKEN
npx wrangler deploy
```

Only the **correct** Worker (`astra-one-monitor`) should receive the two secrets. The previous erroneous Worker `ser` is unrelated; no deletion is necessary. Supply monitor secrets as secure prompts; do not paste them into shell history or chat. If you already have the exact Worker URL and ingest token:

```bash
export ASTRA_MONITOR_URL='https://YOUR-WORKER.workers.dev'
read -rsp 'Ingest token: ' ASTRA_MONITOR_INGEST_TOKEN; echo
export ASTRA_MONITOR_INGEST_TOKEN
python3 -m astra_one.linux_cli sync
```

The dashboard displays role/worker stage codes (e.g., `worker_3_leased`, `independent_qc_start`, `merger_local_commit`), event time, task ID, status and tool counts; it receives **no code, prompts, architecture text, source paths or raw terminal output**. Upload failures leave durable local outbox events for `sync`. The Cloudflare dashboard is a **monitor**, not a remote command channel.

## 8. What the current implementation DOES NOT guarantee

- It is *not* a live-tested, fully autonomous self-healing JARVIS. No self-updater, host-service cutover, system-critical mirror migration, or unattended production release.
- Completion means local candidate with independent QC and optionally local integration. It does **not** mean deployed to Cloudflare or released to GitHub.
- A Codex workspace sandbox + a Docker test container are important controls, not complete protection from malicious/generated code; keep production credentials and personal data away.
- Long-running rate limits, unknown model entitlement, provider errors, Docker runtime security, test coverage quality and host-dependent behavior require on-device verification.
- The first prototype schedules 5 *coding/repair slots*, not arbitrary nested agent swarms. The Supervisor, independent QC and Merger are additional role-specific Codex sessions.
