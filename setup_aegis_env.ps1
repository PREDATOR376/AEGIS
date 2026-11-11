# ==============================================================================
# AEGIS Requirement R1 Automated Provisioning Script
# ==============================================================================
$ErrorActionPreference = "Stop"
Write-Host "=== [AEGIS] Starting R1 Environment Setup ===" -ForegroundColor Cyan

$VenvDir = "e:\AEGIS\aegis_env"
$PythonExe = "$VenvDir\Scripts\python.exe"
$PytestExe = "$VenvDir\Scripts\pytest.exe"
$ReqFile = "e:\AEGIS\requirements.txt"

# 1. Check if virtual environment already exists and is valid
if (Test-Path $PythonExe) {
    Write-Host "[OK] Existing virtual environment found at $VenvDir" -ForegroundColor Green
} else {
    Write-Host "[INFO] Bootstrapping Python 3.11..." -ForegroundColor Yellow

    # Try uv bootstrap first (fastest)
    $UvExe = "$HOME\.local\bin\uv.exe"
    if (-not (Test-Path $UvExe)) {
        Write-Host "[INFO] Installing Astral uv..."
        try {
            powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
        } catch {
            Write-Warning "PowerShell irm failed, downloading uv zip..."
            $uvZip = "$env:TEMP\uv.zip"
            curl.exe -L -o $uvZip "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip"
            New-Item -ItemType Directory -Force -Path "$HOME\.local\bin" | Out-Null
            tar.exe -xf $uvZip -C "$HOME\.local\bin"
        }
    }

    if (Test-Path $UvExe) {
        Write-Host "[OK] uv is available at $UvExe" -ForegroundColor Green
        Write-Host "[INFO] Installing Python 3.11 via uv..."
        & $UvExe python install 3.11

        Write-Host "[INFO] Creating venv at $VenvDir..."
        & $UvExe venv $VenvDir --python 3.11
    } else {
        # Fallback to python.org official installer
        Write-Host "[INFO] uv unavailable; falling back to official python.org installer..." -ForegroundColor Yellow
        $installer = "$env:TEMP\python-3.11.9-amd64.exe"
        curl.exe -L -o $installer "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
        $pyHome = "$env:LOCALAPPDATA\Programs\Python\Python311"
        Start-Process -FilePath $installer -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 TargetDir=""$pyHome""" -Wait
        
        Write-Host "[INFO] Creating venv at $VenvDir..."
        & "$pyHome\python.exe" -m venv $VenvDir
    }
}

# 2. Verify venv python.exe exists
if (-not (Test-Path $PythonExe)) {
    throw "CRITICAL: Virtual environment python.exe not found at $PythonExe"
}
$pyVer = & $PythonExe --version
Write-Host "[OK] Python verified: $pyVer" -ForegroundColor Green

# 3. Install requirements
Write-Host "[INFO] Installing dependencies from $ReqFile..." -ForegroundColor Yellow
$UvExe = "$HOME\.local\bin\uv.exe"
if (Test-Path $UvExe) {
    & $UvExe pip install --python $PythonExe -r $ReqFile pytest
} else {
    & $PythonExe -m pip install --upgrade pip
    & $PythonExe -m pip install -r $ReqFile
}

# 4. Verify pytest.exe exists
if (-not (Test-Path $PytestExe)) {
    Write-Warning "pytest.exe not found in Scripts, installing pytest explicitly..."
    if (Test-Path $UvExe) {
        & $UvExe pip install --python $PythonExe pytest
    } else {
        & $PythonExe -m pip install pytest
    }
}
$pytestVer = & $PytestExe --version
Write-Host "[OK] Pytest verified: $pytestVer" -ForegroundColor Green

# 5. Full import verification
Write-Host "[INFO] Verifying package imports..." -ForegroundColor Yellow
& $PythonExe -c "import dxcam, numpy, cv2, imgui, glfw, OpenGL, win32api, pytest; print('ALL REQUIRED PACKAGES IMPORTED SUCCESSFULLY')"

# 6. Execute pytest on the test suite
Write-Host "[INFO] Running pytest test suite..." -ForegroundColor Cyan
& $PytestExe -v e:\AEGIS\tests\test_health_extractor.py

Write-Host "=== [AEGIS] R1 Environment Setup COMPLETE ===" -ForegroundColor Green
