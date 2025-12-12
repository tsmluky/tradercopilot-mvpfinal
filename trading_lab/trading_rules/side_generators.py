import pandas as pd
import numpy as np
from .indicators import ema, bollinger

def side_ma_cross(df: pd.DataFrame, fast: int, slow: int) -> pd.Series:
    """
    MA Cross Strategy:
    LONG when fast EMA crosses above slow EMA.
    SHORT when fast EMA crosses below slow EMA.
    """
    close = df["close"]
    f = ema(close, fast)
    s = ema(close, slow)
    
    # Logic: Current Fast > Slow AND Previous Fast <= Slow
    cross_up = (f > s) & (f.shift(1) <= s.shift(1))
    cross_dn = (f < s) & (f.shift(1) >= s.shift(1))
    
    return pd.Series(np.where(cross_up, "LONG", np.where(cross_dn, "SHORT", "")), index=df.index)

def side_donchian(df: pd.DataFrame, n: int, atr_pct_min: float) -> pd.Series:
    """
    Donchian Breakout Strategy (Refined):
    LONG when High > Max(High, n) AND ATR > SMA(ATR, 20) AND Close > EMA200.
    SHORT when Low < Min(Low, n) AND ATR > SMA(ATR, 20) AND Close < EMA200.
    """
    high, low, close = df["high"], df["low"], df["close"]
    
    # Donchian channels
    donch_high = high.rolling(window=n, min_periods=n).max().shift(1)
    donch_low  = low.rolling(window=n, min_periods=n).min().shift(1)
    
    # Volatility Filter: ATR > SMA(ATR, 20)
    atr = df["ATR"]
    atr_ma = atr.rolling(window=20).mean()
    volatility_ok = atr > atr_ma

    # Trend Filter: EMA200
    # Ensure EMA200 exists in DF, otherwise skip or calculate
    if "EMA200" in df.columns:
        ema200 = df["EMA200"]
        trend_up = close > ema200
        trend_dn = close < ema200
    else:
        # Fallback if not pre-calculated
        ema200 = close.ewm(span=200, adjust=False).mean()
        trend_up = close > ema200
        trend_dn = close < ema200
    
    long_sig  = (high > donch_high) & volatility_ok & trend_up
    short_sig = (low  < donch_low)  & volatility_ok & trend_dn
    
    return pd.Series(np.where(long_sig, "LONG", np.where(short_sig, "SHORT", "")), index=df.index)

def side_bbmr(df: pd.DataFrame, bb_period: int, bb_std: float, regime_thr: float) -> pd.Series:
    """
    Bollinger Mean Reversion Strategy:
    LONG when %B < 0.05 (oversold) AND Trend Strength is weak.
    SHORT when %B > 0.95 (overbought) AND Trend Strength is weak.
    Trend Strength defined as |EMA50 - EMA200| / Close < regime_thr.
    """
    mid, upper, lower = bollinger(df["close"], bb_period, bb_std)
    
    # %B Indicator
    pct_b = (df["close"] - lower) / (upper - lower)
    
    # Regime: Ranging (weak trend)
    trend_strength = (df["EMA50"] - df["EMA200"]).abs() / df["close"]
    regime_range = trend_strength < regime_thr
    
    long_sig  = (pct_b < 0.05) & regime_range
    short_sig = (pct_b > 0.95) & regime_range
    
    return pd.Series(np.where(long_sig, "LONG", np.where(short_sig, "SHORT", "")), index=df.index)
