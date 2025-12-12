# ============================================
# TraderCopilot - Evaluar Señales
# ============================================
# Verifica si las señales alcanzaron TP o SL usando datos reales de mercado

param(
    [Parameter(Mandatory = $false)]
    [string]$Mode = "CUSTOM",  # LITE, PRO, CUSTOM
    
    [Parameter(Mandatory = $false)]
    [string]$Token = "ALL"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TraderCopilot - Signal Evaluator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Mode: $Mode" -ForegroundColor Yellow
Write-Host "Token: $Token" -ForegroundColor Yellow
Write-Host ""

$pythonScript = @"
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from evaluated_logger import evaluate_all_tokens

print('🔍 Evaluating signals...\n')

processed, new_evaluations = evaluate_all_tokens()

print(f'\n📊 Results:')
print(f'  Tokens processed: {processed}')
print(f'  New evaluations: {new_evaluations}')

if new_evaluations > 0:
    print(f'\n✅ {new_evaluations} signals evaluated!')
    print(f'Check results in: backend/logs/EVALUATED/')
else:
    print(f'\nℹ️  No new signals to evaluate')
"@

$pythonScript | Out-File -FilePath "temp_evaluate.py" -Encoding UTF8

Write-Host "Evaluating..." -ForegroundColor Cyan
python temp_evaluate.py

Remove-Item "temp_evaluate.py" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "✅ Done! View results with: .\view_performance.ps1" -ForegroundColor Green
