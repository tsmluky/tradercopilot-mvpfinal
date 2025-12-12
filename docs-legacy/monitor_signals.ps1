# ============================================
# TraderCopilot - Monitor de Señales en Tiempo Real
# ============================================

param(
    [int]$RefreshSeconds = 5,
    [string]$Mode = "LITE"  # LITE, PRO, EVALUATED
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TraderCopilot - Signal Monitor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Mode: $Mode" -ForegroundColor Yellow
Write-Host "Refresh: Every $RefreshSeconds seconds" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

$LogsPath = "backend\logs\$Mode"

while ($true) {
    Clear-Host
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  TraderCopilot - Signal Monitor" -ForegroundColor Cyan
    Write-Host "  Mode: $Mode | $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    if (Test-Path $LogsPath) {
        $csvFiles = Get-ChildItem -Path $LogsPath -Filter "*.csv"
        
        if ($csvFiles.Count -eq 0) {
            Write-Host "No signals found yet..." -ForegroundColor Yellow
        } else {
            foreach ($file in $csvFiles) {
                $token = $file.BaseName.ToUpper()
                $signals = Import-Csv $file.FullName
                
                Write-Host "[$token] - $($signals.Count) signals" -ForegroundColor Green
                
                # Mostrar últimas 3 señales
                $signals | Select-Object -Last 3 | ForEach-Object {
                    $color = if ($_.direction -eq "long") { "Green" } else { "Red" }
                    Write-Host "  $($_.timestamp) | " -NoNewline
                    Write-Host "$($_.direction.ToUpper())" -ForegroundColor $color -NoNewline
                    Write-Host " @ $($_.entry) | TP: $($_.tp) | SL: $($_.sl) | Conf: $($_.confidence)"
                    Write-Host "  Rationale: $($_.rationale)" -ForegroundColor Gray
                    Write-Host ""
                }
            }
        }
    } else {
        Write-Host "Logs directory not found: $LogsPath" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "Next refresh in $RefreshSeconds seconds..." -ForegroundColor Gray
    Start-Sleep -Seconds $RefreshSeconds
}
