# ============================================
# TraderCopilot - Ver Resumen de Señales
# ============================================

param(
    [string]$Mode = "LITE",
    [string]$Token = "ALL",
    [int]$Last = 10
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TraderCopilot - Signals Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$LogsPath = "backend\logs\$Mode"

if (-not (Test-Path $LogsPath)) {
    Write-Host "❌ No logs found for mode: $Mode" -ForegroundColor Red
    exit 1
}

$csvFiles = Get-ChildItem -Path $LogsPath -Filter "*.csv"

if ($csvFiles.Count -eq 0) {
    Write-Host "❌ No CSV files found in $LogsPath" -ForegroundColor Yellow
    exit 0
}

$allSignals = @()

foreach ($file in $csvFiles) {
    $tokenName = $file.BaseName.ToUpper()
    
    if ($Token -ne "ALL" -and $tokenName -ne $Token.ToUpper()) {
        continue
    }
    
    $signals = Import-Csv $file.FullName
    
    foreach ($signal in $signals) {
        $allSignals += [PSCustomObject]@{
            Timestamp  = $signal.timestamp
            Token      = $tokenName
            Timeframe  = $signal.timeframe
            Direction  = $signal.direction
            Entry      = [decimal]$signal.entry
            TP         = [decimal]$signal.tp
            SL         = [decimal]$signal.sl
            Confidence = [decimal]$signal.confidence
            Rationale  = $signal.rationale
            Source     = $signal.source
        }
    }
}

if ($allSignals.Count -eq 0) {
    Write-Host "❌ No signals found" -ForegroundColor Yellow
    exit 0
}

# Ordenar por timestamp descendente
$allSignals = $allSignals | Sort-Object Timestamp -Descending

Write-Host "Total Signals: $($allSignals.Count)" -ForegroundColor Green
Write-Host ""

# Estadísticas
$longCount = ($allSignals | Where-Object { $_.Direction -eq "long" }).Count
$shortCount = ($allSignals | Where-Object { $_.Direction -eq "short" }).Count
$avgConfidence = ($allSignals | Measure-Object -Property Confidence -Average).Average

Write-Host "📊 Statistics:" -ForegroundColor Cyan
Write-Host "  Long signals: $longCount" -ForegroundColor Green
Write-Host "  Short signals: $shortCount" -ForegroundColor Red
Write-Host "  Avg Confidence: $([math]::Round($avgConfidence, 2))" -ForegroundColor Yellow
Write-Host ""

# Mostrar últimas N señales
Write-Host "📋 Last $Last signals:" -ForegroundColor Cyan
Write-Host ""

$allSignals | Select-Object -First $Last | Format-Table `
@{Label = "Time"; Expression = { $_.Timestamp.Substring(11, 8) } }, `
@{Label = "Token"; Expression = { $_.Token }; Width = 6 }, `
@{Label = "TF"; Expression = { $_.Timeframe }; Width = 4 }, `
@{Label = "Dir"; Expression = { $_.Direction.ToUpper() }; Width = 5 }, `
@{Label = "Entry"; Expression = { $_.Entry }; Width = 10 }, `
@{Label = "TP"; Expression = { $_.TP }; Width = 10 }, `
@{Label = "SL"; Expression = { $_.SL }; Width = 10 }, `
@{Label = "Conf"; Expression = { $_.Confidence }; Width = 5 } `
    -AutoSize

Write-Host ""
Write-Host "💡 Tip: Use -Last 20 to see more signals" -ForegroundColor Gray
Write-Host "💡 Tip: Use -Token ETH to filter by token" -ForegroundColor Gray
