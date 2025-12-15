
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "   TraderCopilot - Cleanup & Restart" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

# 1. Kill Processes
Write-Host "1. Killing old processes..." -ForegroundColor Yellow
Stop-Process -Name "python" -ErrorAction SilentlyContinue -Force
Stop-Process -Name "node" -ErrorAction SilentlyContinue -Force
Stop-Process -Name "uvicorn" -ErrorAction SilentlyContinue -Force

Start-Sleep -Seconds 2

# 2. Check Port 8000
$port = 8000
$tcp = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($tcp) {
    Write-Host "⚠️ Port $port is still in use by PID $($tcp.OwningProcess). Killing it..." -ForegroundColor Red
    Stop-Process -Id $tcp.OwningProcess -Force
}
else {
    Write-Host "✅ Port $port is free." -ForegroundColor Green
}

# 3. Start Backend
Write-Host "2. Starting Backend..." -ForegroundColor Green
Start-Process "cmd" -ArgumentList "/k cd backend && python run_backend.py" -WindowStyle Normal

# 4. Start Frontend
Write-Host "3. Starting Frontend..." -ForegroundColor Green
Start-Process "cmd" -ArgumentList "/k cd web && npm run dev" -WindowStyle Normal

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "   DONE! Check the new windows." -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
