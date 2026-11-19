[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param(
    [ValidateSet('Check', 'RegisterTask')]
    [string] $Mode = 'Check',
    [ValidatePattern('^[A-Za-z0-9._-]{1,64}$')]
    [string] $Distribution = 'ARCHON-Ubuntu-24.04',
    [ValidatePattern('^[A-Za-z0-9 ._-]{1,80}$')]
    [string] $TaskName = 'ARCHON-Astra-QC-Merger',
    [ValidateRange(1, 1440)]
    [int] $IntervalMinutes = 3
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Test-Executable([string] $Name) {
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Get-WslDistributionNames {
    if (-not (Test-Executable 'wsl.exe')) {
        return @()
    }
    return @((& wsl.exe --list --quiet 2>$null) | ForEach-Object { $_.Trim() } | Where-Object { $_ })
}

$checks = [ordered]@{
    powershell = $true
    wsl = (Test-Executable 'wsl.exe')
    git = (Test-Executable 'git.exe')
    python = (Test-Executable 'python.exe')
    ollama = (Test-Executable 'ollama.exe')
    distribution = ((Get-WslDistributionNames) -contains $Distribution)
}

if ($Mode -eq 'Check') {
    [pscustomobject]@{
        status = if (($checks.Values -contains $false)) { 'missing_prerequisite' } else { 'ready' }
        distribution = $Distribution
        checks = [pscustomobject]$checks
        remote_queue = 'disabled'
        credentials = 'not inspected'
    } | ConvertTo-Json -Depth 4
    if ($checks.Values -contains $false) { exit 2 }
    exit 0
}

if ($checks.Values -contains $false) {
    throw 'RegisterTask requires the WSL, Git, Python, Ollama and named ARCHON distribution checks to pass.'
}

$taskCommand = 'cd /home/archon/ARCHON-astra-source/bootstrap/astra-one && python3 -m astra_one.linux_cli --home /home/archon/.local/state/archon-astra qc-merge --limit 1 --test-image archon-python:3.12-git-20261119 --max-seconds 1800'
$actionArguments = "--distribution $Distribution --user archon -- bash -lc `"$taskCommand`""
$action = New-ScheduledTaskAction -Execute 'wsl.exe' -Argument $actionArguments
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes $IntervalMinutes)
$description = 'ARCHON Astra One local QC and serialized Merger only; no builder, remote queue or deployment authority.'

if ($PSCmdlet.ShouldProcess($TaskName, 'register the explicit local QC/Merger startup task')) {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description $description -Force | Out-Null
    [pscustomobject]@{
        status = 'registered'
        task_name = $TaskName
        distribution = $Distribution
        remote_queue = 'disabled'
        credentials = 'not inspected'
    } | ConvertTo-Json -Depth 4
}
