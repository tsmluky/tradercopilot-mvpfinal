# score_backtester.py — v3 (robusto a BOM/espacios en cabeceras)
import os, math, argparse
from dataclasses import dataclass
from typing import Tuple, Optional
import numpy as np
import pandas as pd

DEFAULT_DATA_PATH = "data/ADAUSDT_60.csv"
CONFIDENCE_THRESHOLD = 60.0
TIMEOUT_BARS = 48
ATR_LEN = 14
COMMISSION_PCT_PER_SIDE = 0.04  # 0.04% por lado

def sl_mult_from_conf(conf: float) -> float:
    return ((100.0 - conf) / 100.0) * 1.8 + 1.2

def tp_mult_from_conf(conf: float) -> float:
    return (conf / 100.0) * 3.0 + 1.5

from features import add_features
from models.scoring import Scorer

def _clean_headers(cols) -> list[str]:
    cleaned = []
    for c in cols:
        name = str(c)
        # quita BOM, espacios, tabs y lower
        name = name.replace("\ufeff", "").strip().lower()
        cleaned.append(name)
    return cleaned

def _parse_date_col(df: pd.DataFrame) -> pd.DataFrame:
    cols = list(df.columns)
    # orden de preferencia
    keys_main = ["timestamp", "date", "datetime", "time"]
    keys_ms   = ["open_time", "open_time_ms", "close_time", "close_time_ms"]

    for key in keys_main:
        if key in cols:
            s = pd.to_numeric(df[key], errors="coerce") if key == "timestamp" else df[key]
            if key == "timestamp":
                # epoch s vs ms
                if pd.notna(s).any() and pd.Series(s).gt(1e12).any():
                    df[key] = pd.to_datetime(s, unit="ms", errors="coerce")
                else:
                    df[key] = pd.to_datetime(s, unit="s", errors="coerce")
            else:
                df[key] = pd.to_datetime(df[key], errors="coerce")
            df = df.set_index(key).sort_index()
            return df

    for key in keys_ms:
        if key in cols:
            s = pd.to_numeric(df[key], errors="coerce")
            df[key] = pd.to_datetime(s, unit="ms", errors="coerce")
            df = df.set_index(key).sort_index()
            return df

    raise ValueError(
        f"No se encontró columna temporal reconocible. Cabeceras: {list(df.columns)}"
    )

def load_price_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"No existe el archivo: {path}")
    # encoding='utf-8' suele respetar BOM; de todas formas limpiamos
    df = pd.read_csv(path, encoding="utf-8")
    df.columns = _clean_headers(df.columns)

    # mapear fecha
    df = _parse_date_col(df)

    # Validar OHLCV mínimas
    required = {"open", "high", "low", "close", "volume"}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas OHLCV: {missing}. Cabeceras: {list(df.columns)}")
    return df.sort_index()

def guess_symbol_tf_from_filename(path: str) -> Tuple[str, str]:
    base = os.path.basename(path).replace(".csv", "")
    parts = base.split("_")
    if len(parts) >= 2:
        symbol, tf = parts[0], parts[1]
    else:
        symbol, tf = base, "NA"
    return symbol.upper(), tf

@dataclass
class TradeResult:
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    side: str
    entry_price: float
    exit_price: float
    return_pct: float
    result: str
    bars_held: int
    tp_level: float
    sl_level: float
    confidence: float

def simulate_trade(df_slice: pd.DataFrame, side: str, entry_price: float, atr_value: float,
                   conf: float, commission_pct_per_side: float, timeout_bars: int) -> Optional[TradeResult]:
    if df_slice.empty or math.isnan(entry_price) or math.isnan(atr_value):
        return None

    sl_mult = sl_mult_from_conf(conf); tp_mult = tp_mult_from_conf(conf)
    if np.isnan(sl_mult) or np.isnan(tp_mult):
        return None

    if side == "LONG":
        sl_level = entry_price - atr_value * sl_mult
        tp_level = entry_price + atr_value * tp_mult
    else:
        sl_level = entry_price + atr_value * sl_mult
        tp_level = entry_price - atr_value * tp_mult

    for idx, (ts, row) in enumerate(df_slice.iterrows(), start=1):
        high, low, close = float(row["high"]), float(row["low"]), float(row["close"])

        hit_tp = (high >= tp_level) if side == "LONG" else (low <= tp_level)
        hit_sl = (low <= sl_level)  if side == "LONG" else (high >= sl_level)

        def _ret(exit_px):
            gross = (exit_px / entry_price - 1.0) * 100.0 if side == "LONG" else (entry_price / exit_px - 1.0) * 100.0
            return gross - 2 * commission_pct_per_side

        if hit_sl and hit_tp:
            return TradeResult(df_slice.index[0], ts, side, entry_price, sl_level, _ret(sl_level), "loss",
                               idx, tp_level, sl_level, conf)
        if hit_tp:
            return TradeResult(df_slice.index[0], ts, side, entry_price, tp_level, _ret(tp_level), "win",
                               idx, tp_level, sl_level, conf)
        if hit_sl:
            return TradeResult(df_slice.index[0], ts, side, entry_price, sl_level, _ret(sl_level), "loss",
                               idx, tp_level, sl_level, conf)

        if idx >= timeout_bars:
            exit_px = close
            net = _ret(exit_px)
            return TradeResult(df_slice.index[0], ts, side, entry_price, exit_px, net,
                               ("win" if net > 0 else "loss"), idx, tp_level, sl_level, conf)

    # cierre al final si no hubo evento
    ts = df_slice.index[-1]
    exit_px = float(df_slice.iloc[-1]["close"])
    gross = (exit_px / entry_price - 1.0) * 100.0 if side == "LONG" else (entry_price / exit_px - 1.0) * 100.0
    net = gross - 2 * commission_pct_per_side
    return TradeResult(df_slice.index[0], ts, side, entry_price, exit_px, net, ("win" if net > 0 else "loss"),
                       len(df_slice), tp_level, sl_level, conf)

def equity_metrics(returns_pct: np.ndarray) -> dict:
    if returns_pct.size == 0:
        return {"trades": 0, "winrate": 0.0, "avg_return_pct": 0.0, "profit_factor": 0.0,
                "expectancy_pct": 0.0, "max_drawdown_pct": 0.0}
    wins = returns_pct[returns_pct > 0]; losses = returns_pct[returns_pct <= 0]
    gp = wins.sum() if wins.size else 0.0
    gl = -losses.sum() if losses.size else 0.0
    pf = (gp / gl) if gl > 1e-9 else float("inf")
    winrate = (wins.size / returns_pct.size) * 100.0
    expectancy = returns_pct.mean()
    equity = np.cumprod(1.0 + returns_pct / 100.0)
    peak = np.maximum.accumulate(equity)
    dd = (equity / peak - 1.0) * 100.0
    return {"trades": int(returns_pct.size), "winrate": round(float(winrate), 2),
            "avg_return_pct": round(float(expectancy), 3),
            "profit_factor": (round(float(pf), 3) if pf != float("inf") else float("inf")),
            "expectancy_pct": round(float(expectancy), 3),
            "max_drawdown_pct": round(float(dd.min()), 2)}

def run_backtest(data_path: str, threshold: float, timeout_bars: int, commission_pct_per_side: float):
    os.makedirs("results", exist_ok=True)
    df = load_price_csv(data_path)
    df = add_features(df)

    if "atr_pct" in df.columns:
        df["atr_abs"] = df["atr_pct"] * df["close"]
    else:
        tr = np.maximum(df["high"] - df["low"],
                        np.maximum(abs(df["high"] - df["close"].shift(1)),
                                   abs(df["low"] - df["close"].shift(1))))
        df["atr_abs"] = tr.rolling(ATR_LEN, min_periods=1).mean()

    scorer = Scorer()
    scored = scorer.score(df)

    entries = scored[(scored["signal_side"] != "NO_TRADE") & (scored["confidence"] >= threshold)].copy()

    trades = []
    idx_arr = scored.index
    for t in entries.index:
        pos = idx_arr.get_indexer([t], method="nearest")[0]
        next_pos = pos + 1
        if next_pos >= len(idx_arr):
            continue

        side = str(entries.loc[t, "signal_side"])
        conf = float(entries.loc[t, "confidence"])
        entry_time = idx_arr[next_pos]
        entry_price = float(scored.loc[entry_time, "close"])
        atr_value = float(scored.loc[entry_time, "atr_abs"])

        df_slice = scored.iloc[next_pos: next_pos + timeout_bars + 1][["open", "high", "low", "close"]]
        tr = simulate_trade(df_slice, side, entry_price, atr_value, conf, commission_pct_per_side, timeout_bars)
        if tr is not None:
            trades.append(tr)

    trades_df = pd.DataFrame([t.__dict__ for t in trades])
    symbol, tf = guess_symbol_tf_from_filename(data_path)
    metrics = equity_metrics(trades_df["return_pct"].values if not trades_df.empty else np.array([]))
    summary = pd.DataFrame([{ "symbol": symbol, "timeframe": tf, "threshold": threshold,
                              "timeout_bars": timeout_bars, "commission_pct_per_side": commission_pct_per_side, **metrics }])

    trades_path = f"results/score_trades_{symbol}_{tf}.csv"
    summary_path = f"results/score_summary_{symbol}_{tf}.csv"
    trades_df.to_csv(trades_path, index=False)
    summary.to_csv(summary_path, index=False)
    print(f"✅ Guardado: {trades_path}")
    print(f"✅ Guardado: {summary_path}")
    return trades_df, summary

def main():
    print(">> score_backtester v3 — parser robusto de fecha/cabeceras")
    p = argparse.ArgumentParser(description="Backtest de señales por score/confianza.")
    p.add_argument("--data", type=str, default=DEFAULT_DATA_PATH, help="Ruta al CSV de datos (data/...)")
    p.add_argument("--threshold", type=float, default=CONFIDENCE_THRESHOLD, help="Umbral mínimo de confianza (0-100)")
    p.add_argument("--timeout", type=int, default=TIMEOUT_BARS, help="Máximo de barras abiertas por trade")
    p.add_argument("--fee", type=float, default=COMMISSION_PCT_PER_SIDE, help="Comisión % por lado (ej. 0.04)")
    args = p.parse_args()
    run_backtest(args.data, args.threshold, args.timeout, args.fee)

if __name__ == "__main__":
    main()
