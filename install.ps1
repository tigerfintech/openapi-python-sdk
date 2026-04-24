# Tiger Open API Python SDK — Windows Installer (PowerShell)
#
# Usage:
#   irm https://raw.githubusercontent.com/tigerfintech/openapi-python-sdk/master/install.ps1 | iex
#
# Options (via environment variables):
#   $env:TIGEROPEN_INSTALL_METHOD = "uv"   -- force install method (uv|pipx|pip)
#   $env:TIGEROPEN_NO_MODIFY_PATH = "1"    -- skip PATH modification

$ErrorActionPreference = "Stop"

# ─── Colors ──────────────────────────────────────────────────────────────────

function Write-Info  { param($msg) Write-Host "info: $msg" -ForegroundColor Green }
function Write-Warn  { param($msg) Write-Host "warn: $msg" -ForegroundColor Yellow }
function Write-Err   { param($msg) Write-Host "error: $msg" -ForegroundColor Red; exit 1 }

function Has-Command { param($cmd) return [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

# ─── Banner ──────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "  Tiger Open API Python SDK Installer" -ForegroundColor Cyan
Write-Host "  ─────────────────────────────────────"
Write-Host ""

# ─── Python Detection ────────────────────────────────────────────────────────

$PYTHON = $null
foreach ($candidate in @("python", "python3", "py")) {
    if (Has-Command $candidate) {
        $PYTHON = $candidate
        break
    }
}

if (-not $PYTHON) {
    Write-Err "Python not found. Install Python 3.8+ first:`n  https://www.python.org/downloads/`n  Or: winget install Python.Python.3"
}

$PY_VERSION = & $PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
$PY_MAJOR   = & $PYTHON -c "import sys; print(sys.version_info.major)" 2>$null
$PY_MINOR   = & $PYTHON -c "import sys; print(sys.version_info.minor)" 2>$null

if (-not $PY_VERSION) { Write-Err "Could not determine Python version" }
if ([int]$PY_MAJOR -lt 3 -or ([int]$PY_MAJOR -eq 3 -and [int]$PY_MINOR -lt 8)) {
    Write-Err "Python 3.8+ required, found $PY_VERSION"
}

Write-Info "Found Python $PY_VERSION ($PYTHON)"

# ─── Choose Install Method ───────────────────────────────────────────────────

$METHOD = $env:TIGEROPEN_INSTALL_METHOD

if (-not $METHOD) {
    if (Has-Command "uv")   { $METHOD = "uv" }
    elseif (Has-Command "pipx") { $METHOD = "pipx" }
    else { $METHOD = "pip" }
}

Write-Info "Install method: $METHOD"

# ─── Install ─────────────────────────────────────────────────────────────────

switch ($METHOD) {
    "uv" {
        if (-not (Has-Command "uv")) { Write-Err "uv not found. Install with: irm https://astral.sh/uv/install.ps1 | iex" }
        Write-Info "Installing tigeropen via uv..."
        & uv pip install tigeropen --upgrade
    }
    "pipx" {
        if (-not (Has-Command "pipx")) { Write-Err "pipx not found. Install with: pip install pipx" }
        Write-Info "Installing tigeropen via pipx..."
        & pipx install tigeropen --force
    }
    "pip" {
        Write-Info "Installing tigeropen via pip..."
        & $PYTHON -m pip install tigeropen --upgrade
    }
    default {
        Write-Err "Unknown install method: $METHOD (use uv, pipx, or pip)"
    }
}

# ─── Verify Installation ─────────────────────────────────────────────────────

$SDK_VERSION = & $PYTHON -c "from tigeropen import __VERSION__; print(__VERSION__)" 2>$null
if (-not $SDK_VERSION) {
    Write-Err "Installation failed — could not import tigeropen"
}

Write-Info "tigeropen v$SDK_VERSION installed successfully"

# ─── PATH Setup ──────────────────────────────────────────────────────────────

if ($env:TIGEROPEN_NO_MODIFY_PATH -ne "1") {
    $TIGEROPEN_BIN = Get-Command "tigeropen" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source

    if (-not $TIGEROPEN_BIN) {
        # Check common pip/uv install locations on Windows
        $candidates = @(
            "$env:APPDATA\Python\Scripts\tigeropen.exe",
            "$env:LOCALAPPDATA\Programs\Python\Python$($PY_MAJOR)$($PY_MINOR)\Scripts\tigeropen.exe",
            "$env:LOCALAPPDATA\Programs\Python\Python$($PY_MAJOR)$($PY_MINOR.PadLeft(2,'0'))\Scripts\tigeropen.exe"
        )
        foreach ($path in $candidates) {
            if (Test-Path $path) {
                $TIGEROPEN_BIN = $path
                break
            }
        }
    }

    if ($TIGEROPEN_BIN) {
        Write-Info "CLI installed at: $TIGEROPEN_BIN"
        $BIN_DIR = Split-Path $TIGEROPEN_BIN

        # Check if already in PATH
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if ($currentPath -notlike "*$BIN_DIR*") {
            [Environment]::SetEnvironmentVariable("PATH", "$BIN_DIR;$currentPath", "User")
            Write-Info "Added $BIN_DIR to user PATH"
            Write-Warn "Restart your terminal (or open a new PowerShell window) for PATH changes to take effect"
        }
    } else {
        Write-Warn "tigeropen installed but CLI not found on PATH"
        Write-Warn "You may need to add pip's Scripts directory to your PATH manually"
        Write-Warn "Run: & $PYTHON -m site --user-site  (then look for the Scripts sibling dir)"
    }
}

# ─── Success Message ─────────────────────────────────────────────────────────

Write-Host ""
Write-Host "  Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "  Getting started:"
Write-Host ""
Write-Host "    # Set up your API credentials" -ForegroundColor Cyan
Write-Host "    tigeropen config init"
Write-Host ""
Write-Host "    # Or set environment variables" -ForegroundColor Cyan
Write-Host "    `$env:TIGEROPEN_TIGER_ID   = 'your_tiger_id'"
Write-Host "    `$env:TIGEROPEN_PRIVATE_KEY = 'your_private_key'"
Write-Host "    `$env:TIGEROPEN_ACCOUNT     = 'your_account'"
Write-Host ""
Write-Host "    # Query market data" -ForegroundColor Cyan
Write-Host "    tigeropen quote briefs AAPL TSLA"
Write-Host "    tigeropen quote bars AAPL --period day --limit 10"
Write-Host ""
Write-Host "    # Manage orders" -ForegroundColor Cyan
Write-Host "    tigeropen trade order list"
Write-Host "    tigeropen account assets"
Write-Host ""
Write-Host "  Documentation: https://docs.itigerup.com/docs/" -ForegroundColor Cyan
Write-Host "  GitHub:        https://github.com/tigerfintech/openapi-python-sdk" -ForegroundColor Cyan
Write-Host ""
