param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [switch]$NoPush,
    [switch]$NoCommit,
    [switch]$NoDeploy,
    [switch]$AllowDirty,
    [string]$RemoteHost = "ubuntu@43.160.240.244",
    [string]$IdentityFile = "$env:USERPROFILE\.ssh\id_ed25519"
)

$ErrorActionPreference = "Stop"
$env:GIT_HTTP_LOW_SPEED_LIMIT = "1"
$env:GIT_HTTP_LOW_SPEED_TIME = "120"
$env:GIT_SSH_COMMAND = "ssh -o ConnectTimeout=15 -o ServerAliveInterval=15 -o ServerAliveCountMax=4"

$AllowedFiles = @(
    "dash/data/codex-usage.json",
    "dash/data/codex-usage.js"
)

$LogDir = Join-Path $RepoRoot "logs"
$LogPath = Join-Path $LogDir "local-codex-usage-report.log"
$LockPath = Join-Path $env:TEMP "maxnow-local-codex-usage-report.lock"

function Write-ReportLog {
    param([string]$Message)
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$stamp] $Message"
    Write-Host $line
    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir | Out-Null
    }
    Add-Content -Path $LogPath -Value $line -Encoding UTF8
}

function Invoke-Step {
    param(
        [string]$Label,
        [scriptblock]$Block
    )
    Write-ReportLog $Label
    & $Block
}

function Get-GitDirtyPaths {
    param([string[]]$StatusLines)
    $paths = @()
    foreach ($line in $StatusLines) {
        if ($line.Length -lt 4) {
            continue
        }
        $path = $line.Substring(3).Trim()
        if ($path.Contains(" -> ")) {
            $path = ($path -split " -> ", 2)[1]
        }
        $paths += ($path -replace "\\", "/")
    }
    return $paths
}

function Assert-NoBlockingDirtyFiles {
    param([string]$Stage)
    if ($AllowDirty) {
        return
    }
    $status = @(git status --porcelain)
    $paths = Get-GitDirtyPaths -StatusLines $status
    $blocking = @($paths | Where-Object { $AllowedFiles -notcontains $_ })
    if ($blocking.Count -gt 0) {
        throw "$Stage has unrelated dirty files: $($blocking -join ', ')"
    }
}

function Assert-CleanWorktree {
    param([string]$Stage)
    if ($AllowDirty) {
        return
    }
    $status = @(git status --porcelain)
    if ($status.Count -gt 0) {
        $paths = Get-GitDirtyPaths -StatusLines $status
        throw "$Stage requires a clean worktree: $($paths -join ', ')"
    }
}

$lockStream = $null
try {
    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir | Out-Null
    }
    $lockStream = [System.IO.File]::Open($LockPath, [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)

    Set-Location $RepoRoot
    Write-ReportLog "local Codex usage report start"

    $branch = (git branch --show-current).Trim()
    if ($branch -ne "main") {
        throw "expected local reporting worktree to be on main, got '$branch'"
    }

    Assert-CleanWorktree -Stage "before refresh"

    Invoke-Step "pull latest origin/main" {
        git pull --ff-only origin main
    }

    Invoke-Step "refresh local Codex usage ledger" {
        python scripts/update_data.py codex-usage --source-only
    }

    Invoke-Step "run consistency check" {
        python scripts/check.py
    }

    Assert-NoBlockingDirtyFiles -Stage "after refresh"

    $changedAllowed = @(git status --porcelain -- $AllowedFiles)
    if ($changedAllowed.Count -eq 0) {
        Write-ReportLog "no Codex usage data changes to report"
        return
    }

    if ($NoCommit) {
        $paths = Get-GitDirtyPaths -StatusLines $changedAllowed
        Write-ReportLog "skip commit because -NoCommit was set; changed files: $($paths -join ', ')"
        return
    }

    Invoke-Step "stage generated usage ledgers" {
        git add -- $AllowedFiles
    }

    $summary = @(git diff --cached --name-only)
    Write-ReportLog "staged: $($summary -join ', ')"

    Invoke-Step "commit generated usage ledgers" {
        git commit -m "Update local Codex token usage"
    }

    if ($NoPush) {
        Write-ReportLog "skip push because -NoPush was set"
    } else {
        Invoke-Step "push generated usage ledgers to origin/main" {
            git push origin HEAD:main
        }
        if ($NoDeploy) {
            Write-ReportLog "-NoDeploy is deprecated; server token merge is scheduled independently"
        }
    }

    Write-ReportLog "local Codex usage report ok"
} catch {
    Write-ReportLog "local Codex usage report failed: $($_.Exception.Message)"
    throw
} finally {
    if ($lockStream) {
        $lockStream.Dispose()
    }
}
