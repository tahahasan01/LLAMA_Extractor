# Movie Recommendation Chatbot - Setup and Run Script
# This script will set up and start your movie recommendation chatbot

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Movie Recommendation Chatbot Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "Step 1: Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Step 2: Create virtual environment if it doesn't exist
Write-Host ""
Write-Host "Step 2: Setting up virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

# Step 3: Activate virtual environment and install dependencies
Write-Host ""
Write-Host "Step 3: Installing dependencies..." -ForegroundColor Yellow
Write-Host "Activating virtual environment..." -ForegroundColor Cyan

& ".\venv\Scripts\Activate.ps1"

Write-Host "Installing required packages..." -ForegroundColor Cyan
pip install --upgrade pip -q
pip install -r requirements.txt

Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Step 4: Check for .env file
Write-Host ""
Write-Host "Step 4: Checking configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "⚠️ .env file not found!" -ForegroundColor Red
    Write-Host "Please edit the .env file and add your TMDb API key" -ForegroundColor Yellow
    Write-Host "Get your API key from: https://www.themoviedb.org/settings/api" -ForegroundColor Cyan
} else {
    Write-Host "✅ .env file found" -ForegroundColor Green
}

# Step 5: Check ODBC Driver
Write-Host ""
Write-Host "Step 5: Checking ODBC Driver for SQL Server..." -ForegroundColor Yellow
$drivers = Get-OdbcDriver | Where-Object {$_.Name -like "*SQL Server*"}
if ($drivers) {
    Write-Host "✅ ODBC Driver found:" -ForegroundColor Green
    $drivers | ForEach-Object { Write-Host "   - $($_.Name)" -ForegroundColor Cyan }
} else {
    Write-Host "⚠️ ODBC Driver not found!" -ForegroundColor Red
    Write-Host "Please download and install from: https://aka.ms/downloadmsodbcsql" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installing the driver, run this script again." -ForegroundColor Yellow
    
    $download = Read-Host "Would you like to open the download page now? (y/n)"
    if ($download -eq 'y') {
        Start-Process "https://aka.ms/downloadmsodbcsql"
    }
    exit 1
}

# Step 6: Instructions for SQL Server
Write-Host ""
Write-Host "Step 6: SQL Server Database Setup" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Please complete these steps in SQL Server Management Studio (SSMS):" -ForegroundColor White
Write-Host ""
Write-Host "1. Open SQL Server Management Studio" -ForegroundColor Cyan
Write-Host "2. Connect to your SQL Server instance" -ForegroundColor Cyan
Write-Host "3. Open the file: setup_database.sql" -ForegroundColor Cyan
Write-Host "4. Execute the script (Press F5)" -ForegroundColor Cyan
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$sqlDone = Read-Host "Have you created the database in SSMS? (y/n)"

if ($sqlDone -ne 'y') {
    Write-Host ""
    Write-Host "Please create the database first, then run this script again." -ForegroundColor Yellow
    Write-Host "You can also create it manually with this command:" -ForegroundColor Cyan
    Write-Host "  CREATE DATABASE MovieChatbot;" -ForegroundColor White
    exit 0
}

# Step 7: Test database connection
Write-Host ""
Write-Host "Step 7: Testing database connection..." -ForegroundColor Yellow
try {
    python -c "from database.sqlserver_db import get_sqlserver_db; db = get_sqlserver_db(); print('✅ Database connection successful!')"
    Write-Host "✅ Connected to SQL Server successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Database connection failed!" -ForegroundColor Red
    Write-Host "Please check your SQL Server settings in the .env file" -ForegroundColor Yellow
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

# Step 8: Check TMDb API Key
Write-Host ""
Write-Host "Step 8: Checking TMDb API Key..." -ForegroundColor Yellow
$envContent = Get-Content .env
$apiKey = ($envContent | Select-String "TMDB_API_KEY=(.+)" | ForEach-Object { $_.Matches.Groups[1].Value })

if ($apiKey -eq "your_tmdb_api_key_here" -or [string]::IsNullOrWhiteSpace($apiKey)) {
    Write-Host "⚠️ TMDb API key not configured!" -ForegroundColor Red
    Write-Host ""
    Write-Host "To get your FREE API key:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://www.themoviedb.org/signup" -ForegroundColor Cyan
    Write-Host "2. Create a free account" -ForegroundColor Cyan
    Write-Host "3. Go to Settings > API" -ForegroundColor Cyan
    Write-Host "4. Request an API key (choose 'Developer' option)" -ForegroundColor Cyan
    Write-Host "5. Copy your API key" -ForegroundColor Cyan
    Write-Host "6. Edit the .env file and replace 'your_tmdb_api_key_here' with your actual key" -ForegroundColor Cyan
    Write-Host ""
    
    $openTmdb = Read-Host "Would you like to open TMDb signup page now? (y/n)"
    if ($openTmdb -eq 'y') {
        Start-Process "https://www.themoviedb.org/signup"
    }
    
    Write-Host ""
    Write-Host "After adding your API key to .env, run this script again." -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "✅ TMDb API key configured" -ForegroundColor Green
}

# Step 9: Start the application
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🎬 Starting Movie Recommendation Chatbot" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will start on: http://localhost:5000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run the Flask application
python app.py
