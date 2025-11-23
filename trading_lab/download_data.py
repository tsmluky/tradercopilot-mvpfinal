import ccxt
import pandas as pd
import os

# =========================
# Configuración
# =========================
symbols = ["ETH/USDT", "BTC/USDT", "SOL/USDT"]
timeframes = ["15m", "1h", "4h", "1d"]
limit = 1000  # Velas por petición (máx. Binance)
start_date = '2018-01-01T00:00:00Z'  # Fecha inicial
output_dir = os.path.join(os.path.dirname(__file__), "datasets")  # Carpeta datasets en raíz

# Crear carpeta datasets si no existe
os.makedirs(output_dir, exist_ok=True)

# =========================
# Conexión a Binance
# =========================
exchange = ccxt.binance()

def fetch_ohlcv(symbol, timeframe):
    """Descarga datos OHLCV completos desde la fecha de inicio."""
    all_data = []
    since = exchange.parse8601(start_date)

    while True:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
        if not ohlcv:
            break
        all_data.extend(ohlcv)
        since = ohlcv[-1][0] + 1  # Avanza al siguiente lote
        print(f"Descargadas {len(all_data)} velas para {symbol} {timeframe}...")
        if len(ohlcv) < limit:
            break

    # Convertir a DataFrame
    df = pd.DataFrame(all_data, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

# =========================
# Descarga y guardado
# =========================
for symbol in symbols:
    for tf in timeframes:
        print(f"📥 Descargando {symbol} {tf} desde {start_date}...")
        df = fetch_ohlcv(symbol, tf)
        file_name = f"{symbol.replace('/', '')}_{tf}.csv"
        path = os.path.join(output_dir, file_name)
        df.to_csv(path, index=False)
        print(f"✅ Guardado: {path}")

print("\n🎯 Descarga completada. Archivos en carpeta 'datasets/'")
