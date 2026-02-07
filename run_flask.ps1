# =============================================================================
# CRATA AI - Growth Intelligence Dashboard (Flask)
# PowerShell Runner Script
# =============================================================================

Write-Host "=============================================================================" -ForegroundColor Cyan
Write-Host "CRATA AI - Growth Intelligence Dashboard (Flask)" -ForegroundColor Cyan
Write-Host "=============================================================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Activate virtual environment if exists
if (Test-Path "venv_flask\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".\venv_flask\Scripts\Activate.ps1"
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv_flask
    & ".\venv_flask\Scripts\Activate.ps1"
    pip install Flask google-analytics-data pandas python-dotenv
}

Write-Host ""
Write-Host "Starting Flask server..." -ForegroundColor Green
Write-Host "Open your browser at: http://127.0.0.1:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host "=============================================================================" -ForegroundColor Cyan
Write-Host ""

python app_flask.py

