param(
    [string]$TaskName = "MaxNow-Local-Codex-Usage-Report",
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [ValidateRange(0, 59)]
    [int]$ReportMinute = 2,
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
$now = Get-Date
$startAt = $now.Date.AddHours($now.Hour).AddMinutes($ReportMinute)
if ($startAt -le $now) {
    $startAt = $startAt.AddHours(1)
}
$trigger = New-ScheduledTaskTrigger -Once -At $startAt -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -Hidden
$description = "Refresh local Codex token usage, commit generated MaxNow usage ledger, and push to origin/main."

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description $description -Force | Out-Null

Write-Host "[ok] registered scheduled task '$TaskName' at minute $ReportMinute of every hour"
Write-Host "[ok] log: $(Join-Path $RepoRoot 'logs\local-codex-usage-report.log')"

if ($RunNow) {
    Start-ScheduledTask -TaskName $TaskName
    Write-Host "[ok] started scheduled task '$TaskName'"
}
