# ============================================
# TraderCopilot - Forzar Ejecución de Estrategia
# ============================================

param(
    [string]$Strategy = "donchian_v2",
    [string[]]$Tokens = @("ETH", "BTC", "SOL"),
    [string]$Timeframe = "1h"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Force Strategy Execution" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Strategy: $Strategy" -ForegroundColor Yellow
Write-Host "Tokens: $($Tokens -join ', ')" -ForegroundColor Yellow
Write-Host "Timeframe: $Timeframe" -ForegroundColor Yellow
Write-Host ""

# Crear script Python temporal para ejecutar estrategia
$pythonScript = @"
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from strategies.registry import get_registry
from strategies.DonchianBreakoutV2 import DonchianBreakoutV2
from core.signal_logger import log_signal

# Registrar estrategia
registry = get_registry()
registry.register(DonchianBreakoutV2)

# Obtener instancia
strategy = registry.get('$Strategy')

if not strategy:
    print('❌ Strategy not found: $Strategy')
    sys.exit(1)

# Ejecutar
tokens = '$($Tokens -join ',')'.split(',')
signals = strategy.generate_signals(tokens=tokens, timeframe='$Timeframe', context={})

print(f'\n✅ Generated {len(signals)} signals\n')

for signal in signals:
    log_signal(signal)
    print(f'📊 {signal.token} {signal.direction.upper()} @ {signal.entry}')
    print(f'   TP: {signal.tp} | SL: {signal.sl} | Conf: {signal.confidence}')
    print(f'   {signal.rationale}\n')

if len(signals) == 0:
    print('ℹ️  No signals generated (no setup detected)')
"@

$pythonScript | Out-File -FilePath "temp_force_strategy.py" -Encoding UTF8

# Ejecutar
Write-Host "Executing strategy..." -ForegroundColor Cyan
python temp_force_strategy.py

# Limpiar
Remove-Item "temp_force_strategy.py" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
