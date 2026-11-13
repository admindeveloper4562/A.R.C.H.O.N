# Windows: install Astra One, but do not start SDA yet

**Prerequisites:** Windows PowerShell 5.1+, Python 3.11+, Git for Windows, Codex CLI, Ollama (already serving Qwen3 8B). Authenticate Git to read your **private** `personal-jarvis` repository.

1. Download `Astra-One-v0.1.0.zip` from the ChatGPT attachment and save it to `Downloads`. Do not use an unauthenticated third-party download URL.
2. Open PowerShell, paste the block below. The script **refuses to overwrite** an existing lab.

```powershell
$base = Join-Path $HOME 'Projects\Astra-One-Test'
$zip = Join-Path $HOME 'Downloads\Astra-One-v0.1.0.zip'
if (-not (Test-Path -LiteralPath $zip)) { throw "Download $zip first" }
if (Test-Path -LiteralPath $base) { throw "Lab already exists: $base. Preserve it; choose a new path." }
New-Item -ItemType Directory -Path $base -Force | Out-Null
Expand-Archive -LiteralPath $zip -DestinationPath $base
$source = Join-Path $base 'jarvis-source'
git clone --single-branch --branch feature/jarvis-v2-expanded-architecture-20261113 https://github.com/admindeveloper4562/personal-jarvis.git $source
if ($LASTEXITCODE -ne 0) { throw "Git clone failed; check GitHub authentication" }
Set-Location (Join-Path $base 'Astra-One')
python -m unittest discover -s tests -p 'test_*.py' -v
if ($LASTEXITCODE -ne 0) { throw "Astra unit tests failed" }
python -m astra_one doctor --source $source
python -m astra_one init --source $source
python -m astra_one status
```

**Expected:** Python tests pass, state is initialized, `architecture_approved: false`, no tasks, Codex engine stopped. It does NOT start Codex, download models, deploy to Cloudflare, change your original JARVIS checkout or start the old Workhorse. The newly cloned private repo contains the SDA draft architecture but is a separate lab source.

## Cloudflare next

Follow [Cloudflare deployment](CLOUDFLARE_DEPLOY.md) after installation. The dashboard can be deployed with an empty event database. It will remain empty until later work begins.

## AFTER you provide the final JARVIS v2 architecture

The following is a **future operator procedure, not part of the install block**:

```powershell
Set-Location "$HOME\Projects\Astra-One-Test\Astra-One"
python -m astra_one architecture import --file "C:\path\to\JARVIS-V2-FINAL.md"
# Inspect the full imported document, then copy the printed sha256 into the next command:
python -m astra_one architecture approve --sha256 "PASTE_SHA256_FROM_IMPORT"
# Create task JSON from the approved architecture; example format in examples/task.sample.json.
python -m astra_one enqueue --file "C:\path\to\first-approved-task.json"
python -m astra_one tasks
# Starts exactly one queued task. Not enabled until you explicitly run this:
python -m astra_one run-once --model qwen3:8b --context 16384
```

Each run creates a NEW separate `feature/astra-*` Git worktree in `%LOCALAPPDATA%\AstraOne\workspaces`, reports progress and stops at `awaiting_review`. Nothing is merged, pushed, deleted or deployed by the coding worker. You must inspect its branch/diff, approve the task explicitly and integrate it into the **isolated local Astra integration branch** before dependent tasks can run. Cloudflare has no authority to trigger integration.

## Local Ollama optimization (already verified on your machine)

Run Ollama as one process only. Your measured 16K/Q8 configuration achieved about 53–63 generated tokens/s on an RTX 5060 Ti 8 GB.

```powershell
# Only if Ollama is NOT already running; otherwise change its service/tray settings and restart it:
$env:OLLAMA_CONTEXT_LENGTH = '16384'
$env:OLLAMA_FLASH_ATTENTION = '1'
$env:OLLAMA_KV_CACHE_TYPE = 'q8_0'
$env:OLLAMA_NUM_PARALLEL = '1'
ollama serve
```

In another window, check `ollama ps`. No model speed is guaranteed for future larger task prompts.

## Optional local planner after blueprint approval

```powershell
# Example: select the SDA section in a large Markdown architecture document.
python -m astra_one plan --focus SDA --count 4
# Open the private proposed-plan JSON printed by the planner and review every item.
python -m astra_one enqueue-plan --file 'C:\PATH\TO\REVIEWED-PLAN.json'
# After the first task has passed independent human review:
python -m astra_one approve-task ASTRA-101
python -m astra_one integrate ASTRA-101 --confirm
```

The local planner uses Ollama `qwen3:8b` directly for structured task proposals only. It does not send the blueprint to Cloudflare or auto-enqueue tasks. `integrate` makes a local Git feature-branch commit but does not push, deploy, or modify `main`/`develop`.
