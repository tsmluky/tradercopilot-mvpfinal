# realtime.py
# Genera una señal puntual (última vela) con TP/SL y sizing por riesgo fijo.

import os
import json
import argparse
import pandas as pd
import numpy as np

from models.scoring import score_signals

DATASETS_DIR = "datasets"

def load_dataset(symbol: str, timeframe: str) -> pd.DataFrame:
    path = os.path.join(DATASETS_DIR, f"{symbol}_{timeframe}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No existe dataset: {path}")
    df = pd.read_csv(path)
    time_col = None
    for c in ["timestamp", "time", "date", "datetime", "open_time"]:
        if c in df.columns: time_col = c; break
    if time_col:
        df[time_col] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
        df = df.dropna(subset=[time_col]).sort_values(time_col).set_index(time_col)
    return df

def position_size(capital: float, risk_pct: float, entry: float, sl: float) -> float:
    """
    Tamaño por riesgo fijo. Si SL==entry, devuelve 0.
    """
    risk_amount = capital * (risk_pct / 100.0)
    per_unit_risk = abs(entry - sl)
    if per_unit_risk <= 0:
        return 0.0
    size = risk_amount / per_unit_risk
    return max(size, 0.0)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="ETHUSDT")
    ap.add_argument("--timeframe", default="1h")
    ap.add_argument("--capital", type=float, default=1000.0)
    ap.add_argument("--risk_pct", type=float, default=1.0)  # % del capital por trade
    args = ap.parse_args()

    df = load_dataset(args.symbol, args.timeframe)
    scored = score_signals(df.copy(), symbol=args.symbol, timeframe=args.timeframe)
    last = scored.iloc[-1]

    side = last["signal_side"]
    entry = float(last["close"])
    tp = float(last["tp_price"])
    sl = float(last["sl_price"])
    conf = float(last["confidence"])

    size = position_size(args.capital, args.risk_pct, entry, sl)

    out = {
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "signal_side": side,
        "confidence": round(conf, 2),
        "entry_price": entry,
        "tp_price": tp,
        "sl_price": sl,
        "risk_pct": args.risk_pct,
        "position_size_units": round(size, 6),
        "ts": str(scored.index[-1]),
    }

    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
