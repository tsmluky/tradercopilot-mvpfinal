# ============================================
# TraderCopilot - Restart Scheduler
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Restarting TraderCopilot Scheduler" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que no haya scheduler corriendo
Write-Host "Checking for running scheduler..." -ForegroundColor Yellow
$schedulerProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*scheduler.py*" }

if ($schedulerProcess) {
    Write-Host "⚠️  Found running scheduler (PID: $($schedulerProcess.Id))" -ForegroundColor Yellow
    Write-Host "Stopping it..." -ForegroundColor Yellow
    Stop-Process -Id $schedulerProcess.Id -Force
    Start-Sleep -Seconds 2
    Write-Host "✅ Stopped" -ForegroundColor Green
}
else {
    Write-Host "✅ No scheduler running" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting scheduler with optimized strategies..." -ForegroundColor Cyan
Write-Host ""

# Iniciar scheduler en background
Start-Process -FilePath "python" -ArgumentList "backend/scheduler.py" -WorkingDirectory "." -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "✅ Scheduler started!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Active Strategies:" -ForegroundColor Cyan
Write-Host "  - Donchian Breakout V2 (4h)" -ForegroundColor White
Write-Host "  - BB Mean Reversion (1h, 15m)" -ForegroundColor White
Write-Host ""
Write-Host "💡 Monitor signals with: .\monitor_signals.ps1" -ForegroundColor Gray
Write-Host "💡 View performance with: .\view_performance.ps1" -ForegroundColor Gray
