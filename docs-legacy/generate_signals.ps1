# ============================================
# TraderCopilot - Generar Señales Manualmente
# ============================================
# Ejecuta estrategias específicas bajo demanda

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("donchian_v2", "ma_cross_v1", "donchian_breakout_v1", "bb_mean_reversion_v1", "rsi_divergence_v1", "supertrend_flow_v1", "vwap_intraday_v1", "ALL")]
    [string]$Strategy = "donchian_v2",
    
    [Parameter(Mandatory = $false)]
    [string[]]$Tokens = @("ETH", "BTC", "SOL"),
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("15m", "30m", "1h", "4h", "1d")]
    [string]$Timeframe = "1h"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TraderCopilot - Manual Signal Generator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Strategy: $Strategy" -ForegroundColor Yellow
Write-Host "Tokens: $($Tokens -join ', ')" -ForegroundColor Yellow
Write-Host "Timeframe: $Timeframe" -ForegroundColor Yellow
Write-Host ""

$pythonScript = @"
import sys
import os
import io

# Force UTF-8 for stdout to avoid Windows charmap errors
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from strategies.registry import get_registry
from strategies.DonchianBreakoutV2 import DonchianBreakoutV2
from strategies.ma_cross import MACrossStrategy
from strategies.donchian import DonchianStrategy
from strategies.bb_mean_reversion import BBMeanReversionStrategy
from strategies.rsi_divergence import RSIDivergenceStrategy
from strategies.supertrend_flow import SuperTrendFlowStrategy
from strategies.vwap_intraday import VWAPIntradayStrategy
from core.signal_logger import log_signal

# Registrar todas las estrategias
registry = get_registry()
registry.register(DonchianBreakoutV2)
registry.register(MACrossStrategy)
registry.register(DonchianStrategy)
registry.register(BBMeanReversionStrategy)
registry.register(RSIDivergenceStrategy)
registry.register(SuperTrendFlowStrategy)
registry.register(VWAPIntradayStrategy)

strategy_id = '$Strategy'
tokens = '$($Tokens -join ',')'.split(',')
timeframe = '$Timeframe'

if strategy_id == 'ALL':
    strategies_to_run = ['donchian_v2', 'ma_cross_v1', 'donchian_breakout_v1', 'bb_mean_reversion_v1']
else:
    strategies_to_run = [strategy_id]

total_signals = 0

for strat_id in strategies_to_run:
    print(f'\n🔄 Executing: {strat_id}')
    print('=' * 50)
    
    strategy = registry.get(strat_id)
    
    if not strategy:
        print(f'❌ Strategy not found: {strat_id}')
        continue
    
    try:
        signals = strategy.generate_signals(tokens=tokens, timeframe=timeframe, context={})
        
        if len(signals) == 0:
            print(f'ℹ️  No signals generated (no setup detected)')
        else:
            print(f'✅ Generated {len(signals)} signals:\n')
            
            for signal in signals:
                log_signal(signal)
                total_signals += 1
                
                dir_color = '🟢' if signal.direction == 'long' else '🔴'
                print(f'{dir_color} {signal.token} {signal.direction.upper()} @ {signal.entry}')
                print(f'   TP: {signal.tp} | SL: {signal.sl} | Confidence: {signal.confidence}')
                print(f'   Rationale: {signal.rationale}')
                print()
    
    except Exception as e:
        print(f'❌ Error executing {strat_id}: {e}')
        import traceback
        traceback.print_exc()

print('\n' + '=' * 50)
print(f'✅ Total signals generated: {total_signals}')
print('=' * 50)
"@

$pythonScript | Out-File -FilePath "temp_generate_signals.py" -Encoding UTF8

Write-Host "Executing..." -ForegroundColor Cyan
python temp_generate_signals.py

Remove-Item "temp_generate_signals.py" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "✅ Done! Check signals with: .\view_signals.ps1" -ForegroundColor Green
