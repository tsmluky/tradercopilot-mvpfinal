@echo off
echo ===================================================
echo   TRADERCOPILOT - CLEAN DEPLOYMENT PROTOCOL
echo ===================================================
echo.
echo This script will wipe all signal history from the LIVE database.
echo Use this only when you want to present a pristine "Day 1" product.
echo.
set /p confirm="Type 'CLEAN' to confirm factory reset: "

if "%confirm%"=="CLEAN" (
    echo.
    echo Sending Reset Command to Production...
    curl -X POST https://tradercopilot-mvpfinal.up.railway.app/system/reset
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
