@echo off
echo ========================================
echo   TraderCopilot - Mobile Access Setup
echo ========================================
echo.

echo [INFO] Checking your local IP...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    goto :found
)
:found
echo Your local IP: %IP%
echo.

echo ========================================
echo   Option 1: Same WiFi Access
echo ========================================
echo.
echo 1. Make sure your phone is on the SAME WiFi
echo 2. Open on your phone: http://%IP%:5173
echo.
echo If it doesn't work, check Windows Firewall.
echo.

echo ========================================
echo   Option 2: Internet Access (Ngrok)
echo ========================================
echo.
echo Starting Ngrok tunnel...
echo.

start "Ngrok Frontend" cmd /k "ngrok http 5173"
timeout /t 3 /nobreak > nul

start "Ngrok Backend" cmd /k "ngrok http 8010"
timeout /t 2 /nobreak > nul

echo.
echo ========================================
echo   Ngrok URLs will appear in new windows
echo ========================================
echo.
echo Look for lines like:
echo   Forwarding: https://abc123.ngrok.io
echo.
echo 1. Copy the FRONTEND url (port 5173)
echo 2. Open it on your phone
echo 3. Works from ANYWHERE (any WiFi, 4G, etc)
echo.
echo NOTE: You'll need to update the backend URL
echo in web/src/services/api.ts with the backend
echo ngrok URL (port 8010)
echo.
echo Press any key to close this window...
pause > nul
