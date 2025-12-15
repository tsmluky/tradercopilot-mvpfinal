@echo off
echo ===================================================
echo   TRADERCOPILOT - CLEAN DEPLOYMENT PROTOCOL V2
echo ===================================================
echo.
echo Checking Server Connectivity...
:check_connection
curl -I -s https://tradercopilot-mvpfinal-production.up.railway.app/health > NUL
if %errorlevel% neq 0 (
    echo [!] Server not reachable or starting up... Waiting 5s...
    timeout /t 5 > NUL
    goto check_connection
)
echo [OK] Server is UP and READY.
echo.
echo This script will wipe all signal history from the LIVE database.
echo.
set /p confirm="Type 'CLEAN' to confirm factory reset: "

if "%confirm%"=="CLEAN" (
    echo.
    echo Sending Reset Command to Production...
    curl -X POST https://tradercopilot-mvpfinal-production.up.railway.app/system/reset
    echo.
    echo.
    echo ===================================================
    echo   RESET COMPLETE.
    echo   The dashboard is now clean.
    echo   New signals will appear as they are generated.
    echo ===================================================
) else (
    echo.
    echo Cancelled. No changes made.
)
pause
