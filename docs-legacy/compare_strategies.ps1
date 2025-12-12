# ============================================
# TraderCopilot - Comparar Todas las Estrategias
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Strategy Comparison Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$strategies = @("donchian_v2", "ma_cross_v1", "donchian_breakout_v1", "bb_mean_reversion_v1")
$tokens = @("ETH", "BTC", "SOL")
$timeframe = "1h"

Write-Host "Testing all strategies on $timeframe timeframe" -ForegroundColor Yellow
Write-Host "Tokens: $($tokens -join ', ')" -ForegroundColor Yellow
Write-Host ""

foreach ($strategy in $strategies) {
    Write-Host "Testing: $strategy" -ForegroundColor Cyan
    Write-Host "----------------------------------------" -ForegroundColor Gray
    
    .\generate_signals.ps1 -Strategy $strategy -Tokens $tokens -Timeframe $timeframe
    
    Write-Host ""
}

Write-Host ""
Write-Host "✅ Strategy comparison completed!" -ForegroundColor Green
Write-Host "View results with: .\view_signals.ps1 -Last 30" -ForegroundColor Cyan
