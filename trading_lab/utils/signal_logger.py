# utils/signal_logger.py
import os
import pandas as pd

LOGS_DIR = "logs"

def save_signal(
    symbol: str,
    timeframe: str,
    strategy: str,
    entry_time,
    entry_price: float,
    side: str = "LONG",
    tp: float = 0.0,
    sl: float = 0.0,
    bars_timeout: int = 10,
    confidence: float = 0.0
):
    """
    Guarda señales en CSV: logs/<symbol>_<strategy>_<timeframe>.csv
    """
    os.makedirs(LOGS_DIR, exist_ok=True)
    filename = f"{symbol}_{strategy}_{timeframe}.csv"
    path = os.path.join(LOGS_DIR, filename)

    row = {
        "entry_time": pd.to_datetime(entry_time).strftime("%Y-%m-%d %H:%M:%S"),
        "side": side.upper(),
        "entry_price": float(entry_price),
        "tp": float(tp),
        "sl": float(sl),
        "bars_timeout": int(bars_timeout),
        "confidence": float(confidence),
    }
    df = pd.DataFrame([row])
    if os.path.exists(path):
        df.to_csv(path, mode="a", header=False, index=False)
    else:
        df.to_csv(path, index=False)
    return path
