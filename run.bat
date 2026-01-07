@echo off
REM British Days Application Launcher for Windows
REM This script runs the British Days application

echo Starting British Days Application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
pip show Pillow >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install -r requirements.txt
)

REM Run the application
python main.py

pause
