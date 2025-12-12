# ============================================
# TraderCopilot - Optimización de Timeframes
# ============================================
# Prueba todas las estrategias en múltiples timeframes y compara resultados

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Timeframe Optimization Analysis" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$strategies = @("donchian_v2", "ma_cross_v1", "donchian_breakout_v1", "bb_mean_reversion_v1")
$timeframes = @("15m", "30m", "1h", "4h")
$tokens = @("ETH", "BTC", "SOL")

# Limpiar logs anteriores
Write-Host "🧹 Cleaning previous test data..." -ForegroundColor Yellow
Remove-Item -Path backend\logs\CUSTOM\*.csv -Force -ErrorAction SilentlyContinue
Remove-Item -Path backend\logs\EVALUATED\*.csv -Force -ErrorAction SilentlyContinue

Write-Host "✅ Clean slate ready`n" -ForegroundColor Green

$results = @()

foreach ($strategy in $strategies) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "Testing Strategy: $strategy" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""
    
    foreach ($tf in $timeframes) {
        Write-Host "  📊 Timeframe: $tf" -ForegroundColor Yellow
        
        # Generar señales
        .\generate_signals.ps1 -Strategy $strategy -Tokens $tokens -Timeframe $tf | Out-Null
        
        # Evaluar señales
        $evalOutput = .\evaluate_custom_signals.ps1 2>&1 | Out-String
        
        # Extraer número de señales evaluadas
        if ($evalOutput -match "Total: (\d+) signals evaluated") {
            $signalsCount = [int]$Matches[1]
        }
        else {
            $signalsCount = 0
        }
        
        # Calcular win rate
        if ($signalsCount -gt 0) {
            # Leer evaluaciones
            $allWins = 0
            $allLosses = 0
            $allOpen = 0
            $totalPnL = 0.0
            
            Get-ChildItem -Path "backend\logs\EVALUATED\*.evaluated.csv" -ErrorAction SilentlyContinue | ForEach-Object {
                $evals = Import-Csv $_.FullName
                foreach ($eval in $evals) {
                    if ($eval.result -eq "WIN") { $allWins++ }
                    elseif ($eval.result -eq "LOSS") { $allLosses++ }
                    else { $allOpen++ }
                    
                    if ($eval.pnl_r) {
                        $totalPnL += [decimal]$eval.pnl_r
                    }
                }
            }
            
            $total = $allWins + $allLosses + $allOpen
            $winRate = if ($total -gt 0) { [math]::Round(($allWins / $total) * 100, 2) } else { 0 }
            $avgPnL = if ($total -gt 0) { [math]::Round($totalPnL / $total, 2) } else { 0 }
            
            $results += [PSCustomObject]@{
                Strategy  = $strategy
                Timeframe = $tf
                Signals   = $total
                Wins      = $allWins
                Losses    = $allLosses
                Open      = $allOpen
                WinRate   = $winRate
                AvgPnL    = $avgPnL
                TotalPnL  = [math]::Round($totalPnL, 2)
            }
            
            $color = if ($winRate -ge 50) { "Green" } else { if ($winRate -ge 30) { "Yellow" } else { "Red" } }
            Write-Host "    Signals: $total | Wins: $allWins | Losses: $allLosses | WR: $winRate%" -ForegroundColor $color
        }
        else {
            Write-Host "    No signals generated" -ForegroundColor Gray
        }
        
        # Limpiar para próximo test
        Remove-Item -Path backend\logs\CUSTOM\*.csv -Force -ErrorAction SilentlyContinue
        Remove-Item -Path backend\logs\EVALUATED\*.csv -Force -ErrorAction SilentlyContinue
        
        Write-Host ""
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  📊 OPTIMIZATION RESULTS" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Ordenar por win rate
$sortedResults = $results | Sort-Object WinRate -Descending

Write-Host "🏆 TOP 10 BEST PERFORMERS (by Win Rate):" -ForegroundColor Cyan
Write-Host ""

$sortedResults | Select-Object -First 10 | Format-Table `
@{Label = "Strategy"; Expression = { $_.Strategy }; Width = 25 }, `
@{Label = "TF"; Expression = { $_.Timeframe }; Width = 6 }, `
@{Label = "Signals"; Expression = { $_.Signals }; Width = 8 }, `
@{Label = "Wins"; Expression = { $_.Wins }; Width = 6 }, `
@{Label = "Losses"; Expression = { $_.Losses }; Width = 7 }, `
@{Label = "WR%"; Expression = { $_.WinRate }; Width = 7 }, `
@{Label = "Avg PnL"; Expression = { $_.AvgPnL }; Width = 9 }, `
@{Label = "Total PnL"; Expression = { $_.TotalPnL }; Width = 10 } `
    -AutoSize

Write-Host ""
Write-Host "📈 TOP 10 BEST PERFORMERS (by Total PnL):" -ForegroundColor Cyan
Write-Host ""

$results | Sort-Object TotalPnL -Descending | Select-Object -First 10 | Format-Table `
@{Label = "Strategy"; Expression = { $_.Strategy }; Width = 25 }, `
@{Label = "TF"; Expression = { $_.Timeframe }; Width = 6 }, `
@{Label = "Signals"; Expression = { $_.Signals }; Width = 8 }, `
@{Label = "WR%"; Expression = { $_.WinRate }; Width = 7 }, `
@{Label = "Total PnL"; Expression = { $_.TotalPnL }; Width = 10 } `
    -AutoSize

Write-Host ""
Write-Host "💡 Recommendations:" -ForegroundColor Yellow

$bestConfig = $sortedResults | Select-Object -First 1
if ($bestConfig) {
    Write-Host "  Best Strategy: $($bestConfig.Strategy)" -ForegroundColor Green
    Write-Host "  Best Timeframe: $($bestConfig.Timeframe)" -ForegroundColor Green
    Write-Host "  Win Rate: $($bestConfig.WinRate)%" -ForegroundColor Green
    Write-Host "  Total PnL: $($bestConfig.TotalPnL)R" -ForegroundColor Green
}

Write-Host ""
Write-Host "📁 Full results saved to: optimization_results.csv" -ForegroundColor Gray

# Guardar resultados completos
$results | Export-Csv -Path "optimization_results.csv" -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "✅ Optimization complete!" -ForegroundColor Green
