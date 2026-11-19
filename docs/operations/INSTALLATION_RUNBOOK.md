# ARCHON Astra One installation runbook

This runbook installs a reproducible local control-plane layout for the
`develop` branch. It does not modify `main`, create a second Master, edit the
canonical SQLite database directly, install credentials, or make a production
deployment claim.

## 1. Verify the installation contract

From the repository root:

```bash
python3 infra/verify_installation.py
python3 infra/verify_installation.py --platform linux
```

The verifier is read-only. It checks that every declared artifact and runbook
exists, that paths stay inside the checkout, and that iOS/TWS are not claimed.

## 2. Linux user installation

Use a dedicated non-root Linux user. Confirm the prerequisites and source
checkout first:

```bash
test "$(id -u)" -ne 0
python3 bootstrap/astra-one/scripts/linux_preflight.sh
python3 -m astra_one.linux_cli --home "$HOME/.local/state/archon-astra" status
```

Install the deterministic QC/Merger timer only after inspecting the unit files:

```bash
install -Dm644 infra/systemd/archon-astra.service "$HOME/.config/systemd/user/archon-astra.service"
install -Dm644 infra/systemd/archon-astra.timer "$HOME/.config/systemd/user/archon-astra.timer"
systemctl --user daemon-reload
systemctl --user enable --now archon-astra.timer
systemctl --user status archon-astra.timer archon-astra.service
```

The timer invokes `tools/astra_batch_cycle.sh`, which performs only the
deterministic Supervisor/QC/Merger pass. It does not launch a coding worker,
pull tasks from Cloudflare, push Git, or publish `develop`. A Main Codex builder
must still claim an approved task through Astra's `builder-claim` workflow.

## 3. Windows/WSL harness

In PowerShell, run the read-only check:

```powershell
& .\infra\windows\install.ps1 -Mode Check
```

Use `-Mode RegisterTask -WhatIf` to preview the optional startup task. If the
owner explicitly enables it, the task runs only local `qc-merge` in the named
WSL distribution. It does not start Ollama, inspect tokens, or create a second
controller. Windows-specific hardware and Ollama evidence must be measured on
the actual Windows host.

## 4. Optional Cloudflare metadata monitor

The monitor is optional and owner-operated. From
`bootstrap/astra-one/cloudflare/astra-one-monitor`:

```powershell
npm install
npm run typecheck
npm run smoke
Copy-Item .\wrangler.toml.example .\wrangler.toml
npx wrangler login
npx wrangler d1 list
```

Only after reviewing the existing account, binding and quota may an owner run
the remote schema/deploy commands in the Cloudflare guide. Never paste tokens
into Git, this chat, task JSON, logs or screenshots. The monitor stores bounded
progress metadata only; it is not a central executable task queue.

## 5. Deferred platforms and stop conditions

Native iOS/macOS installation is `deferred_unclaimed` until a real macOS/Xcode
environment and the required simulator or device are available. TWS is
`out_of_scope` for REL by owner-requested amendment. Neither is represented as
a passing installation check.

If a required tool, owner credential, quota, device, source ancestry, SQLite
integrity check, or safety control is missing, preserve the evidence and leave
the affected operation pending or blocked. Do not fabricate a platform result.
