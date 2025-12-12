# ============================================
# Test Manual de Todas las Estrategias
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Manual Strategy Testing" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Limpiar
Remove-Item -Path backend\logs\CUSTOM\*.csv -Force -ErrorAction SilentlyContinue
Remove-Item -Path backend\logs\EVALUATED\*.csv -Force -ErrorAction SilentlyContinue

$tests = @(
    @{Strategy = "donchian_v2"; TF = "4h"; Name = "Donchian V2" },
    @{Strategy = "bb_mean_reversion_v1"; TF = "15m"; Name = "BB Mean Rev 15m" },
    @{Strategy = "bb_mean_reversion_v1"; TF = "1h"; Name = "BB Mean Rev 1h" },
    @{Strategy = "rsi_divergence_v1"; TF = "1h"; Name = "RSI Div 1h" },
    @{Strategy = "rsi_divergence_v1"; TF = "4h"; Name = "RSI Div 4h" },
    @{Strategy = "supertrend_flow_v1"; TF = "4h"; Name = "SuperTrend 4h" },
    @{Strategy = "supertrend_flow_v1"; TF = "1d"; Name = "SuperTrend 1d" },
    @{Strategy = "vwap_intraday_v1"; TF = "15m"; Name = "VWAP 15m" },
    @{Strategy = "vwap_intraday_v1"; TF = "30m"; Name = "VWAP 30m" }
)

foreach ($test in $tests) {
    Write-Host "Testing: $($test.Name)" -ForegroundColor Cyan -NoNewline
    
    # Generar
    .\generate_signals.ps1 -Strategy $test.Strategy -Timeframe $test.TF 2>&1 | Out-Null
    
    # Contar señales
    $signalCount = 0
    Get-ChildItem -Path "backend\logs\CUSTOM\*.csv" -ErrorAction SilentlyContinue | ForEach-Object {
        $signals = Import-Csv $_.FullName
        $signalCount += $signals.Count
    }
    
    if ($signalCount -gt 0) {
        Write-Host " - $signalCount signals" -ForegroundColor Green
        
        # Evaluar
        .\evaluate_custom_signals.ps1 2>&1 | Out-Null
        
        # Ver resultados
        .\view_performance.ps1 -Last $signalCount 2>&1 | Out-Null
    }
    else {
        Write-Host " - No signals" -ForegroundColor Gray
    }
    
    # Limpiar para próximo test
    Remove-Item -Path backend\logs\CUSTOM\*.csv -Force -ErrorAction SilentlyContinue
    Remove-Item -Path backend\logs\EVALUATED\*.csv -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "✅ All tests complete!" -ForegroundColor Green
