# live_signals.py
# Genera señales "última vela" para TODAS las estrategias activas del catálogo.
# Guarda results/live_signals.csv y results/<RUN_ID>/live_signals.csv

import os, sys, json
from datetime import datetime, timezone
from typing import Dict, Any, List

import numpy as np
import pandas as pd
import yaml

DATASETS_DIR = "datasets"
RESULTS_DIR  = "results"

COMMISSION_PCT_PER_SIDE = 0.04 / 100.0
SLIPPAGE_PCT_PER_SIDE   = 0.02 / 100.0

RUN_ID = datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%M%S")

# -------- utilidades comunes --------
def _infer_time_col(df: pd.DataFrame) -> str:
    for c in ["timestamp","time","date","datetime","open_time"]:
        if c in df.columns: return c
    return ""

def load_dataset(symbol: str, timeframe: str, fast_tail: int = 5000) -> pd.DataFrame:
    path = os.path.join(DATASETS_DIR, f"{symbol}_{timeframe}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No existe dataset: {path}")
    df = pd.read_csv(path)
    tcol = _infer_time_col(df)
    if tcol:
        df[tcol] = pd.to_datetime(df[tcol], utc=True, errors="coerce")
        df = df.dropna(subset=[tcol]).sort_values(tcol).set_index(tcol)
    cols_lower = [c.lower() for c in df.columns]
    for k in ["open","high","low","close","volume"]:
        if k in cols_lower:
            df[k] = df[df.columns[cols_lower.index(k)]]
    if len(df) > fast_tail:
        df = df.tail(fast_tail)
    return df

def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()

def rma(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(alpha=1/n, adjust=False).mean()

def ensure_features(df: pd.DataFrame) -> pd.DataFrame:
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat([(high-low).abs(),
                    (high-prev_close).abs(),
                    (low-prev_close).abs()], axis=1).max(axis=1)
    df["ATR"] = rma(tr, 14)
    df["EMA50"] = ema(close, 50)
    df["EMA200"] = ema(close, 200)
    # Bollinger auxiliares si se usan
    return df

# -------- generadores de señal --------
def side_ma_cross(df: pd.DataFrame, fast: int, slow: int) -> pd.Series:
    f = ema(df["close"], fast)
    s = ema(df["close"], slow)
    cross_up = (f > s) & (f.shift(1) <= s.shift(1))
    cross_dn = (f < s) & (f.shift(1) >= s.shift(1))
    return pd.Series(np.where(cross_up,"LONG",np.where(cross_dn,"SHORT","")), index=df.index)

def side_donchian(df: pd.DataFrame, n: int, atr_pct_min: float) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    donch_high = high.rolling(n, min_periods=n).max().shift(1)
    donch_low  = low .rolling(n, min_periods=n).min().shift(1)
    atr_pct = (df["ATR"]/close).fillna(0.0)
    up = close > df["EMA200"]; dn = close < df["EMA200"]
    long_sig  = (high > donch_high) & (atr_pct >= atr_pct_min) & up
    short_sig = (low  < donch_low ) & (atr_pct >= atr_pct_min) & dn
    return pd.Series(np.where(long_sig,"LONG",np.where(short_sig,"SHORT","")), index=df.index)

def side_bbmr(df: pd.DataFrame, bb_period: int, bb_std: float, regime_thr: float) -> pd.Series:
    m = df["close"].rolling(bb_period).mean()
    sd = df["close"].rolling(bb_period).std(ddof=0)
    u, l = m + bb_std*sd, m - bb_std*sd
    pct_b = (df["close"] - l) / (u - l)
    regime_range = (df["EMA50"] - df["EMA200"]).abs() / df["close"] < regime_thr
    long_sig  = (pct_b < 0.05) & regime_range
    short_sig = (pct_b > 0.95) & regime_range
    return pd.Series(np.where(long_sig,"LONG",np.where(short_sig,"SHORT","")), index=df.index)

def compute_entry_tp_sl(df: pd.DataFrame, side_series: pd.Series,
                        tp_atr: float, sl_atr: float) -> Dict[str, Any]:
    """
    Devuelve dict con señal de la ÚLTIMA vela (entrada en open de la próxima).
    Si no hay señal, retorna side=NO_TRADE.
    """
    if side_series.empty:
        return {"side":"NO_TRADE"}

    last_idx = side_series.index[-1]
    side = side_series.iloc[-1]
    if side == "" or side is None:
        return {"side":"NO_TRADE"}

    # Entrada next bar open si existe
    df_idx = df.index
    pos = df_idx.get_indexer_for([last_idx])[0]
    if pos+1 >= len(df):
        return {"side":"NO_TRADE"}  # no tenemos la siguiente vela

    entry_time = df_idx[pos+1]
    raw_entry  = float(df["open"].iloc[pos+1])

    # aplicar costes a la entrada
    if side == "LONG":
        entry = raw_entry * (1 + SLIPPAGE_PCT_PER_SIDE) * (1 + COMMISSION_PCT_PER_SIDE)
    else:
        entry = raw_entry * (1 - SLIPPAGE_PCT_PER_SIDE) * (1 - COMMISSION_PCT_PER_SIDE)

    atr = float(df["ATR"].iloc[pos])  # ATR de la vela que generó la señal
    if not (np.isfinite(atr) and atr > 0):
        return {"side":"NO_TRADE"}

    if side == "LONG":
        tp = entry + tp_atr * atr
        sl = entry - sl_atr * atr
    else:
        tp = entry - tp_atr * atr
        sl = entry + sl_atr * atr

    return {
        "ts_signal": str(last_idx),
        "ts_entry": str(entry_time),
        "side": side,
        "entry_price": entry,
        "tp_price": tp,
        "sl_price": sl,
    }

def load_registry(path="registry/strategies.yaml") -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    strategies = data.get("strategies", [])
    return [s for s in strategies if s.get("status") in ("active","experimental")]

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_latest = os.path.join(RESULTS_DIR, "live_signals.csv")
    out_run    = os.path.join(RESULTS_DIR, RUN_ID)
    os.makedirs(out_run, exist_ok=True)
    out_run = os.path.join(out_run, "live_signals.csv")

    rows = []
    for s in load_registry():
        symbol = s["symbol"]; tf = s["timeframe"]; kind = s["kind"]; p = s["params"]
        df = load_dataset(symbol, tf)
        df = ensure_features(df)

        if kind == "ma_cross":
            side_series = side_ma_cross(df, p["fast"], p["slow"])
        elif kind == "donchian":
            side_series = side_donchian(df, p["n"], p["atr_pct_min"])
        elif kind == "bbmr":
            side_series = side_bbmr(df, p["bb_period"], p["bb_std"], p["regime_thr"])
        else:
            print(f"[live] Estrategia desconocida: {kind}")
            continue

        sig = compute_entry_tp_sl(df, side_series, p["tp_atr"], p["sl_atr"])

        row = {
            "run_id": RUN_ID,
            "strategy_id": s["id"],
            "display_name": s["display_name"],
            "risk_label": s.get("risk_label",""),
            "status": s.get("status",""),
            "symbol": symbol,
            "timeframe": tf,
            "side": sig.get("side","NO_TRADE"),
            "entry_price": sig.get("entry_price", np.nan),
            "tp_price": sig.get("tp_price", np.nan),
            "sl_price": sig.get("sl_price", np.nan),
            "ts_signal": sig.get("ts_signal",""),
            "ts_entry": sig.get("ts_entry",""),
        }
        rows.append(row)

    out_df = pd.DataFrame(rows).sort_values(["symbol","timeframe","strategy_id"])
    out_df.to_csv(out_latest, index=False)
    out_df.to_csv(out_run, index=False)
    print(f"[live] Guardado: {out_latest}")
    print(out_df)

if __name__ == "__main__":
    main()
