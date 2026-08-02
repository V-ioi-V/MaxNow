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
$ReportCommitMessage = "Update local Codex token usage"
$MaxPushAttempts = 3
if ($env:MAXNOW_CODEX_PUSH_ATTEMPTS) {
    $parsedPushAttempts = 0
    if (-not [int]::TryParse($env:MAXNOW_CODEX_PUSH_ATTEMPTS, [ref]$parsedPushAttempts) -or $parsedPushAttempts -lt 1) {
        throw "MAXNOW_CODEX_PUSH_ATTEMPTS must be a positive integer"
    }
    $MaxPushAttempts = $parsedPushAttempts
}

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

function Add-GitRuntimeToolsToPath {
    if (Get-Command openssl -ErrorAction SilentlyContinue) {
        return
    }

    $gitCommand = Get-Command git -ErrorAction Stop
    $gitRoot = Split-Path (Split-Path $gitCommand.Source -Parent) -Parent
    $gitUsrBin = Join-Path $gitRoot "usr\bin"
    if (Test-Path (Join-Path $gitUsrBin "openssl.exe")) {
        $env:PATH = "$gitUsrBin;$env:PATH"
    }
}

function Invoke-NativeStep {
    param(
        [string]$Label,
        [scriptblock]$Block
    )
    Write-ReportLog $Label
    & $Block
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "$Label failed with exit code $exitCode"
    }
}

function Invoke-NativeCapture {
    param(
        [string]$Label,
        [scriptblock]$Block
    )
    $output = @(& $Block)
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "$Label failed with exit code $exitCode"
    }
    return $output
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
    $status = @(Invoke-NativeCapture "inspect worktree for blocking files" { git status --porcelain })
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
    $status = @(Invoke-NativeCapture "inspect clean worktree" { git status --porcelain })
    if ($status.Count -gt 0) {
        $paths = Get-GitDirtyPaths -StatusLines $status
        throw "$Stage requires a clean worktree: $($paths -join ', ')"
    }
}

function Test-AllowedPath {
    param([string]$Path)
    return $AllowedFiles -contains ($Path -replace "\\", "/")
}

function Restore-InterruptedGeneratedFiles {
    if ($AllowDirty) {
        return
    }

    $status = @(Invoke-NativeCapture "inspect worktree before generated-file recovery" { git status --porcelain })
    if ($status.Count -eq 0) {
        return
    }

    Assert-NoBlockingDirtyFiles -Stage "before refresh"
    Write-ReportLog "recover generated usage files left by an interrupted run"
    Invoke-NativeStep "restore interrupted generated usage files" {
        git restore --staged --worktree -- $AllowedFiles
    }
    Assert-CleanWorktree -Stage "after generated-file recovery"
}

function Test-GitAncestor {
    param(
        [string]$Ancestor,
        [string]$Descendant
    )

    & git merge-base --is-ancestor $Ancestor $Descendant
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 0) {
        return $true
    }
    if ($exitCode -eq 1) {
        return $false
    }
    throw "git merge-base --is-ancestor failed with exit code $exitCode"
}

function Test-LocalOnlyCommitsAreGenerated {
    $commits = @(Invoke-NativeCapture "list local-only reporting commits" { git rev-list origin/main..HEAD })
    if ($commits.Count -eq 0) {
        return $false
    }

    foreach ($commit in $commits) {
        $subject = (Invoke-NativeCapture "inspect reporting commit subject" { git show -s --format=%s $commit }) -join "`n"
        if ($subject.Trim() -ne $ReportCommitMessage) {
            return $false
        }

        $paths = @(Invoke-NativeCapture "inspect reporting commit files" { git diff-tree --no-commit-id --name-only -r $commit })
        foreach ($path in $paths) {
            if ($path -and -not (Test-AllowedPath $path)) {
                return $false
            }
        }
    }

    return $true
}

function Sync-OriginMain {
    Invoke-NativeStep "fetch latest origin/main" {
        git fetch origin main
    }

    if (Test-GitAncestor "HEAD" "origin/main") {
        $head = (Invoke-NativeCapture "read local reporting commit" { git rev-parse HEAD }) -join ""
        $originHead = (Invoke-NativeCapture "read origin/main reporting commit" { git rev-parse origin/main }) -join ""
        if ($head.Trim() -ne $originHead.Trim()) {
            Invoke-NativeStep "fast-forward to origin/main" {
                git merge --ff-only origin/main
            }
        }
        return
    }

    if (-not (Test-LocalOnlyCommitsAreGenerated)) {
        throw "local main diverged with commits outside the generated Windows usage boundary; manual recovery required"
    }

    Write-ReportLog "recover generated-only local divergence from origin/main"
    Invoke-NativeStep "reset generated reporting commits to origin/main" {
        git reset --hard origin/main
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
    Add-GitRuntimeToolsToPath

    $branch = ((Invoke-NativeCapture "read reporting branch" { git branch --show-current }) -join "").Trim()
    if ($branch -ne "main") {
        throw "expected local reporting worktree to be on main, got '$branch'"
    }

    Restore-InterruptedGeneratedFiles

    $attempt = 1
    while ($attempt -le $MaxPushAttempts) {
        Sync-OriginMain

        Invoke-NativeStep "refresh local Codex usage ledger" {
            python scripts/update_data.py codex-usage --source-only
        }

        Invoke-NativeStep "run consistency check" {
            python scripts/check.py
        }

        Assert-NoBlockingDirtyFiles -Stage "after refresh"

        $changedAllowed = @(Invoke-NativeCapture "inspect generated usage changes" { git status --porcelain -- $AllowedFiles })
        if ($changedAllowed.Count -eq 0) {
            Write-ReportLog "no Codex usage data changes to report"
            break
        }

        if ($NoCommit) {
            $paths = Get-GitDirtyPaths -StatusLines $changedAllowed
            Write-ReportLog "skip commit because -NoCommit was set; changed files: $($paths -join ', ')"
            break
        }

        Invoke-NativeStep "stage generated usage ledgers" {
            git add -- $AllowedFiles
        }

        $summary = @(Invoke-NativeCapture "inspect staged usage changes" { git diff --cached --name-only })
        Write-ReportLog "staged: $($summary -join ', ')"

        Invoke-NativeStep "commit generated usage ledgers" {
            git commit -m $ReportCommitMessage
        }

        if ($NoPush) {
            Write-ReportLog "skip push because -NoPush was set"
            break
        }

        Write-ReportLog "push generated usage ledgers to origin/main (attempt $attempt/$MaxPushAttempts)"
        & git push origin HEAD:main
        $pushExitCode = $LASTEXITCODE
        if ($pushExitCode -eq 0) {
            break
        }

        Write-ReportLog "push failed with exit code $pushExitCode"
        if ($attempt -ge $MaxPushAttempts) {
            throw "push failed after $MaxPushAttempts attempts; the next scheduled run will retry safely"
        }

        $attempt += 1
        Write-ReportLog "push raced with another main update; resync and regenerate before retry"
        Start-Sleep -Seconds 2
    }

    if ($NoDeploy) {
        Write-ReportLog "-NoDeploy is deprecated; server token merge is scheduled independently"
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
