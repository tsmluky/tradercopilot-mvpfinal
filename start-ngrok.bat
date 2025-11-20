@echo off
echo ========================================
echo   TraderCopilot - Ngrok Setup
echo ========================================
echo.
echo [1/2] Starting Frontend Tunnel (port 5173)...
echo.

start "Ngrok Frontend" cmd /k "echo FRONTEND TUNNEL && echo =============== && ngrok http 5173"

timeout /t 5 /nobreak > nul

echo.
echo [2/2] Starting Backend Tunnel (port 8010)...
echo.

start "Ngrok Backend" cmd /k "echo BACKEND TUNNEL && echo =============== && ngrok http 8010"

timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo   INSTRUCTIONS:
echo ========================================
echo.
echo Two new windows opened with Ngrok tunnels.
echo.
echo Look for lines like:
echo   Forwarding: https://XXXXX.ngrok.io
echo.
echo STEP 1: Copy BOTH URLs
echo   - Frontend URL (port 5173)
echo   - Backend URL (port 8010)
echo.
echo STEP 2: Update backend URL
echo   Edit: web/src/services/api.ts
echo   Change: const API_BASE_URL = 'https://YOUR_BACKEND_URL.ngrok.io';
echo.
echo STEP 3: Restart frontend
echo   Ctrl+C in frontend terminal
echo   Run: npm run dev -- --host
echo.
echo STEP 4: Open frontend URL on your phone
echo   https://YOUR_FRONTEND_URL.ngrok.io
echo.
echo ========================================
echo.
pause
