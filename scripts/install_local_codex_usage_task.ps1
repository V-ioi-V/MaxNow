param(
    [string]$TaskName = "MaxNow-Local-Codex-Usage-Report",
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [int]$EveryMinutes = 60,
    [switch]$NoDeploy,
    [switch]$RunNow
)

$ErrorActionPreference = "Stop"

$HiddenLauncher = Join-Path $RepoRoot "scripts\report_codex_usage_hidden.vbs"
if (-not (Test-Path $HiddenLauncher)) {
    throw "hidden launcher not found: $HiddenLauncher"
}

$argument = "`"$HiddenLauncher`""
if ($NoDeploy) {
    Write-Host "[warn] -NoDeploy is deprecated; server token merge runs on its own schedule."
}

$action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument $argument -WorkingDirectory $RepoRoot
$startAt = (Get-Date).AddMinutes(5)
$trigger = New-ScheduledTaskTrigger -Once -At $startAt -RepetitionInterval (New-TimeSpan -Minutes $EveryMinutes) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 30) -Hidden
$description = "Refresh local Codex token usage, commit generated MaxNow usage ledger, and push to origin/main."

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description $description -Force | Out-Null

Write-Host "[ok] registered scheduled task '$TaskName' every $EveryMinutes minutes"
Write-Host "[ok] log: $(Join-Path $RepoRoot 'logs\local-codex-usage-report.log')"

if ($RunNow) {
    Start-ScheduledTask -TaskName $TaskName
    Write-Host "[ok] started scheduled task '$TaskName'"
}
