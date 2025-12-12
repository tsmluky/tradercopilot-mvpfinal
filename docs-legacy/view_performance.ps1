# ============================================
# TraderCopilot - Ver Performance de Señales
# ============================================

param(
    [Parameter(Mandatory = $false)]
    [string]$Token = "ALL",
    
    [Parameter(Mandatory = $false)]
    [int]$Last = 20
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TraderCopilot - Performance Report" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$evaluatedPath = "backend\logs\EVALUATED"

if (-not (Test-Path $evaluatedPath)) {
    Write-Host "❌ No evaluated signals found. Run .\evaluate_signals.ps1 first" -ForegroundColor Red
    exit 1
}

$csvFiles = Get-ChildItem -Path $evaluatedPath -Filter "*.evaluated.csv"

if ($csvFiles.Count -eq 0) {
    Write-Host "❌ No evaluated signals found. Run .\evaluate_signals.ps1 first" -ForegroundColor Yellow
    exit 0
}

$allEvaluations = @()

foreach ($file in $csvFiles) {
    $tokenName = $file.BaseName.Replace(".evaluated", "").ToUpper()
    
    if ($Token -ne "ALL" -and $tokenName -ne $Token.ToUpper()) {
        continue
    }
    
    $evals = Import-Csv $file.FullName
    
    foreach ($eval in $evals) {
        $allEvaluations += [PSCustomObject]@{
            SignalTime = $eval.signal_ts
            EvalTime   = $eval.evaluated_at
            Token      = $tokenName
            Timeframe  = $eval.timeframe
            Direction  = $eval.direction
            Entry      = [decimal]$eval.entry
            TP         = [decimal]$eval.tp
            SL         = [decimal]$eval.sl
            ExitPrice  = [decimal]$eval.price_at_eval
            Result     = $eval.result
            MovePct    = $eval.move_pct
            PnLR       = if ($eval.pnl_r) { [decimal]$eval.pnl_r } else { 0 }
        }
    }
}

if ($allEvaluations.Count -eq 0) {
    Write-Host "❌ No evaluations found for token: $Token" -ForegroundColor Yellow
    exit 0
}

# Ordenar por timestamp descendente
$allEvaluations = $allEvaluations | Sort-Object SignalTime -Descending

# Calcular estadísticas
$totalSignals = $allEvaluations.Count
$wins = ($allEvaluations | Where-Object { $_.Result -eq "WIN" }).Count
$losses = ($allEvaluations | Where-Object { $_.Result -eq "LOSS" }).Count
$breakeven = ($allEvaluations | Where-Object { $_.Result -eq "BE" }).Count
$winRate = if ($totalSignals -gt 0) { [math]::Round(($wins / $totalSignals) * 100, 2) } else { 0 }
$avgPnL = if ($totalSignals -gt 0) { [math]::Round(($allEvaluations | Measure-Object -Property PnLR -Average).Average * 100, 2) } else { 0 }
$totalPnL = [math]::Round(($allEvaluations | Measure-Object -Property PnLR -Sum).Sum * 100, 2)

Write-Host "📊 Overall Statistics:" -ForegroundColor Cyan
Write-Host "  Total Signals: $totalSignals" -ForegroundColor White
Write-Host "  Wins: $wins" -ForegroundColor Green
Write-Host "  Losses: $losses" -ForegroundColor Red
Write-Host "  Breakeven: $breakeven" -ForegroundColor Yellow
Write-Host "  Win Rate: $winRate%" -ForegroundColor $(if ($winRate -ge 50) { "Green" } else { "Red" })
Write-Host "  Avg PnL: $avgPnL%" -ForegroundColor $(if ($avgPnL -gt 0) { "Green" } else { "Red" })
Write-Host "  Total PnL: $totalPnL%" -ForegroundColor $(if ($totalPnL -gt 0) { "Green" } else { "Red" })
Write-Host ""

# Estadísticas por token
Write-Host "📊 Performance by Token:" -ForegroundColor Cyan
$tokenStats = $allEvaluations | Group-Object Token | ForEach-Object {
    $tokenEvals = $_.Group
    $tokenWins = ($tokenEvals | Where-Object { $_.Result -eq "WIN" }).Count
    $tokenTotal = $tokenEvals.Count
    $tokenWinRate = if ($tokenTotal -gt 0) { [math]::Round(($tokenWins / $tokenTotal) * 100, 2) } else { 0 }
    $tokenPnL = [math]::Round(($tokenEvals | Measure-Object -Property PnLR -Sum).Sum * 100, 2)
    
    [PSCustomObject]@{
        Token    = $_.Name
        Total    = $tokenTotal
        Wins     = $tokenWins
        WinRate  = "$tokenWinRate%"
        TotalPnL = "$tokenPnL%"
    }
}

$tokenStats | Format-Table -AutoSize
Write-Host ""

# Mostrar últimas N evaluaciones
Write-Host "📋 Last $Last Evaluated Signals:" -ForegroundColor Cyan
Write-Host ""

$allEvaluations | Select-Object -First $Last | ForEach-Object {
    $resultColor = switch ($_.Result) {
        "WIN" { "Green" }
        "LOSS" { "Red" }
        default { "Yellow" }
    }
    
    $resultSymbol = switch ($_.Result) {
        "WIN" { "✅" }
        "LOSS" { "❌" }
        default { "⚖️" }
    }
    
    Write-Host "$resultSymbol " -NoNewline -ForegroundColor $resultColor
    Write-Host "$($_.Token) $($_.Direction.ToUpper()) @ $($_.Entry) → $($_.ExitPrice) | " -NoNewline
    Write-Host "$($_.Result)" -ForegroundColor $resultColor -NoNewline
    Write-Host " | PnL: $($_.MovePct)" -ForegroundColor $(if ($_.PnLR -gt 0) { "Green" } else { "Red" })
    Write-Host "  Signal: $($_.SignalTime.Substring(0,16)) | Eval: $($_.EvalTime.Substring(0,16))" -ForegroundColor Gray
    Write-Host ""
}

Write-Host ""
Write-Host "💡 Tip: Use -Token ETH to see only ETH performance" -ForegroundColor Gray
Write-Host "💡 Tip: Use -Last 50 to see more results" -ForegroundColor Gray
