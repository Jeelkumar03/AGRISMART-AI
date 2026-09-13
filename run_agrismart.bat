@echo off
title AgriSmart AI Launcher
cd /d "%~dp0"

echo Starting AgriSmart AI...
echo.

start "AgriSmart Backend" cmd /k ".venv\Scripts\activate.bat && python app\backend\main.py"
timeout /t 6 /nobreak >nul

start "AgriSmart Frontend" cmd /k "python -m http.server 8000 --directory app\frontend"
timeout /t 3 /nobreak >nul

start http://localhost:8000

echo.
echo AgriSmart AI is running.
echo Close the two server windows to stop it.
pause