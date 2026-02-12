# Salon MS Setup - Step by Step
# Run this script from the project root directory

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SALON MS - PROJECT SETUP" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. Check Python
Write-Host "[1/6] Checking Python..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "ERROR: Python not found. Install Python 3.8+ from python.org" -ForegroundColor Red
    exit 1
}
$pyVersion = python --version 2>&1
Write-Host "    Found: $pyVersion" -ForegroundColor Green

# 2. Create venv
Write-Host "`n[2/6] Setting up virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "    Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "    Created venv/" -ForegroundColor Green
}

# 3. Install packages
Write-Host "`n[3/6] Installing Python packages..." -ForegroundColor Yellow
Write-Host "    This may take a few minutes..." -ForegroundColor Gray
& "venv\Scripts\pip.exe" install --upgrade pip --quiet
& "venv\Scripts\pip.exe" install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Package installation failed" -ForegroundColor Red
    exit 1
}
Write-Host "    Django, MySQL client, and REST framework installed" -ForegroundColor Green

# 4. Setup .env
Write-Host "`n[4/6] Configuring environment..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "    .env already exists" -ForegroundColor Green
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "    Created .env file" -ForegroundColor Green
    Write-Host "    ACTION REQUIRED: Edit .env with your MySQL password!" -ForegroundColor Magenta
}

# 5. Database check
Write-Host "`n[5/6] Database setup..." -ForegroundColor Yellow
$envContent = Get-Content ".env" -Raw
if ($envContent -match "DB_PASSWORD=your_password_here" -or $envContent -match "DB_PASSWORD=`$") {
    Write-Host "    WARNING: Database password not configured in .env" -ForegroundColor Red
    Write-Host "    Open .env and set DB_PASSWORD before running migrations" -ForegroundColor Yellow
} else {
    Write-Host "    Database credentials configured" -ForegroundColor Green
}

# 6. Next steps
Write-Host "`n[6/6] Setup complete!" -ForegroundColor Green
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  NEXT STEPS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "1. Edit .env with your MySQL credentials:" -ForegroundColor White
Write-Host "   notepad .env`n" -ForegroundColor Gray

Write-Host "2. Create MySQL database:" -ForegroundColor White
Write-Host "   mysql -u root -p" -ForegroundColor Gray
Write-Host "   CREATE DATABASE salon_db;`n" -ForegroundColor Gray

Write-Host "3. Activate virtual environment:" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1`n" -ForegroundColor Gray

Write-Host "4. Run Django migrations:" -ForegroundColor White
Write-Host "   python manage.py makemigrations" -ForegroundColor Gray
Write-Host "   python manage.py migrate`n" -ForegroundColor Gray

Write-Host "5. Create admin user:" -ForegroundColor White
Write-Host "   python manage.py createsuperuser`n" -ForegroundColor Gray

Write-Host "6. Start the server:" -ForegroundColor White
Write-Host "   python manage.py runserver`n" -ForegroundColor Gray

Write-Host "========================================`n" -ForegroundColor Cyan

# Ask if they want to activate venv now
$activate = Read-Host "Activate virtual environment now? (y/n)"
if ($activate -eq "y" -or $activate -eq "Y") {
    Write-Host "`nActivating venv... Run 'deactivate' to exit venv`n" -ForegroundColor Green
    & "venv\Scripts\Activate.ps1"
}
