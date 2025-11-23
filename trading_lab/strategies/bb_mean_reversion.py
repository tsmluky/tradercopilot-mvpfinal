# strategies/bb_mean_reversion.py
import numpy as np
import pandas as pd

def bollinger(df: pd.DataFrame, period: int=20, stds: float=2.0):
    m = df["close"].rolling(period).mean()
    sd = df["close"].rolling(period).std(ddof=0)
    upper = m + stds * sd
    lower = m - stds * sd
    return m, upper, lower

def generate_signals(df: pd.DataFrame, bb_period: int=20, bb_std: float=2.0, regime_thr: float=0.01) -> pd.Series:
    m, u, l = bollinger(df, bb_period, bb_std)
    pct_b = (df["close"] - l) / (u - l)
    regime_range = (df["EMA50"] - df["EMA200"]).abs() / df["close"] < regime_thr

    long_sig  = (pct_b < 0.05) & regime_range
    short_sig = (pct_b > 0.95) & regime_range

    side = np.where(long_sig, "LONG", np.where(short_sig, "SHORT", ""))
    return pd.Series(side, index=df.index, name="side")
