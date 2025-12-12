# ============================================
# TraderCopilot - Evaluar Señales CUSTOM
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Evaluating CUSTOM Signals" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$pythonScript = @"
import csv
import os
import io
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set

# Force UTF-8 for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup paths
BASE_DIR = Path(os.getcwd()) / 'backend'
LOGS_DIR = BASE_DIR / 'logs'
CUSTOM_DIR = LOGS_DIR / 'CUSTOM'
EVAL_DIR = LOGS_DIR / 'EVALUATED'

EVAL_DIR.mkdir(parents=True, exist_ok=True)

EVAL_HEADERS = [
    'signal_ts', 'evaluated_at', 'token', 'timeframe',
    'entry', 'tp', 'sl', 'price_at_eval', 'result', 'move_pct', 'pnl_r', 'notes'
]

def get_current_price(token: str, timeframe: str):
    '''Get current price from market data'''
    import sys
    sys.path.insert(0, str(BASE_DIR))
    from indicators.market import get_market_data
    
    df, market = get_market_data(token.lower(), timeframe)
    if market:
        return float(market['price'])
    return None

def evaluate_signal(row: Dict) -> Dict:
    '''Evaluate a single signal'''
    token = row.get('token', '').upper()
    timeframe = row.get('timeframe', '1h')
    direction = row.get('direction', 'long').lower()
    signal_ts = row.get('timestamp', '')
    
    try:
        entry = float(row.get('entry', 0))
        tp = float(row.get('tp', 0))
        sl = float(row.get('sl', 0))
    except:
        entry = tp = sl = 0
    
    # Get current price
    price_now = get_current_price(token, timeframe)
    if not price_now:
        return None
    
    # Evaluate result
    if direction == 'long':
        if price_now >= tp > 0:
            result = 'WIN'
        elif price_now <= sl < entry:
            result = 'LOSS'
        else:
            result = 'OPEN'
        move_pct = ((price_now / entry) - 1) * 100
        pnl_r = (price_now - entry) / (entry - sl) if (entry - sl) > 0 else 0
    else:  # short
        if price_now <= tp < entry:
            result = 'WIN'
        elif price_now >= sl > 0:
            result = 'LOSS'
        else:
            result = 'OPEN'
        move_pct = ((entry / price_now) - 1) * 100
        pnl_r = (entry - price_now) / (sl - entry) if (sl - entry) > 0 else 0
    
    return {
        'signal_ts': signal_ts,
        'evaluated_at': datetime.utcnow().isoformat() + 'Z',
        'token': token,
        'timeframe': timeframe,
        'entry': f'{entry:.2f}',
        'tp': f'{tp:.2f}',
        'sl': f'{sl:.2f}',
        'price_at_eval': f'{price_now:.2f}',
        'result': result,
        'move_pct': f'{move_pct:+.2f}%',
        'pnl_r': f'{pnl_r:.2f}',
        'notes': f'Evaluated at {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}'
    }

def get_evaluated_timestamps(token: str) -> Set[str]:
    '''Get already evaluated signal timestamps'''
    eval_file = EVAL_DIR / f'{token}.evaluated.csv'
    if not eval_file.exists():
        return set()
    
    evaluated = set()
    with open(eval_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            evaluated.add(row.get('signal_ts', ''))
    return evaluated

def evaluate_token(token: str) -> int:
    '''Evaluate all pending signals for a token'''
    custom_file = CUSTOM_DIR / f'{token}.csv'
    if not custom_file.exists():
        return 0
    
    evaluated_ts = get_evaluated_timestamps(token)
    
    # Read signals
    signals = []
    with open(custom_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = row.get('timestamp', '')
            if ts and ts not in evaluated_ts:
                signals.append(row)
    
    if not signals:
        return 0
    
    # Evaluate signals
    evaluations = []
    for signal in signals:
        eval_result = evaluate_signal(signal)
        if eval_result:
            evaluations.append(eval_result)
    
    if not evaluations:
        return 0
    
    # Save evaluations
    eval_file = EVAL_DIR / f'{token}.evaluated.csv'
    file_exists = eval_file.exists()
    
    with open(eval_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=EVAL_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(evaluations)
    
    return len(evaluations)

# Main execution
if not CUSTOM_DIR.exists():
    print('❌ No CUSTOM signals found')
    exit(0)

print('🔍 Evaluating CUSTOM signals...\n')

total_evaluated = 0
tokens = [f.stem for f in CUSTOM_DIR.glob('*.csv')]

for token in tokens:
    count = evaluate_token(token)
    if count > 0:
        print(f'✅ {token}: {count} signals evaluated')
        total_evaluated += count
    else:
        print(f'ℹ️  {token}: No new signals to evaluate')

print(f'\n📊 Total: {total_evaluated} signals evaluated')
"@

$pythonScript | Out-File -FilePath "temp_evaluate_custom.py" -Encoding UTF8

python temp_evaluate_custom.py

Remove-Item "temp_evaluate_custom.py" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "✅ Done! View results with: .\view_performance.ps1" -ForegroundColor Green
