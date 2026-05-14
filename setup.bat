@echo off
cd /d "%~dp0"
title Eagle Mail Agent - Setup

echo ========================================
echo  Eagle Mail Agent - Setup
echo ========================================
echo.

echo [1/3] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment.
    echo Make sure Python 3 is installed and added to PATH.
    pause
    exit /b 1
)

echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Setup complete.
echo  Run run.bat to start the agent.
echo ========================================
pause
