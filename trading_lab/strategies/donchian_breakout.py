# strategies/donchian_breakout.py
import numpy as np
import pandas as pd

def generate_signals(df: pd.DataFrame, n: int = 20, atr_pct_min: float = 0.005) -> pd.Series:
    high = df["high"]; low = df["low"]; close = df["close"]
    donch_high = high.rolling(window=n, min_periods=n).max().shift(1)
    donch_low  = low.rolling(window=n, min_periods=n).min().shift(1)
    atr_pct = (df["ATR"] / close).fillna(0.0)

    regime_up = close > df["EMA200"]
    regime_dn = close < df["EMA200"]

    long_sig  = (high > donch_high) & (atr_pct >= atr_pct_min) & regime_up
    short_sig = (low  < donch_low)  & (atr_pct >= atr_pct_min) & regime_dn

    side = np.where(long_sig, "LONG", np.where(short_sig, "SHORT", ""))
    return pd.Series(side, index=df.index, name="side")
