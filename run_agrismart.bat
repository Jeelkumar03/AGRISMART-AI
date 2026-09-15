@echo off
setlocal
title AgriSmart AI Launcher
cd /d "%~dp0"

echo ============================================
echo   AgriSmart AI - Launcher
echo ============================================
echo.

if not exist ".venv\Scripts\activate.bat" (
    echo [1/4] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: venv creation failed. Confirm Python is installed and on PATH.
        pause
        exit /b 1
    )
) else (
    echo [1/4] Virtual environment found.
)

echo [2/4] Installing dependencies from requirements.txt...
call .venv\Scripts\activate.bat
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: pip install failed. Check requirements.txt / internet connection.
    pause
    exit /b 1
)

echo [3/4] Starting backend (app\backend\main.py)...
start "AgriSmart Backend" cmd /k ".venv\Scripts\activate.bat && python app\backend\main.py"
timeout /t 6 /nobreak >nul

echo [4/4] Starting frontend server...
start "AgriSmart Frontend" cmd /k "python -m http.server 8000 --directory app\frontend"
timeout /t 3 /nobreak >nul

start http://localhost:8000
echo.
echo AgriSmart AI is running.
echo Close the two server windows to stop it.
pause
