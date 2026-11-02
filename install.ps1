# Chwezi PDF Suite - Windows installer / updater
# Run once on a new machine to install everything, or again to update.
# Requires PowerShell 5.1+ (built into Windows 10/11).

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$PYTHON_VERSION = "3.12.10"
$PYTHON_URL     = "https://www.python.org/ftp/python/$PYTHON_VERSION/python-$PYTHON_VERSION-amd64.exe"
$INSTALLER_PATH = "$env:TEMP\python-installer.exe"

function Write-Step($msg) {
    Write-Host ""
    Write-Host "==> $msg" -ForegroundColor Cyan
}

function Write-Ok($msg) {
    Write-Host "    OK  $msg" -ForegroundColor Green
}

function Write-Fail($msg) {
    Write-Host "    ERR $msg" -ForegroundColor Red
}

# Banner
Write-Host ""
Write-Host "=====================================================" -ForegroundColor Blue
Write-Host "  Chwezi PDF Suite - Install / Update (Windows)  " -ForegroundColor Blue
Write-Host "=====================================================" -ForegroundColor Blue

# 1. Python
Write-Step "Checking Python installation"

$pythonCmd = $null
foreach ($candidate in @("python", "python3", "py")) {
    try {
        $ver = & $candidate --version 2>&1
        if ($ver -match "Python 3") {
            $pythonCmd = $candidate
            Write-Ok "Found: $ver"
            break
        }
    } catch { }
}

if (-not $pythonCmd) {
    Write-Host "    Python 3 not found. Downloading installer..." -ForegroundColor Yellow
    Write-Host "    URL: $PYTHON_URL"

    try {
        Invoke-WebRequest -Uri $PYTHON_URL -OutFile $INSTALLER_PATH -UseBasicParsing
        Write-Ok "Downloaded installer to $INSTALLER_PATH"
    } catch {
        Write-Fail "Failed to download Python installer: $_"
        Write-Host "    Please install Python 3 manually from https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }

    Write-Host "    Running installer (this may take a minute)..." -ForegroundColor Yellow
    $proc = Start-Process -FilePath $INSTALLER_PATH `
        -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0" `
        -Wait -PassThru
    Remove-Item $INSTALLER_PATH -Force

    if ($proc.ExitCode -ne 0) {
        Write-Fail "Python installer exited with code $($proc.ExitCode)"
        exit 1
    }
    Write-Ok "Python $PYTHON_VERSION installed"

    # Refresh PATH so python is available in this session
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "User") + ";" +
                [System.Environment]::GetEnvironmentVariable("PATH", "Machine")

    $pythonCmd = "python"
}

# 2. pip
Write-Step "Upgrading pip"
& $pythonCmd -m ensurepip --upgrade 2>&1 | Out-Null
& $pythonCmd -m pip install --upgrade pip --quiet
Write-Ok "pip up to date"

# 3. Dependencies
Write-Step "Installing / upgrading project dependencies"

$req = Join-Path $PSScriptRoot "requirements.txt"
if (-not (Test-Path $req)) {
    Write-Fail "requirements.txt not found at $req"
    exit 1
}

& $pythonCmd -m pip install --upgrade -r $req
if ($LASTEXITCODE -ne 0) {
    Write-Fail "pip install failed (exit $LASTEXITCODE)"
    exit 1
}
Write-Ok "All dependencies installed / up to date"

# Done
Write-Host ""
Write-Host "=====================================================" -ForegroundColor Green
Write-Host "  Setup complete! Run the suite with:               " -ForegroundColor Green
Write-Host "    python index-app.py                             " -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green
Write-Host ""
