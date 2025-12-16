# backend/scheduler.py
"""
Simple Strategy Scheduler (Marketplace Edition)

Script que ejecuta las "Personas" del Marketplace en loop constante.
NO requiere Docker ni cron, solo:
    python scheduler.py
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

# Setup path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from database import SessionLocal
from strategies.registry import get_registry
from core.signal_logger import log_signal
from marketplace_config import get_active_strategies

class StrategyScheduler:
    """
    Scheduler de Estrategias (Modo Marketplace).
    
    Ejecuta las 'Personas' definidas en marketplace_config.py
    """
    
    def __init__(self, loop_interval: int = 60):
        self.loop_interval = loop_interval
        self.registry = get_registry()
        
        print("="*60)
        print("🚀 TraderCopilot - Marketplace Scheduler")
        print("="*60)
        
        # Registrar estrategias built-in
        print("\n📦 Registering strategies...")
        from strategies.example_rsi_macd import RSIMACDDivergenceStrategy
        from strategies.ma_cross import MACrossStrategy
        from strategies.DonchianBreakoutV2 import DonchianBreakoutV2 as DonchianStrategy
        from strategies.bb_mean_reversion import BBMeanReversionStrategy
        from strategies.rsi_divergence import RSIDivergenceStrategy
        from strategies.TrendFollowingNative import TrendFollowingNative
        from strategies.DonchianBreakoutV2 import DonchianBreakoutV2
        
        self.registry.register(RSIMACDDivergenceStrategy)
        self.registry.register(MACrossStrategy)
        self.registry.register(DonchianStrategy)
        self.registry.register(BBMeanReversionStrategy)
        self.registry.register(RSIDivergenceStrategy)
        self.registry.register(TrendFollowingNative)
        self.registry.register(DonchianBreakoutV2)
        print("✅ Strategies registered")
        
        # State tracking for intervals
        self.last_run = {} # {persona_id: timestamp}
        self.processed_signals = {} # {signal_key: timestamp}
        self.last_signal_direction = {} # {persona_id_token: direction} (For alternation enforcement)
    
    def run(self):
        """Loop principal."""
        iteration = 0
        try:
            while True:
                iteration += 1
                # User requests Buenos Aires Time (UTC-3) for logs
                now = datetime.utcnow()
                ba_time = now - timedelta(hours=3)
                print(f"\n[{ba_time.strftime('%H:%M:%S')}] Iteration #{iteration}")
                
                # 1. Obtener Personas Activas
                personas = get_active_strategies()
                print(f"  ℹ️  Active Personas: {len(personas)}")
                
                # 2. Ejecutar cada Persona
                for persona in personas:
                    p_id = persona["id"]
                    
                    # Rate Limit simple (ej: cada 5 mins para todos, o custom)
                    # Por ahora, usamos interval global de loop (60s)
                    # Si quisiéramos per-strategy intervals, checkeamos self.last_run[p_id]
                    
                    print(f"  🔄 Running Persona: {persona['name']} ({persona['symbol']}/{persona['timeframe']})")
                    
                    # Instanciar estrategia técnica
                    strategy_id = persona["strategy_id"]
                    strategy = self.registry.get(strategy_id)
                    
                    if not strategy:
                        print(f"  ⚠️  Strategy class '{strategy_id}' not found!")
                        continue
                        
                    try:
                        # Ejecutar
                        signals = strategy.generate_signals(
                            tokens=[persona["symbol"]],
                            timeframe=persona["timeframe"]
                        )
                        
                        count = 0
                        for sig in signals:
                            # Deduplication Logic 3.0: Timestamp AND Alternation
                            # 1. Prevent reprocessing old signals (History spam)
                            ts_key = f"{p_id}_{sig.token}"
                            last_ts = self.processed_signals.get(ts_key)
                            
                            if last_ts and sig.timestamp <= last_ts:
                                continue

                            # 2. Prevent same-side spam (Visual Clarity)
                            last_dir = self.last_signal_direction.get(ts_key)
                            if last_dir == sig.direction:
                                continue
                            
                            # 3. Valid New Signal
                            self.processed_signals[ts_key] = sig.timestamp
                            self.last_signal_direction[ts_key] = sig.direction
                            
                            # Enriquecer source con el ID de la persona
                            # sig.source = f"Marketplace:{p_id}" 
                            # FIX user confusion: Use the Human Readable Name (e.g. "The Scalper")
                            sig.source = persona['name']
                            log_signal(sig)
                            count += 1
                            print(f"    ⭐ SIGNAL: {sig.direction} @ {sig.entry}")
                            
                        if count == 0:
                            print("    (No new signals)")
                            
                        self.last_run[p_id] = now
                        
                    except Exception as e:
                        print(f"  ❌ Error executing {persona['name']}: {e}")
                
                # 3. Evaluador PnL (Critico para mostrar profit real)
                print("  ⚖️  Evaluating Pending Signals...")
                try:
                    from evaluated_logger import evaluate_all_tokens
                    processed, new_evals = evaluate_all_tokens()
                    if new_evals > 0:
                        print(f"    ✅ Evaluated {new_evals} signals")
                except Exception as e:
                    print(f"  ❌ Eval Error: {e}")

                print(f"  😴 Sleeping {self.loop_interval}s...")
                time.sleep(self.loop_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopped.")

if __name__ == "__main__":
    scheduler = StrategyScheduler(loop_interval=10)
    scheduler.run()

