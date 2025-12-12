# ============================================
# TraderCopilot - Verificar Señales en DB
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Database Signals Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Crear script Python temporal
$pythonScript = @"
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from database import SessionLocal
from models_db import Signal, StrategyConfig
from sqlalchemy import func, desc

db = SessionLocal()

# Contar señales por modo
print('📊 Signals by Mode:')
modes = db.query(Signal.mode, func.count(Signal.id)).group_by(Signal.mode).all()
for mode, count in modes:
    print(f'  {mode}: {count} signals')

print()

# Contar señales por token
print('📊 Signals by Token:')
tokens = db.query(Signal.token, func.count(Signal.id)).group_by(Signal.token).all()
for token, count in tokens:
    print(f'  {token}: {count} signals')

print()

# Últimas 5 señales
print('📋 Last 5 Signals:')
signals = db.query(Signal).order_by(desc(Signal.timestamp)).limit(5).all()
for s in signals:
    print(f'  [{s.timestamp.strftime("%H:%M:%S")}] {s.token} {s.direction.upper()} @ {s.entry} | Mode: {s.mode}')

print()

# Estrategias activas
print('⚙️  Active Strategies:')
strategies = db.query(StrategyConfig).filter(StrategyConfig.enabled == 1).all()
for strat in strategies:
    last_exec = strat.last_execution.strftime('%H:%M:%S') if strat.last_execution else 'Never'
    print(f'  {strat.name} ({strat.strategy_id})')
    print(f'    Last execution: {last_exec}')
    print(f'    Total signals: {strat.total_signals}')
    print(f'    Interval: {strat.interval_seconds}s')
    print()

db.close()
"@

$pythonScript | Out-File -FilePath "temp_check_db.py" -Encoding UTF8

python temp_check_db.py

Remove-Item "temp_check_db.py" -ErrorAction SilentlyContinue
