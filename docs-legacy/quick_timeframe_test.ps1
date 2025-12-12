# ============================================
# TraderCopilot - Test Rápido de Timeframes
# ============================================
# Versión más rápida que solo prueba Donchian V2

param(
    [Parameter(Mandatory = $false)]
    [string[]]$Timeframes = @("15m", "30m", "1h", "4h", "1d")
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Quick Timeframe Test - Donchian V2" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Limpiar
Remove-Item -Path backend\logs\CUSTOM\*.csv -Force -ErrorAction SilentlyContinue
Remove-Item -Path backend\logs\EVALUATED\*.csv -Force -ErrorAction SilentlyContinue

$results = @()

foreach ($tf in $Timeframes) {
    Write-Host "Testing $tf..." -ForegroundColor Yellow
    
    # Generar
    .\generate_signals.ps1 -Strategy "donchian_v2" -Tokens @("ETH", "BTC", "SOL") -Timeframe $tf | Out-Null
    
    # Evaluar
    .\evaluate_custom_signals.ps1 | Out-Null
    
    # Calcular stats
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
    
    $results += [PSCustomObject]@{
        Timeframe = $tf
        Signals   = $total
        Wins      = $allWins
        Losses    = $allLosses
        WinRate   = $winRate
        TotalPnL  = [math]::Round($totalPnL, 2)
    }
    
    # Limpiar para próximo
    Remove-Item -Path backend\logs\CUSTOM\*.csv -Force -ErrorAction SilentlyContinue
    Remove-Item -Path backend\logs\EVALUATED\*.csv -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "📊 Results:" -ForegroundColor Cyan
$results | Format-Table -AutoSize

$best = $results | Sort-Object WinRate -Descending | Select-Object -First 1
Write-Host ""
Write-Host "🏆 Best Timeframe: $($best.Timeframe) with $($best.WinRate)% win rate" -ForegroundColor Green
