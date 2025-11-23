# models/scoring.py
# Scoring robusto con fallback: combina YAML parcial con defaults para evitar KeyError.

import os
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd

try:
    import yaml  # opcional
except Exception:
    yaml = None

DEFAULT_WEIGHTS = {
    "ema200_trend": 30,
    "ema50_trend": 20,
    "macd_hist": 20,
    "rsi_mid": 10,
    "rsi_extremes": 20,
}

DEFAULT_THRESHOLDS = {
    "long_confidence": 60,
    "short_confidence": 60,
}

DEFAULT_TP_MULT = 1.5
DEFAULT_SL_MULT = 1.0

def _load_yaml(path: str) -> Optional[Dict[str, Any]]:
    if not os.path.exists(path) or yaml is None:
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0.0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
    rs = gain / (loss.replace(0, np.nan))
    out = 100 - (100 / (1 + rs))
    return out.fillna(50)

def macd(series: pd.Series, fast=12, slow=26, signal=9):
    ema_f = ema(series, fast)
    ema_s = ema(series, slow)
    macd_line = ema_f - ema_s
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def ensure_core_indicators(df: pd.DataFrame) -> pd.DataFrame:
    # ATR(14)
    if "ATR" not in df.columns:
        high, low, close = df["high"], df["low"], df["close"]
        tr = pd.concat([(high - low).abs(),
                        (high - close.shift(1)).abs(),
                        (low - close.shift(1)).abs()], axis=1).max(axis=1)
        df["ATR"] = tr.ewm(alpha=1/14, adjust=False).mean()

    if "EMA50" not in df.columns:
        df["EMA50"] = ema(df["close"], 50)
    if "EMA200" not in df.columns:
        df["EMA200"] = ema(df["close"], 200)

    if "RSI" not in df.columns:
        df["RSI"] = rsi(df["close"], 14)

    if "MACD_HIST" not in df.columns:
        macd_line, signal_line, hist = macd(df["close"])
        df["MACD"] = macd_line
        df["MACD_SIGNAL"] = signal_line
        df["MACD_HIST"] = hist

    return df

def _merge_cfg(cfg: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    cfg = cfg or {}
    user_w = cfg.get("weights", {}) or {}
    user_thr = cfg.get("thresholds", {}) or {}

    weights = {**DEFAULT_WEIGHTS, **user_w}
    thresholds = {**DEFAULT_THRESHOLDS, **user_thr}

    tp_mult = cfg.get("tp_atr_mult", DEFAULT_TP_MULT)
    sl_mult = cfg.get("sl_atr_mult", DEFAULT_SL_MULT)

    return {"weights": weights, "thresholds": thresholds,
            "tp_atr_mult": tp_mult, "sl_atr_mult": sl_mult}

def _score_row(row, cfg):
    w = cfg["weights"]
    thr = cfg["thresholds"]
    tp_mult = cfg["tp_atr_mult"]
    sl_mult = cfg["sl_atr_mult"]

    # Protecciones por si hay NaNs al inicio
    price = float(row["close"])
    ema50 = float(row.get("EMA50", np.nan))
    ema200 = float(row.get("EMA200", np.nan))
    rsi_val = float(row.get("RSI", 50.0))
    hist = float(row.get("MACD_HIST", 0.0))
    atr = float(row.get("ATR", 0.0))
    if not np.isfinite(atr) or atr <= 0:
        atr = 1e-9  # evita divisiones raras

    long_score = 0
    short_score = 0

    # Tendencia vs EMA200 / EMA50
    if np.isfinite(ema200):
        if price > ema200:
            long_score += w["ema200_trend"]
        else:
            short_score += w["ema200_trend"]

    if np.isfinite(ema50):
        if price > ema50:
            long_score += w["ema50_trend"]
        else:
            short_score += w["ema50_trend"]

    # Momentum MACD (histograma)
    if np.isfinite(hist):
        if hist > 0:
            long_score += w["macd_hist"]
        else:
            short_score += w["macd_hist"]

    # RSI zona media (continuidad)
    if 45 <= rsi_val <= 60:
        long_score += w["rsi_mid"]

    # RSI extremos (riesgo de reversión → favorece prudencia en largos,
    # o entradas contrarias sólo si hay tendencia clara; mantenemos sencillo)
    if rsi_val < 30 or rsi_val > 70:
        short_score += w["rsi_extremes"]

    # Decisión y niveles TP/SL por ATR
    if long_score >= short_score:
        confidence = long_score
        side = "LONG" if confidence >= thr["long_confidence"] else "NO_TRADE"
        tp = price + tp_mult * atr
        sl = price - sl_mult * atr
    else:
        confidence = short_score
        side = "SHORT" if confidence >= thr["short_confidence"] else "NO_TRADE"
        tp = price - tp_mult * atr
        sl = price + sl_mult * atr

    return long_score, short_score, confidence, side, tp, sl

def score_signals(df: pd.DataFrame, symbol: str = "", timeframe: str = "") -> pd.DataFrame:
    raw_cfg = _load_yaml("scoring_config.yaml")
    cfg = _merge_cfg(raw_cfg)
    df = ensure_core_indicators(df)

    outs = []
    for _, row in df.iterrows():
        ls, ss, conf, side, tp, sl = _score_row(row, cfg)
        outs.append((ls, ss, conf, side, tp, sl))

    df["score_long"] = [o[0] for o in outs]
    df["score_short"] = [o[1] for o in outs]
    df["confidence"] = [o[2] for o in outs]
    df["signal_side"] = [o[3] for o in outs]
    df["tp_price"] = [o[4] for o in outs]
    df["sl_price"] = [o[5] for o in outs]
    df["symbol"] = symbol
    df["timeframe"] = timeframe
    return df
