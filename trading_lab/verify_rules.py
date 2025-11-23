import sys
import os
import pandas as pd
import numpy as np

# Add root to path to import engine
sys.path.append(os.getcwd())

try:
    from engine import load_dataset, ensure_min_features, ma_cross_series
except ImportError:
    print("Could not import engine.py. Make sure you are running this from trading_lab root.")
    sys.exit(1)

from trading_rules.indicators import ensure_features as new_ensure_features
from trading_rules.side_generators import side_ma_cross
from trading_rules.signal_builder import compute_entry_tp_sl

def test_ma_cross_equivalence():
    print("🔍 Verificando portabilidad de reglas (Old Engine vs New Modules)...")
    
    # 1. Cargar Datos
    symbol = "ETHUSDT"
    tf = "1h" # Usamos 1h que suele haber datos
    try:
        df = load_dataset(symbol, tf)
        print(f"Datos cargados: {symbol} {tf} ({len(df)} velas)")
    except FileNotFoundError:
        print(f"❌ No se encontró dataset para {symbol} {tf}. Intenta con otro.")
        return

    # 2. Ejecutar Lógica Antigua (Engine)
    print("Ejecutando lógica antigua...")
    df_old = ensure_min_features(df.copy())
    old_series = ma_cross_series(df_old, 20, 50)
    
    # 3. Ejecutar Nueva Lógica (Trading Rules)
    print("Ejecutando nueva lógica modular...")
    df_new = new_ensure_features(df.copy())
    new_series = side_ma_cross(df_new, 20, 50)
    
    # 4. Comparar Resultados
    # Reemplazar NaN/None con "" para comparar strings
    old_series = old_series.fillna("")
    new_series = new_series.fillna("")
    
    matches = (old_series == new_series).all()
    
    if matches:
        print("✅ ÉXITO: La lógica portada produce EXACTAMENTE los mismos resultados.")
    else:
        print("❌ FALLO: Hay diferencias en las señales generadas.")
        diff = old_series.compare(new_series)
        print(diff.head())

    # 5. Probar Signal Builder (Simulación de Live)
    print("\n🛠 Probando Signal Builder (Simulación Live)...")
    # Forzamos un slice donde sepamos que hubo cruce o usamos el último
    last_sig = compute_entry_tp_sl(df_new, new_series, tp_atr=1.5, sl_atr=1.0)
    print("Output del Signal Builder:", last_sig)
    
    if last_sig["side"] != "NO_TRADE":
        print(f"¡Señal detectada! {last_sig['side']} @ {last_sig['entry_price']:.2f}")
    else:
        print("No hay señal en la última vela (comportamiento normal si no hubo cruce reciente).")

if __name__ == "__main__":
    test_ma_cross_equivalence()
