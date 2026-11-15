# Owner-operated Cloudflare deployment

Astra One's Cloudflare Worker is **read-only from the browser's perspective**. It accepts authenticated metadata from the Windows engine and serves authenticated dashboards. The Cloudflare service cannot run CodeX, access your computer or read the final architecture. It does not reuse the existing `jarvis-coordinator` secrets or D1 database.

## Deploy when you choose

In PowerShell from the installed `Astra-One` folder:

```powershell
Set-Location "$HOME\Projects\Astra-One-Test\Astra-One\cloudflare\astra-one-monitor"
npm install
npx wrangler login
npx wrangler d1 create astra-one-monitor --location apac
Copy-Item .\wrangler.toml.example .\wrangler.toml
notepad .\wrangler.toml
```

In Notepad replace `REPLACE_WITH_UUID_FROM_WRANGLER_D1_CREATE` with the UUID printed by `d1 create`. Then:

```powershell
npx wrangler d1 execute astra-one-monitor --remote --file=.\schema.sql
npx wrangler secret put ASTRA_INGEST_TOKEN
npx wrangler secret put ASTRA_VIEW_TOKEN
npx wrangler deploy
```

Create **two different random 32-byte tokens** and enter them into the corresponding secure CLI prompts. Store the values privately (e.g., a password manager), not in your Git repository. Example PowerShell token generation (run twice; don't screenshot it):

```powershell
$bytes = New-Object byte[] 32
[System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
[Convert]::ToBase64String($bytes)
```

`wrangler deploy` prints the **actual** URL; use that, do not guess a Workers subdomain. Open it to see the dashboard; log in with `ASTRA_VIEW_TOKEN`.

## Configure local metadata sync

The following only sets variables in the **current PowerShell terminal**. It does not start SDA:

```powershell
$env:ASTRA_MONITOR_URL = 'https://ACTUAL-WORKERS-URL'
$env:ASTRA_MONITOR_INGEST_TOKEN = 'PASTE_YOUR_INGEST_TOKEN'
python -m astra_one sync
```

When you later run Astra One in the same terminal, these variables will be inherited. To avoid displaying a long-lived secret in PowerShell history, prefer setting the ingest token through an OS-managed secure environment, not an inline string. Never place it inside a repository, task JSON, issue, prompt or screenshot.

For a normal event delivery, `POST /api/events` uses the ingest bearer token, while `GET /api/summary`, `/api/runs`, and `/api/events?run_id=...` require the **different** view bearer token. Tokens are stored as Cloudflare Secrets. The web UI keeps the view token in memory for that tab only. Rate limits, fine-grained accounts, rotation, and SSO are not part of this prototype. Consider Cloudflare Access before exposing the dashboard beyond personal use.

## Verify after deploy

```powershell
Invoke-RestMethod 'https://ACTUAL-WORKERS-URL/api/health'
# Expect: { ok: true, service: 'astra-one-monitor' }
```

The dashboard will initially show no runs. That's expected until a later owner-approved architecture and coding task are started.
