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
        from strategies.donchian import DonchianStrategy
        from strategies.bb_mean_reversion import BBMeanReversionStrategy
        from strategies.rsi_divergence import RSIDivergenceStrategy
        from strategies.TrendFollowingNative import TrendFollowingNative
        
        self.registry.register(RSIMACDDivergenceStrategy)
        self.registry.register(MACrossStrategy)
        self.registry.register(DonchianStrategy)
        self.registry.register(BBMeanReversionStrategy)
        self.registry.register(RSIDivergenceStrategy)
        self.registry.register(TrendFollowingNative)
        print("✅ Strategies registered")
        
        # State tracking for intervals
        self.last_run = {} # {persona_id: timestamp}
    
    def run(self):
        """Loop principal."""
        iteration = 0
        try:
            while True:
                iteration += 1
                now = datetime.utcnow()
                print(f"\n[{now.strftime('%H:%M:%S')}] Iteration #{iteration}")
                
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
                            # Enriquecer source con el ID de la persona
                            sig.source = f"Marketplace:{p_id}"
                            log_signal(sig)
                            count += 1
                            print(f"    ⭐ SIGNAL: {sig.direction} @ {sig.entry}")
                            
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
    scheduler = StrategyScheduler(loop_interval=60)
    scheduler.run()
Script que ejecuta estrategias registradas en loop constante.

NO requiere Docker ni cron, solo:
    python scheduler.py

Ejecuta cada estrategia que esté enabled=True en la base de datos,
respetando su interval_seconds configurado.
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
from models_db import StrategyConfig
from strategies.registry import get_registry
from core.signal_logger import log_signal
from core.schemas import Signal


class StrategyScheduler:
    """
    Scheduler simple de estrategias.
    
    Ejecuta estrategias en loop, respetando:
    - enabled: Solo ejecuta si está activa
    - interval_seconds: Tiempo mínimo entre ejecuciones
    - last_execution: No ejecuta si no ha pasado el intervalo
    """
    
    def __init__(self, loop_interval: int = 10):
        """
        Args:
            loop_interval: Segundos entre chequeos del loop principal (10s default)
        """
        self.loop_interval = loop_interval
        self.registry = get_registry()
        self.db = SessionLocal()
        
        print("="*60)
        print("🚀 TraderCopilot - Strategy Scheduler")
        print("="*60)
        print(f"Loop interval: {self.loop_interval}s")
        
        # Registrar estrategias built-in
        # Registrar estrategias built-in
        print("\n📦 Registering built-in strategies...")
        from strategies.example_rsi_macd import RSIMACDDivergenceStrategy
        from strategies.ma_cross import MACrossStrategy
        from strategies.donchian import DonchianStrategy
        from strategies.bb_mean_reversion import BBMeanReversionStrategy
        from strategies.DonchianBreakoutV2 import DonchianBreakoutV2
        
        self.registry.register(RSIMACDDivergenceStrategy)
        self.registry.register(MACrossStrategy)
        self.registry.register(DonchianStrategy)
        self.registry.register(BBMeanReversionStrategy)
        self.registry.register(DonchianBreakoutV2)
        print("✅ Strategies registered")
        
        print(f"\nPress Ctrl+C to stop\n")
    
    def load_strategies_from_db(self) -> list:
        """Carga estrategias enabled de la base de datos."""
        try:
            configs = self.db.query(StrategyConfig).filter(
                StrategyConfig.enabled == 1
            ).all()
            return configs
        except Exception as e:
            print(f"❌ Error loading strategies from DB: {e}")
            return []
    
    def should_execute(self, config: StrategyConfig) -> bool:
        """
        Determina si una estrategia debe ejecutarse ahora.
        
        Args:
            config: Configuración de la estrategia
            
        Returns:
            True si debe ejecutarse, False en caso contrario
        """
        if not config.enabled:
            return False
        
        # Si nunca se ha ejecutado, ejecutar ahora
        if not config.last_execution:
            return True
        
        # Calcular tiempo transcurrido
        now = datetime.utcnow()
        elapsed = (now - config.last_execution).total_seconds()
        
        # Ejecutar si ya pasó el intervalo
        return elapsed >= config.interval_seconds
    
    def execute_strategy(self, config: StrategyConfig) -> int:
        """
        Ejecuta una estrategia y loguea sus señales.
        
        Args:
            config: Configuración de la estrategia
            
        Returns:
            Número de señales generadas
        """
        # Obtener instancia de la estrategia del registry
        config_dict = json.loads(config.config_json) if config.config_json else {}
        strategy = self.registry.get(config.strategy_id, config=config_dict)
        
        if not strategy:
            print(f"⚠️  Strategy '{config.strategy_id}' not found in registry")
            return 0
        
        # Parsear tokens y timeframes
        tokens = json.loads(config.tokens) if config.tokens else []
        timeframes = json.loads(config.timeframes) if config.timeframes else [strategy.metadata().default_timeframe]
        
        # Generar señales para cada combinación token/timeframe
        total_signals = 0
        
        for tf in timeframes:
            try:
                signals = strategy.generate_signals(
                    tokens=tokens,
                    timeframe=tf,
                    context={}
                )
                
                # Loguear cada señal
                for signal in signals:
                    log_signal(signal)
                    total_signals += 1
                    print(f"  📊 Signal: {signal.token} {signal.direction} @ {signal.entry}")
                
            except Exception as e:
                print(f"  ❌ Error generating signals for {tf}: {e}")
                import traceback
                traceback.print_exc()
        
        # Actualizar estadísticas en DB
        try:
            config.last_execution = datetime.utcnow()
            config.total_signals += total_signals
            self.db.commit()
        except Exception as e:
            print(f"  ⚠️  Error updating stats: {e}")
            self.db.rollback()
        
        return total_signals
    
    def run(self):
        """
        Loop principal del scheduler.
        
        Ejecuta indefinidamente hasta Ctrl+C.
        """
        iteration = 0
        
        try:
            while True:
                iteration += 1
                now = datetime.utcnow()
                print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] Iteration #{iteration}")
                
                # Cargar estrategias activas de DB
                configs = self.load_strategies_from_db()
                
                if not configs:
                    print("  ℹ️  No active strategies found in DB")
                else:
                    print(f"  ℹ️  Active strategies: {len(configs)}")
                
                # Ejecutar las que toquen
                executed = 0
                for config in configs:
                    if self.should_execute(config):
                        print(f"\n  🔄 Executing: {config.name} ({config.strategy_id})")
                        try:
                            signals_count = self.execute_strategy(config)
                            print(f"  ✅ Generated {signals_count} signals")
                            executed += 1
                        except Exception as e:
                            print(f"  ❌ Execution failed: {e}")
                            import traceback
                            traceback.print_exc()
                
                if executed == 0:
                    print("  💤 No strategies ready to execute")
                
                # Sleep hasta próximo chequeo
                print(f"\n  😴 Sleeping for {self.loop_interval}s...")
                
                # --- NUEVO: Ejecutar evaluación de señales ---
                print("  ⚖️  Running signal evaluator...")
                try:
                    from evaluated_logger import evaluate_all_tokens
                    processed, new_evals = evaluate_all_tokens()
                    if new_evals > 0:
                        print(f"  ✅ Evaluated {new_evals} pending signals")
                except Exception as e:
                    print(f"  ❌ Error running evaluator: {e}")
                # ---------------------------------------------

                time.sleep(self.loop_interval)
        
        except KeyboardInterrupt:
            print("\n\n🛑 Scheduler stopped by user")
        except Exception as e:
            print(f"\n\n❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.db.close()
            print("👋 Goodbye!")


if __name__ == "__main__":
    # Verificar argumentos
    loop_interval = 10  # segundos
    
    if len(sys.argv) > 1:
        try:
            loop_interval = int(sys.argv[1])
        except ValueError:
            print("Usage: python scheduler.py [loop_interval_seconds]")
            print("Example: python scheduler.py 30  # Check every 30 seconds")
            sys.exit(1)
    
    # Iniciar scheduler
    scheduler = StrategyScheduler(loop_interval=loop_interval)
    scheduler.run()
