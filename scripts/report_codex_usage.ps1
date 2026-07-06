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

$AllowedFiles = @(
    "dash/data/codex-usage.json",
    "dash/data/codex-usage.js",
    "dash/data/token-usage.json",
    "dash/data/token-usage.js"
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

function Invoke-ServerTokenMerge {
    if ($NoDeploy) {
        Write-ReportLog "skip server token merge because -NoDeploy was set"
        return
    }

    $sshArgs = @()
    if ($IdentityFile -and (Test-Path $IdentityFile)) {
        $sshArgs += @("-i", $IdentityFile)
    }
    $sshArgs += @($RemoteHost)

    Write-ReportLog "merge token usage on server without refreshing server codex-usage"
    $remoteCommand = @'
set -e
cd /var/www/maxnow-dashboard

usage_units() {
  python3 - "$1" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
try:
    data = json.loads(path.read_text(encoding="utf-8"))
except Exception:
    print(0)
    raise SystemExit
summary = data.get("summary") if isinstance(data, dict) else {}
if not isinstance(summary, dict):
    summary = {}
total = int(summary.get("totalTokens") or data.get("totalTokens") or 0)
runs = int(summary.get("runs") or data.get("runs") or 0)
print(total + runs)
PY
}

restore_runtime_pair() {
  name="$1"
  backup_json="$backup_dir/$name.json"
  backup_js="$backup_dir/$name.js"
  target_json="dash/data/$name.json"
  target_js="dash/data/$name.js"

  if [ ! -f "$backup_json" ]; then
    return
  fi

  backup_units="$(usage_units "$backup_json")"
  target_units="$(usage_units "$target_json")"
  if [ "$backup_units" -gt 0 ] || [ "$target_units" -eq 0 ]; then
    cp -a "$backup_json" "$target_json"
    if [ -f "$backup_js" ]; then cp -a "$backup_js" "$target_js"; fi
    echo "[ok] restored $name from server runtime backup"
  else
    echo "[warn] skipped empty $name backup because current ledger has usage"
  fi
}

refresh_openclaw_if_empty() {
  openclaw_units="$(usage_units dash/data/openclaw-usage.json)"
  if [ "$openclaw_units" -gt 0 ]; then
    return
  fi
  if ! sudo -n test -d /root/.openclaw 2>/dev/null; then
    echo "[warn] OpenClaw ledger is empty and /root/.openclaw is not readable via sudo"
    return
  fi

  echo "[warn] OpenClaw ledger is empty; refreshing it with root OpenClaw state"
  sudo -n python3 scripts/update_data.py openclaw-usage
  sudo -n chown ubuntu:www-data dash/data/openclaw-usage.json dash/data/openclaw-usage.js dash/data/token-usage.json dash/data/token-usage.js logs/openclaw-usage.log logs/token-usage.log 2>/dev/null || true
}

backup_root="/tmp/maxnow-local-codex-usage-report"
backup_dir="$backup_root/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup_dir"
cp -a dash/data/openclaw-usage.json "$backup_dir/openclaw-usage.json" 2>/dev/null || true
cp -a dash/data/openclaw-usage.js "$backup_dir/openclaw-usage.js" 2>/dev/null || true
cp -a dash/data/codex-server-usage.json "$backup_dir/codex-server-usage.json" 2>/dev/null || true
cp -a dash/data/codex-server-usage.js "$backup_dir/codex-server-usage.js" 2>/dev/null || true
ln -sfn "$backup_dir" "$backup_root/latest" 2>/dev/null || true

git stash push -m before-local-codex-usage-report -- dash/data/openclaw-usage.json dash/data/openclaw-usage.js dash/data/codex-usage.json dash/data/codex-usage.js dash/data/codex-macos-usage.json dash/data/codex-macos-usage.js dash/data/codex-server-usage.json dash/data/codex-server-usage.js dash/data/token-usage.json dash/data/token-usage.js dash/data/project-meta.json dash/data/project-meta.js >/dev/null 2>&1 || true
git pull --ff-only origin main
restore_runtime_pair openclaw-usage
restore_runtime_pair codex-server-usage
refresh_openclaw_if_empty
python3 scripts/update_data.py token-usage
python3 scripts/check.py
'@
    $encodedCommand = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($remoteCommand))
    $remoteInvocation = "printf '%s' '$encodedCommand' | base64 -d | bash"
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & ssh @sshArgs $remoteInvocation 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    foreach ($line in $output) {
        Write-ReportLog "server: $line"
    }
    if ($exitCode -ne 0) {
        throw "server token merge failed with exit code $exitCode"
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
        python scripts/update_data.py codex-usage
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
        Invoke-ServerTokenMerge
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
