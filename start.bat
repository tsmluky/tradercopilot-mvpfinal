@echo off
echo ========================================
echo   TraderCopilot MVP - Startup Script
echo ========================================
echo.

echo [1/3] Starting Backend Server...
start "TraderCopilot Backend" pwsh -NoExit -Command "cd backend; pwsh tools/start_dev.ps1 -Port 8010"

timeout /t 3 /nobreak > nul

echo [2/3] Starting Frontend Dev Server...
start "TraderCopilot Frontend" cmd /k "cd web && npm run dev"

timeout /t 2 /nobreak > nul

echo [3/3] Opening Browser...
timeout /t 5 /nobreak > nul
start http://localhost:5173

echo.
echo ========================================
echo   TraderCopilot is starting!
echo ========================================
echo.
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8010
echo   API Docs: http://localhost:8010/docs
echo.
echo   Press any key to close this window...
pause > nul
