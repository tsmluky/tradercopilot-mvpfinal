
$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting TraderCopilot Scheduler (Auto-Restart Mode)..." -ForegroundColor Cyan

$scriptPath = Join-Path $PSScriptRoot "backend\scheduler.py"

while ($true) {
    try {
        Write-Host "Using python: $(Get-Command python | Select-Object -ExpandProperty Source)" -ForegroundColor Gray
        python $scriptPath 30
    }
    catch {
        Write-Host "❌ Scheduler crashed with error: $_" -ForegroundColor Red
    }

    Write-Host "🔄 Restarting in 5 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
}
