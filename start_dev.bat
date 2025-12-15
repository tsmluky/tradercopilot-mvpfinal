@echo off
echo ===========================================
echo   TraderCopilot - Local Development Environment
echo ===========================================
echo.
echo Starting Backend (FastAPI) on Port 8000...
echo Starting Frontend (Vite)...
echo.

:: Start Backend (Robust mode via python script)
:: Check paths and run
start "TraderCopilot Backend" cmd /k "if exist .venv\Scripts\activate (call .venv\Scripts\activate) else (echo No .venv found in root, trying global python...) && cd backend && python run_backend.py"

:: Start Frontend
start "TraderCopilot Web" cmd /k "cd web && npm run dev"

echo.
echo Services should be running!
echo Backend:   http://127.0.0.1:8000
echo Frontend:  http://localhost:5173  (Or 4173 if busy)
echo.
echo IMPORTANT: If 5173 is busy, Vite uses 4173. Check the Web Window!
echo.
pause >nul
