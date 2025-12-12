# ============================================
# TraderCopilot - Análisis Detallado de Estrategia
# ============================================

param(
    [Parameter(Mandatory = $false)]
    [string]$Strategy = "ALL"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Strategy Performance Analysis" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$pythonScript = @"
import sys
import os
import csv
from collections import defaultdict
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

# Leer señales de CUSTOM (estrategias)
custom_path = 'backend/logs/CUSTOM'
evaluated_path = 'backend/logs/EVALUATED'

if not os.path.exists(custom_path):
    print('❌ No CUSTOM signals found')
    sys.exit(1)

# Mapear señales por timestamp
signals_by_ts = {}
for filename in os.listdir(custom_path):
    if filename.endswith('.csv'):
        token = filename.replace('.csv', '').upper()
        filepath = os.path.join(custom_path, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ts = row.get('timestamp', '')
                signals_by_ts[ts] = {
                    'token': token,
                    'source': row.get('source', 'unknown'),
                    'direction': row.get('direction', ''),
                    'entry': row.get('entry', ''),
                    'confidence': row.get('confidence', '')
                }

# Leer evaluaciones
if not os.path.exists(evaluated_path):
    print('❌ No evaluated signals found. Run evaluate_signals.ps1 first')
    sys.exit(1)

strategy_stats = defaultdict(lambda: {'wins': 0, 'losses': 0, 'be': 0, 'total_pnl': 0.0})

for filename in os.listdir(evaluated_path):
    if filename.endswith('.evaluated.csv'):
        filepath = os.path.join(evaluated_path, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                signal_ts = row.get('signal_ts', '')
                result = row.get('result', 'BE')
                pnl_r = float(row.get('pnl_r', 0))
                
                # Buscar estrategia original
                if signal_ts in signals_by_ts:
                    source = signals_by_ts[signal_ts]['source']
                    
                    if result == 'WIN':
                        strategy_stats[source]['wins'] += 1
                    elif result == 'LOSS':
                        strategy_stats[source]['losses'] += 1
                    else:
                        strategy_stats[source]['be'] += 1
                    
                    strategy_stats[source]['total_pnl'] += pnl_r

# Mostrar resultados
print('📊 Strategy Performance:\n')
print(f'{'Strategy':<30} {'Total':<8} {'Wins':<8} {'Losses':<8} {'WR%':<8} {'Total PnL%':<12}')
print('-' * 80)

for strategy, stats in sorted(strategy_stats.items()):
    total = stats['wins'] + stats['losses'] + stats['be']
    win_rate = (stats['wins'] / total * 100) if total > 0 else 0
    total_pnl = stats['total_pnl'] * 100
    
    print(f'{strategy:<30} {total:<8} {stats["wins"]:<8} {stats["losses"]:<8} {win_rate:<8.2f} {total_pnl:<12.2f}')

print()
"@

$pythonScript | Out-File -FilePath "temp_strategy_analysis.py" -Encoding UTF8

python temp_strategy_analysis.py

Remove-Item "temp_strategy_analysis.py" -ErrorAction SilentlyContinue
