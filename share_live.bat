@echo off
title MSC Digital Twin Live Sharing
cls
echo ========================================================
echo   MSC Digital Twin - Live Public Sharing Tool
echo ========================================================
echo.

REM 1. Start Python Dash app in background window
echo [1/2] Starting Python Dash server (port 8056)...
start "MSC Digital Twin Server" powershell -NoExit -Command "python story_app.py"

echo Waiting for Python Dash server to initialize...
timeout /t 3 /nobreak >nul

echo.
echo [2/2] Launching live public tunnel...
echo --------------------------------------------------------
echo Choose tunnel provider:
echo  [1] Cloudflare Tunnel (Recommended - No password, fast & stable)
echo  [2] Localtunnel (loca.lt)
echo --------------------------------------------------------
set /p choice="Select 1 or 2 (default is 1): "

if "%choice%"=="2" (
    echo.
    echo Starting Localtunnel on port 8056...
    echo (Note: If visitors see a password screen, their password is their IP at https://loca.lt/mytunnelpassword)
    npx -y localtunnel --port 8056
) else (
    echo.
    echo Starting Cloudflare Tunnel on port 8056...
    echo Your live HTTPS URL will appear below momentarily:
    npx -y cloudflared tunnel --url http://127.0.0.1:8056
)

pause
