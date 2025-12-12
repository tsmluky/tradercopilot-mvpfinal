# ============================================
# TraderCopilot - Test Donchian en Múltiples Timeframes
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Donchian V2 - Multi-Timeframe Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$timeframes = @("15m", "1h", "4h")
$tokens = @("ETH", "BTC", "SOL")

foreach ($tf in $timeframes) {
    Write-Host "Testing Timeframe: $tf" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Gray
    
    .\generate_signals.ps1 -Strategy "donchian_v2" -Tokens $tokens -Timeframe $tf
    
    Write-Host ""
}

Write-Host ""
Write-Host "✅ Multi-timeframe test completed!" -ForegroundColor Green
Write-Host "View results with: .\view_signals.ps1 -Last 20" -ForegroundColor Cyan
