# ============================================
# TraderCopilot - Análisis Completo de Performance
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Complete Performance Analysis" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Limpiar todo
Write-Host "🧹 Cleaning previous data..." -ForegroundColor Yellow
Remove-Item -Path backend\logs\CUSTOM\*.csv -Force -ErrorAction SilentlyContinue
Remove-Item -Path backend\logs\EVALUATED\*.csv -Force -ErrorAction SilentlyContinue

# Configuración
$strategies = @(
    @{Name = "ma_cross_v1"; Display = "MA Cross 10/50" },
    @{Name = "donchian_breakout_v1"; Display = "Donchian Breakout" },
    @{Name = "bb_mean_reversion_v1"; Display = "BB Mean Reversion" },
    @{Name = "donchian_v2"; Display = "Donchian V2" }
)

$timeframes = @("15m", "30m", "1h", "4h")
$tokens = @("ETH", "BTC", "SOL")

$allResults = @()

foreach ($strat in $strategies) {
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "Testing: $($strat.Display)" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    
    foreach ($tf in $timeframes) {
        Write-Host "  ⏱️  $tf..." -NoNewline
        
        # Generar señales
        $genOutput = .\generate_signals.ps1 -Strategy $strat.Name -Tokens $tokens -Timeframe $tf 2>&1 | Out-String
        
        # Contar señales generadas
        if ($genOutput -match "Total signals generated: (\d+)") {
            $signalsGenerated = [int]$Matches[1]
        }
        else {
            $signalsGenerated = 0
        }
        
        if ($signalsGenerated -eq 0) {
            Write-Host " No signals" -ForegroundColor Gray
            continue
        }
        
        # Evaluar
        .\evaluate_custom_signals.ps1 2>&1 | Out-Null
        
        # Analizar resultados
        $wins = 0
        $losses = 0
        $open = 0
        $totalPnL = 0.0
        
        Get-ChildItem -Path "backend\logs\EVALUATED\*.evaluated.csv" -ErrorAction SilentlyContinue | ForEach-Object {
            $evals = Import-Csv $_.FullName
            foreach ($eval in $evals) {
                switch ($eval.result) {
                    "WIN" { $wins++ }
                    "LOSS" { $losses++ }
                    default { $open++ }
                }
                
                if ($eval.pnl_r -and $eval.pnl_r -ne "") {
                    try {
                        $totalPnL += [decimal]$eval.pnl_r
                    }
                    catch {}
                }
            }
        }
        
        $total = $wins + $losses + $open
        $winRate = if ($total -gt 0) { [math]::Round(($wins / $total) * 100, 1) } else { 0 }
        $avgPnL = if ($total -gt 0) { [math]::Round(($totalPnL / $total) * 100, 2) } else { 0 }
        
        $allResults += [PSCustomObject]@{
            Strategy  = $strat.Display
            Timeframe = $tf
            Total     = $total
            Wins      = $wins
            Losses    = $losses
            Open      = $open
            WinRate   = $winRate
            AvgPnL    = $avgPnL
            TotalPnL  = [math]::Round($totalPnL * 100, 2)
        }
        
        $color = if ($winRate -ge 50) { "Green" } elseif ($winRate -ge 30) { "Yellow" } else { "Red" }
        Write-Host " $total signals | WR: $winRate% | PnL: $avgPnL%" -ForegroundColor $color
        
        # Limpiar para próximo test
        Remove-Item -Path backend\logs\CUSTOM\*.csv -Force -ErrorAction SilentlyContinue
        Remove-Item -Path backend\logs\EVALUATED\*.csv -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  📊 FINAL RESULTS" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

if ($allResults.Count -eq 0) {
    Write-Host "❌ No signals were generated in any configuration" -ForegroundColor Red
    Write-Host "This might mean current market conditions don't match strategy criteria" -ForegroundColor Yellow
    exit 0
}

Write-Host "🏆 TOP 10 by Win Rate:" -ForegroundColor Cyan
$allResults | Sort-Object WinRate -Descending | Select-Object -First 10 | Format-Table -AutoSize

Write-Host ""
Write-Host "💰 TOP 10 by Total PnL:" -ForegroundColor Cyan
$allResults | Sort-Object TotalPnL -Descending | Select-Object -First 10 | Format-Table -AutoSize

Write-Host ""
Write-Host "📈 Best Configuration:" -ForegroundColor Yellow
$best = $allResults | Sort-Object WinRate -Descending | Select-Object -First 1
Write-Host "  Strategy: $($best.Strategy)" -ForegroundColor Green
Write-Host "  Timeframe: $($best.Timeframe)" -ForegroundColor Green
Write-Host "  Win Rate: $($best.WinRate)%" -ForegroundColor Green
Write-Host "  Avg PnL: $($best.AvgPnL)%" -ForegroundColor Green
Write-Host "  Total Signals: $($best.Total)" -ForegroundColor Green

# Guardar
$allResults | Export-Csv -Path "performance_analysis.csv" -NoTypeInformation -Encoding UTF8
Write-Host ""
Write-Host "💾 Results saved to: performance_analysis.csv" -ForegroundColor Gray
