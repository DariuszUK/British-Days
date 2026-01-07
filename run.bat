@echo off
REM British Days Application Launcher for Windows
REM This script ensures all dependencies are met before running the application

echo ========================================
echo British Days - Slang Collector
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check if assets directory exists
if not exist "assets" (
    echo [SETUP] Assets directory not found. Generating PNG assets...
    python generate_assets.py
    if %errorlevel% neq 0 (
        echo ERROR: Failed to generate assets
        echo Please ensure Pillow is installed: pip install Pillow
        pause
        exit /b 1
    )
    echo [OK] Assets generated successfully
    echo.
)

REM Check if Pillow is installed
python -c "import PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo [SETUP] Installing required packages...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
    echo.
)

REM Create Data directory if it doesn't exist
if not exist "Data" (
    mkdir Data
    echo [OK] Created Data directory
    echo.
)

REM Run the application
echo Starting British Days application...
echo.
python main.py

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo Application exited with an error
    echo ========================================
    echo.
    echo If you continue to have issues, try:
    echo 1. Run: python generate_assets.py
    echo 2. Run: pip install -r requirements.txt
    echo 3. Check the error message above
    echo.
)

pause

