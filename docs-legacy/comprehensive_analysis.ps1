# ============================================
# TraderCopilot - Comprehensive Strategy Analysis
# ============================================
# Prueba TODAS las estrategias en múltiples timeframes y muestra análisis detallado

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  COMPREHENSIVE STRATEGY ANALYSIS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Testing ALL strategies with 300 candles of historical data" -ForegroundColor Yellow
Write-Host ""

# Limpiar datos previos
Write-Host "🧹 Cleaning previous test data..." -ForegroundColor Yellow
Remove-Item -Path backend\logs\CUSTOM\*.csv -Force -ErrorAction SilentlyContinue
Remove-Item -Path backend\logs\EVALUATED\*.csv -Force -ErrorAction SilentlyContinue

$strategies = @(
    @{Name = "donchian_v2"; Display = "Donchian Breakout V2"; Timeframes = @("4h") },
    @{Name = "bb_mean_reversion_v1"; Display = "BB Mean Reversion"; Timeframes = @("15m", "1h") },
    @{Name = "rsi_divergence_v1"; Display = "RSI Divergence"; Timeframes = @("1h", "4h") },
    @{Name = "supertrend_flow_v1"; Display = "SuperTrend Flow"; Timeframes = @("4h", "1d") },
    @{Name = "vwap_intraday_v1"; Display = "VWAP Intraday"; Timeframes = @("15m", "30m") }
)

$tokens = @("ETH", "BTC", "SOL")
$allResults = @()

$strategyIndex = 1
$totalStrategies = ($strategies | ForEach-Object { $_.Timeframes.Count }) | Measure-Object -Sum | Select-Object -ExpandProperty Sum

foreach ($strat in $strategies) {
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "Strategy: $($strat.Display)" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    
    foreach ($tf in $strat.Timeframes) {
        Write-Host "  ⏱️  Testing $tf..." -NoNewline
        Write-Host " [$strategyIndex/$totalStrategies]" -ForegroundColor Gray
        $strategyIndex++
        
        # Generar señales
        $genOutput = .\generate_signals.ps1 -Strategy $strat.Name -Tokens $tokens -Timeframe $tf 2>&1 | Out-String
        
        if ($genOutput -match "Total signals generated: (\d+)") {
            $signalsGenerated = [int]$Matches[1]
        }
        else {
            $signalsGenerated = 0
        }
        
        if ($signalsGenerated -eq 0) {
            Write-Host "    ❌ No signals generated" -ForegroundColor Gray
            continue
        }
        
        Write-Host "    ✓ Generated $signalsGenerated signals" -ForegroundColor Green
        
        # Evaluar con datos reales
        Write-Host "    🔍 Evaluating..." -NoNewline
        .\evaluate_custom_signals.ps1 2>&1 | Out-Null
        
        # Analizar resultados
        $wins = 0
        $losses = 0
        $open = 0
        $totalPnL = 0.0
        $signalDetails = @()
        
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
                        $pnl = [decimal]$eval.pnl_r
                        $totalPnL += $pnl
                        $signalDetails += [PSCustomObject]@{
                            Token     = $_.BaseName.Replace(".evaluated", "").ToUpper()
                            Time      = $eval.signal_ts
                            Direction = $eval.direction
                            Entry     = [decimal]$eval.entry
                            Exit      = [decimal]$eval.price_at_eval
                            Result    = $eval.result
                            PnL       = $pnl
                        }
                    }
                    catch {}
                }
            }
        }
        
        $total = $wins + $losses + $open
        $winRate = if ($total -gt 0) { [math]::Round(($wins / $total) * 100, 1) } else { 0 }
        $avgPnL = if ($total -gt 0) { [math]::Round(($totalPnL / $total) * 100, 2) } else { 0 }
        $totalPnLPct = [math]::Round($totalPnL * 100, 2)
        
        # Calcular R expectancy (expected R per trade)
        $rExpectancy = if ($total -gt 0) { [math]::Round($totalPnL / $total, 2) } else { 0 }
        
        # Calcular profit factor
        $grossProfit = ($signalDetails | Where-Object { $_.Result -eq "WIN" } | Measure-Object -Property PnL -Sum).Sum
        $grossLoss = [Math]::Abs(($signalDetails | Where-Object { $_.Result -eq "LOSS" } | Measure-Object -Property PnL -Sum).Sum)
        $profitFactor = if ($grossLoss -gt 0) { [math]::Round($grossProfit / $grossLoss, 2) } else { 0 }
        
        # Grade basado en múltiples métricas
        $grade = "F"
        if ($winRate -ge 55 -and $rExpectancy -gt 0.5) { $grade = "A+" }
        elseif ($winRate -ge 50 -and $rExpectancy -gt 0.3) { $grade = "A" }
        elseif ($winRate -ge 45 -and $rExpectancy -gt 0.2) { $grade = "B" }
        elseif ($winRate -ge 40 -and $rExpectancy -gt 0) { $grade = "C" }
        elseif ($winRate -ge 35) { $grade = "D" }
        
        $color = switch ($grade) {
            "A+" { "Green" }
            "A" { "Green" }
            "B" { "Yellow" }
            "C" { "Yellow" }
            default { "Red" }
        }
        
        Write-Host " Done!" -ForegroundColor Green
        Write-Host "    📊 Results: $total signals | WR: $winRate% | Avg: $avgPnL% | Total: $totalPnLPct% | Grade: " -NoNewline
        Write-Host "$grade" -ForegroundColor $color
        
        $allResults += [PSCustomObject]@{
            Strategy     = $strat.Display
            Timeframe    = $tf
            Total        = $total
            Wins         = $wins
            Losses       = $losses
            Open         = $open
            WinRate      = $winRate
            AvgPnL       = $avgPnL
            TotalPnL     = $totalPnLPct
            RExpectancy  = $rExpectancy
            ProfitFactor = $profitFactor
            Grade        = $grade
        }
        
        # Limpiar para próximo test
        Remove-Item -Path backend\logs\CUSTOM\*.csv -Force -ErrorAction SilentlyContinue
        Remove-Item -Path backend\logs\EVALUATED\*.csv -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  📊 COMPREHENSIVE RESULTS" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

if ($allResults.Count -eq 0) {
    Write-Host "❌ No results generated" -ForegroundColor Red
    exit 0
}

# Ordenar por Grade y WinRate
$sorted = $allResults | Sort-Object @{Expression = {
        switch ($_.Grade) {
            "A+" { 1 }
            "A" { 2 }
            "B" { 3 }
            "C" { 4 }
            "D" { 5 }
            default { 6 }
        }
    }
}, WinRate -Descending

Write-Host "🏆 RANKING BY PERFORMANCE:" -ForegroundColor Cyan
Write-Host ""

$sorted | Format-Table `
@{Label = "Rank"; Expression = { $sorted.IndexOf($_) + 1 }; Width = 4 }, `
@{Label = "Strategy"; Expression = { $_.Strategy }; Width = 25 }, `
@{Label = "TF"; Expression = { $_.Timeframe }; Width = 4 }, `
@{Label = "Signals"; Expression = { $_.Total }; Width = 7 }, `
@{Label = "W/L/O"; Expression = { "$($_.Wins)/$($_.Losses)/$($_.Open)" }; Width = 8 }, `
@{Label = "WR%"; Expression = { $_.WinRate }; Width = 5 }, `
@{Label = "Avg%"; Expression = { $_.AvgPnL }; Width = 7 }, `
@{Label = "Total%"; Expression = { $_.TotalPnL }; Width = 8 }, `
@{Label = "R-Exp"; Expression = { $_.RExpectancy }; Width = 6 }, `
@{Label = "PF"; Expression = { $_.ProfitFactor }; Width = 5 }, `
@{Label = "Grade"; Expression = { $_.Grade }; Width = 5 } `
    -AutoSize

Write-Host ""
Write-Host "📈 STATISTICS:" -ForegroundColor Cyan

$totalSignals = ($allResults | Measure-Object -Property Total -Sum).Sum
$avgWinRate = ($allResults | Measure-Object -Property WinRate -Average).Average
$gradeA = ($allResults | Where-Object { $_.Grade -match "^A" }).Count
$gradeB = ($allResults | Where-Object { $_.Grade -eq "B" }).Count
$profitable = ($allResults | Where-Object { $_.TotalPnL -gt 0 }).Count

Write-Host "  Total Strategies Tested: $($allResults.Count)" -ForegroundColor White
Write-Host "  Total Signals Evaluated: $totalSignals" -ForegroundColor White
Write-Host "  Average Win Rate: $([math]::Round($avgWinRate, 1))%" -ForegroundColor White
Write-Host "  A-Grade Strategies: $gradeA" -ForegroundColor Green
Write-Host "  B-Grade Strategies: $gradeB" -ForegroundColor Yellow
Write-Host "  Profitable Strategies: $profitable / $($allResults.Count)" -ForegroundColor $(if ($profitable -gt ($allResults.Count / 2)) { "Green" } else { "Red" })

Write-Host ""
Write-Host "🎯 RECOMMENDATIONS:" -ForegroundColor Yellow

$topStrategies = $sorted | Where-Object { $_.Grade -match "^A" -or ($_.Grade -eq "B" -and $_.WinRate -ge 45) }

if ($topStrategies.Count -gt 0) {
    Write-Host "  ✅ DEPLOY THESE STRATEGIES TO PRODUCTION:" -ForegroundColor Green
    foreach ($s in $topStrategies) {
        Write-Host "     - $($s.Strategy) ($($s.Timeframe)): $($s.WinRate)% WR, $($s.RExpectancy)R" -ForegroundColor White
    }
}
else {
    Write-Host "  ⚠️  No strategies met minimum criteria (Grade A/B)" -ForegroundColor Yellow
}

$needsWork = $sorted | Where-Object { $_.Grade -match "^[CD]" }
if ($needsWork.Count -gt 0) {
    Write-Host ""
    Write-Host "  🔧 NEEDS OPTIMIZATION:" -ForegroundColor Yellow
    foreach ($s in $needsWork) {
        Write-Host "     - $($s.Strategy) ($($s.Timeframe)): $($s.WinRate)% WR" -ForegroundColor Gray
    }
}

# Guardar resultados
$allResults | Export-Csv -Path "comprehensive_analysis.csv" -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "💾 Full results saved to: comprehensive_analysis.csv" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ Analysis complete!" -ForegroundColor Green
