import sys
import os
import pandas as pd
from datetime import datetime

# Añadir el directorio actual al path para que funcionen los imports absolutos (core.*, strategies.*)
sys.path.append(os.path.join(os.getcwd(), "demo_execution"))

from demo_execution.services.market_data import MockMarketDataService
from demo_execution.strategies.implementations.trend_ma_strategy import TrendMaCrossStrategy
from demo_execution.strategies.implementations.donchian_strategy import DonchianBreakoutStrategy
from demo_execution.strategies.base import StrategyConfigInRuntime

def run_demo():
    print("🚀 Iniciando DEMO de Integración (Simulación de Backend)...")
    
    # 1. Inicializar Servicios
    md_service = MockMarketDataService(datasets_dir="data")
    
    # 2. Configurar Estrategias a Probar
    s1 = TrendMaCrossStrategy()
    s1.default_timeframe = "60"
    
    s2 = DonchianBreakoutStrategy()
    s2.default_timeframe = "60"

    strategies_to_run = [s1, s2]
    
    all_signals = []

    # 3. Loop de Ejecución (Simulando un tick del Scheduler)
    print(f"\n📅 Tick: {datetime.utcnow()} (Simulado)")
    
    for strategy in strategies_to_run:
        print(f"\n▶ Ejecutando Estrategia: {strategy.name} ({strategy.id})")
        
        # Configuración de runtime (Tokens a operar)
        config = StrategyConfigInRuntime(
            tokens=["ETH"], # Intentará leer ETHUSDT_60.csv
            params=strategy.default_params
        )
        
        # EJECUCIÓN
        signals = strategy.run(config, md_service)
        
        print(f"  ↳ Señales generadas: {len(signals)}")
        for sig in signals:
            print(f"    🔥 {sig.direction} {sig.token} @ {sig.entry_price:.2f} | TP: {sig.tp_price:.2f} | SL: {sig.sl_price:.2f}")
            all_signals.append(sig.dict())

    # 4. Persistencia (Simulada)
    if all_signals:
        df_sig = pd.DataFrame(all_signals)
        output_file = "demo_execution/signals_log.csv"
        df_sig.to_csv(output_file, index=False)
        print(f"\n✅ Señales guardadas en: {output_file}")
        print(df_sig[["strategy_id", "token", "direction", "entry_price", "created_at"]])
        
        # 5. Cuantificación Preliminar (Simulación de Evaluación)
        # Aquí podríamos simular ver si ganaron o perdieron si tuviéramos datos futuros,
        # pero como estamos corriendo sobre la ÚLTIMA vela del CSV, son señales "vivas".
        print("\n📊 Estado: Estas señales son 'LIVE' (basadas en la última vela del dataset).")
        print("   En un entorno real, el 'SignalEvaluatorWorker' esperaría nuevas velas para validarlas.")
    else:
        print("\n⚠️ No se generaron señales en este tick (es normal, las estrategias no operan en cada vela).")

if __name__ == "__main__":
    run_demo()
