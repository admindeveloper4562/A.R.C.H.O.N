# Windows and WSL installation contract

The Windows path is a local harness for the Linux Astra controller. It does
not turn Windows into a second Master, does not pull executable work from
Cloudflare, and does not claim native iOS or TWS support.

## Check only

From an elevated-free PowerShell session in the repository:

```powershell
& .\infra\windows\install.ps1 -Mode Check
```

The check verifies only the local presence of WSL, Git, Python, Ollama and the
named `ARCHON-Ubuntu-24.04` distribution. It never reads credentials, starts
Ollama, installs a distribution, or changes Task Scheduler.

## Optional startup task

The explicit task is limited to the deterministic local QC/Merger pass. It
cannot claim a builder lease or execute a Cloudflare queue item. Preview the
registration first:

```powershell
& .\infra\windows\install.ps1 -Mode RegisterTask -WhatIf
```

Only an owner may decide to register it:

```powershell
& .\infra\windows\install.ps1 -Mode RegisterTask -Confirm:$false
```

The task runs `qc-merge` inside WSL and writes only to the canonical Astra
state and local integration worktree. Review `STOP`, `PAUSE`, and
`PAUSED_QUOTA` before clearing or starting any work.

## Evidence boundary

Windows/Ollama measurements must come from the actual Windows host and are not
fabricated by Linux or WSL checks. Xcode/iOS remains `deferred_unclaimed`, and
TWS remains out of scope for REL.
