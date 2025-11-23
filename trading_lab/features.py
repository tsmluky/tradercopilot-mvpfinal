# features.py
import pandas as pd
import numpy as np

def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    up = np.where(delta > 0, delta, 0.0)
    down = np.where(delta < 0, -delta, 0.0)
    roll_up = pd.Series(up, index=close.index).ewm(span=period, adjust=False).mean()
    roll_down = pd.Series(down, index=close.index).ewm(span=period, adjust=False).mean()
    rs = roll_up / (roll_down.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.clip(0, 100).fillna(50.0)

def _macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = _ema(close, fast)
    ema_slow = _ema(close, slow)
    macd = ema_fast - ema_slow
    macd_signal = _ema(macd, signal)
    macd_hist = macd - macd_signal
    return macd, macd_signal, macd_hist

def _atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    atr = tr.ewm(span=period, adjust=False).mean()
    return atr

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # EMAs
    df["ema20"] = _ema(df["close"], 20)
    df["ema50"] = _ema(df["close"], 50)
    df["ema200"] = _ema(df["close"], 200)

    # RSI
    df["rsi"] = _rsi(df["close"], 14)

    # MACD
    macd, macd_signal, macd_hist = _macd(df["close"])
    df["macd"] = macd
    df["macd_signal"] = macd_signal
    df["macd_hist"] = macd_hist

    # Bollinger Bands %
    mid = df["close"].rolling(20).mean()
    std = df["close"].rolling(20).std(ddof=0)
    upper = mid + 2 * std
    lower = mid - 2 * std
    df["bb_percent"] = (df["close"] - lower) / (upper - lower)  # 0..1 aprox
    df["bb_percent"] = df["bb_percent"].clip(0, 1)

    # ATR y % de ATR sobre precio
    df["atr"] = _atr(df, 14)
    df["atr_pct"] = (df["atr"] / df["close"]) * 100.0

    # Volumen
    df["volume_ma20"] = df["volume"].rolling(20).mean()

    # Régimen de tendencia
    df["trend_regime"] = 0
    df.loc[df["ema50"] > df["ema200"], "trend_regime"] = 1
    df.loc[df["ema50"] < df["ema200"], "trend_regime"] = -1

    # Limpieza inicial
    df = df.dropna().copy()
    return df
