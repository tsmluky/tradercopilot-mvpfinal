# engine.py
# Backtest con entrada next-bar-open, no-overlap, costes por lado en ejecución,
# logs versionados por RUN_ID y métricas ampliadas + equity curves.
#
# UPDATED: Uses backend.strategies.base.Strategy classes!

import os, math, json, sys
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
from pathlib import Path

import numpy as np
import pandas as pd

# Add backend to path to import strategies
current_dir = Path(__file__).parent
backend_dir = current_dir.parent / "backend"
sys.path.insert(0, str(backend_dir))

from strategies.ma_cross import MACrossStrategy
from strategies.donchian import DonchianStrategy
from strategies.bb_mean_reversion import BBMeanReversionStrategy
from core.schemas import Signal

# ==== CONFIG ====
DATASETS_DIR = "datasets"
RESULTS_DIR  = "results"
LOGS_DIR     = "logs"

# Trabajamos ETH + SOL
SYMBOLS    = ["ETHUSDT", "SOLUSDT"]
TIMEFRAMES = ["15m", "1h", "4h", "1d"]

# Costes por lado (entrada y salida)
COMMISSION_PCT_PER_SIDE = 0.04 / 100.0  # 0.04% por lado
SLIPPAGE_PCT_PER_SIDE   = 0.02 / 100.0  # 0.02% por lado

# Fast mode
FAST_MODE = True
FAST_TAIL = 5000

# Scoring opcional
GENERATE_SCORED_SIGNALS = True

# Estrategias (Instancias de clases)
STRATEGIES = [
    MACrossStrategy(config={"fast_period": 10, "slow_period": 50, "tp_atr_mult": 1.5, "sl_atr_mult": 1.0, "bars_timeout": 48}),
    MACrossStrategy(config={"fast_period": 20, "slow_period": 50, "tp_atr_mult": 1.5, "sl_atr_mult": 1.0, "bars_timeout": 48}),
    DonchianStrategy(config={"period": 20, "atr_pct_min": 0.005, "tp_atr_mult": 1.8, "sl_atr_mult": 1.0}),
    BBMeanReversionStrategy(config={"bb_period": 20, "bb_std": 2.0, "regime_thr": 0.01, "tp_atr_mult": 1.2, "sl_atr_mult": 0.8}),
]
# ==============

RUN_ID = datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%M%S")

def ensure_dirs():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(os.path.join(RESULTS_DIR, RUN_ID), exist_ok=True)
    os.makedirs(os.path.join(LOGS_DIR, RUN_ID), exist_ok=True)

def _infer_time_col(df: pd.DataFrame) -> str:
    for c in ["timestamp", "time", "date", "datetime", "open_time"]:
        if c in df.columns: return c
    return ""

def load_dataset(symbol: str, timeframe: str) -> pd.DataFrame:
    path = os.path.join(DATASETS_DIR, f"{symbol}_{timeframe}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No existe dataset: {path}")
    df = pd.read_csv(path)

    tcol = _infer_time_col(df)
    if tcol:
        df[tcol] = pd.to_datetime(df[tcol], utc=True, errors="coerce")
        df = df.dropna(subset=[tcol]).sort_values(tcol).set_index(tcol)

    # Normaliza columnas OHLCV
    cols_lower = [c.lower() for c in df.columns]
    mapping = {}
    for k in ["open","high","low","close","volume"]:
        if k in cols_lower:
            mapping[k] = df.columns[cols_lower.index(k)]
    for std, real in mapping.items():
        if std != real:
            df[std] = df[real]
    for k in ["open","high","low","close"]:
        if k not in df.columns:
            raise ValueError(f"Falta columna requerida: {k}")

    if FAST_MODE and len(df) > FAST_TAIL:
        df = df.tail(FAST_TAIL)
    return df

# ---------- Simulador secuencial (next-open, no-overlap) ----------
class Trade:
    __slots__ = ("entry_time","exit_time","side","entry_price","exit_price",
                 "return_pct_net","return_pct_gross","result","bars_held",
                 "tp_level","sl_level","confidence","R",
                 "commission_pct_per_side","slippage_pct_per_side")
    def __init__(self, **k):
        for a in self.__slots__:
            setattr(self, a, k.get(a))

def simulate_signals(df: pd.DataFrame,
                     signals: List[Signal],
                     timeout_bars: int = 48, # Default timeout if not in signal
                     commission: float = 0.0004,
                     slippage: float = 0.0002,
                     adverse_first: bool = True) -> List[Trade]:
    """
    Simula trades a partir de una lista de objetos Signal.
    """
    trades: List[Trade] = []
    
    # Convertir señales a un dict indexado por timestamp para acceso rápido
    # O mejor, iterar cronológicamente.
    # Asumimos que signals están ordenadas por timestamp.
    signals.sort(key=lambda s: s.timestamp)
    
    # Mapa de timestamp -> indice en df
    ts_to_idx = {ts: i for i, ts in enumerate(df.index)}
    
    last_exit_idx = -1
    N = len(df)
    
    for sig in signals:
        # Buscar índice de la señal
        # Nota: sig.timestamp debe coincidir con el índice del df.
        # Si el df tiene índice timezone-aware, sig.timestamp también debe serlo.
        # Aseguramos compatibilidad de zona horaria
        sig_ts = sig.timestamp
        if df.index.tz is not None and sig_ts.tzinfo is None:
             sig_ts = sig_ts.replace(tzinfo=timezone.utc)
        
        if sig_ts not in ts_to_idx:
            continue
            
        i = ts_to_idx[sig_ts]
        
        # No overlap logic
        if i <= last_exit_idx:
            continue
            
        # Entrada en apertura de la próxima vela
        entry_idx = i + 1
        if entry_idx >= N:
            break
            
        entry_time = df.index[entry_idx]
        entry_price_raw = float(df["open"].iloc[entry_idx])
        
        side = sig.direction.upper()
        
        # Aplicamos costes de ENTRADA
        entry_price = entry_price_raw * (1 + slippage) * (1 + commission) if side == "LONG" \
                      else entry_price_raw * (1 - slippage) * (1 - commission)
                      
        tp_level = sig.tp
        sl_level = sig.sl
        
        # Si la señal no trae TP/SL (raro en nuestras estrategias), fallback
        if not tp_level or not sl_level:
             continue # Skip signals without TP/SL for now
             
        exit_time = None; exit_price = None; result = None; bars_held = None
        
        # Recorremos barra a barra
        # Usamos timeout de la config de la estrategia si existe, sino default
        # En Signal no guardamos timeout explícito, así que usamos el param de la función
        # O podríamos guardarlo en extra.
        
        for fwd in range(1, timeout_bars + 1):
            j = entry_idx + fwd
            if j >= N: break
            h, l = float(df["high"].iloc[j]), float(df["low"].iloc[j])
            
            hit_tp = (h >= tp_level) if side == "LONG" else (l <= tp_level)
            hit_sl = (l <= sl_level) if side == "LONG" else (h >= sl_level)
            
            if adverse_first:
                if hit_sl:
                    raw = sl_level
                    exit_price = raw * (1 - slippage) * (1 - commission) if side == "LONG" \
                                 else raw * (1 + slippage) * (1 + commission)
                    exit_time = df.index[j]; result = "loss"; bars_held = j - entry_idx
                    break
                if hit_tp:
                    raw = tp_level
                    exit_price = raw * (1 - slippage) * (1 - commission) if side == "LONG" \
                                 else raw * (1 + slippage) * (1 + commission)
                    exit_time = df.index[j]; result = "win"; bars_held = j - entry_idx
                    break
            else:
                if hit_tp:
                    raw = tp_level
                    exit_price = raw * (1 - slippage) * (1 - commission) if side == "LONG" \
                                 else raw * (1 + slippage) * (1 + commission)
                    exit_time = df.index[j]; result = "win"; bars_held = j - entry_idx
                    break
                if hit_sl:
                    raw = sl_level
                    exit_price = raw * (1 - slippage) * (1 - commission) if side == "LONG" \
                                 else raw * (1 + slippage) * (1 + commission)
                    exit_time = df.index[j]; result = "loss"; bars_held = j - entry_idx
                    break
                    
        # Timeout
        if exit_time is None:
            j = min(entry_idx + timeout_bars, N - 1)
            raw = float(df["close"].iloc[j])
            exit_price = raw * (1 - slippage) * (1 - commission) if side == "LONG" \
                         else raw * (1 + slippage) * (1 + commission)
            exit_time = df.index[j]
            pnl = (exit_price - entry_price) if side == "LONG" else (entry_price - exit_price)
            result = "win" if pnl > 0 else ("loss" if pnl < 0 else "breakeven")
            bars_held = j - entry_idx
            
        gross_ret = ((exit_price - entry_price) / entry_price) * (1 if side == "LONG" else -1) * 100.0
        net_ret = gross_ret # Costes ya en precio
        
        risk_per_unit = abs(entry_price - sl_level)
        R = (abs(exit_price - entry_price) / risk_per_unit) if risk_per_unit > 0 else np.nan
        if (side == "LONG" and exit_price < entry_price) or (side == "SHORT" and exit_price > entry_price):
            R = -R
            
        trades.append(Trade(
            entry_time=entry_time, exit_time=exit_time, side=side,
            entry_price=entry_price, exit_price=exit_price,
            return_pct_net=net_ret, return_pct_gross=gross_ret,
            result=result, bars_held=bars_held,
            tp_level=tp_level, sl_level=sl_level, confidence=sig.confidence or 100.0, R=R,
            commission_pct_per_side=commission*100.0, slippage_pct_per_side=slippage*100.0
        ))
        
        last_exit_idx = j
        
    return trades

# ---------- Métricas ----------
def _streaks(returns: pd.Series) -> Tuple[int,int]:
    wins = (returns > 0).astype(int)
    max_win = max_loss = curr = curr_sign = 0
    for x in wins:
        if x == curr_sign:
            curr += 1
        else:
            max_win = max(max_win, curr) if curr_sign == 1 else max_win
            max_loss = max(max_loss, curr) if curr_sign == 0 else max_loss
            curr = 1; curr_sign = x
    max_win = max(max_win, curr) if curr_sign == 1 else max_win
    max_loss = max(max_loss, curr) if curr_sign == 0 else max_loss
    return max_win, max_loss

def compute_metrics(log_df: pd.DataFrame, df_len: int) -> Dict[str, float]:
    rets = log_df["return_pct_net"].fillna(0.0)
    n = len(rets)
    wins = rets[rets > 0].sum()
    losses = rets[rets < 0].sum()
    profit_factor = (wins / abs(losses)) if losses < 0 else (np.inf if wins > 0 else 0.0)
    expectancy = rets.mean()
    # Equity (por trade)
    eq = (1.0 + (rets / 100.0)).cumprod()
    roll_max = eq.cummax()
    dd = (eq/roll_max) - 1.0
    max_dd_pct = dd.min() * 100.0
    total_return_pct = (eq.iloc[-1] - 1.0) * 100.0 if n > 0 else 0.0
    # Sharpe / Sortino por trade (simple)
    r = rets / 100.0
    sharpe = (r.mean() / (r.std(ddof=0) + 1e-9)) * np.sqrt(max(n,1))
    downside = r[r < 0]
    sortino = (r.mean() / (downside.std(ddof=0) + 1e-9)) * np.sqrt(max(n,1))
    # Exposición (aprox): barras totales en mercado / barras totales del dataset
    exposure = (log_df["bars_held"].sum() / max(df_len,1)) * 100.0
    # Streaks
    sw, sl = _streaks(rets)
    return {
        "trades": int(n),
        "winrate": float((rets > 0).mean() * 100.0),
        "avg_return_pct_net": float(expectancy),
        "profit_factor": float(profit_factor if np.isfinite(profit_factor) else 0.0),
        "expectancy_pct": float(expectancy),
        "max_drawdown_pct": float(max_dd_pct),
        "total_return_pct": float(total_return_pct),
        "sharpe_trades": float(sharpe),
        "sortino_trades": float(sortino),
        "exposure_pct": float(exposure),
        "max_win_streak": int(sw),
        "max_loss_streak": int(sl),
    }

def run_strategy_simulation(df: pd.DataFrame, symbol: str, timeframe: str, strategy) -> Tuple[pd.DataFrame, Dict]:
    meta = strategy.metadata()
    name = meta.name
    kind = meta.id
    
    # 1. Generar señales usando la clase Strategy
    # analyze devuelve List[Signal]
    signals = strategy.analyze(df, symbol, timeframe)
    
    # 2. Simular trades
    # Extraer timeout de config si existe
    timeout = strategy.config.get("bars_timeout", 48)
    
    trades = simulate_signals(
        df, signals,
        timeout_bars=timeout,
        commission=COMMISSION_PCT_PER_SIDE,
        slippage=SLIPPAGE_PCT_PER_SIDE,
        adverse_first=True
    )
    
    if not trades:
        return pd.DataFrame(), {
            "symbol": symbol, "timeframe": timeframe, "strategy": name, "kind": kind,
            "trades": 0, "winrate": 0.0, "avg_return_pct_net": 0.0,
            "profit_factor": 0.0, "expectancy_pct": 0.0,
            "max_drawdown_pct": 0.0, "total_return_pct": 0.0,
            "sharpe_trades": 0.0, "sortino_trades": 0.0, "exposure_pct": 0.0,
            "max_win_streak": 0, "max_loss_streak": 0
        }

    log_rows = [{
        "entry_time": t.entry_time, "exit_time": t.exit_time, "side": t.side,
        "entry_price": t.entry_price, "exit_price": t.exit_price,
        "return_pct_gross": t.return_pct_gross, "return_pct_net": t.return_pct_net,
        "result": t.result, "bars_held": t.bars_held, "tp_level": t.tp_level, "sl_level": t.sl_level,
        "confidence": t.confidence, "R": t.R,
        "commission_pct_per_side": t.commission_pct_per_side, "slippage_pct_per_side": t.slippage_pct_per_side,
        "strategy": name, "kind": kind, "symbol": symbol, "timeframe": timeframe
    } for t in trades]
    log_df = pd.DataFrame(log_rows)

    # Guardar logs (latest + por RUN_ID)
    base = f"{symbol}_{kind}_{timeframe}.csv"
    log_df.to_csv(os.path.join(LOGS_DIR, base), index=False)
    log_df.to_csv(os.path.join(LOGS_DIR, RUN_ID, base), index=False)

    # Equity curve por trade (net)
    eq = (1.0 + (log_df["return_pct_net"].fillna(0.0) / 100.0)).cumprod()
    eq_df = pd.DataFrame({"trade_idx": np.arange(len(eq)), "equity": eq})
    eq_base = f"equity_{symbol}_{kind}_{timeframe}.csv"
    eq_df.to_csv(os.path.join(RESULTS_DIR, eq_base), index=False)
    eq_df.to_csv(os.path.join(RESULTS_DIR, RUN_ID, eq_base), index=False)

    metrics = compute_metrics(log_df, df_len=len(df))
    metrics.update({"symbol": symbol, "timeframe": timeframe, "strategy": name, "kind": kind})
    return log_df, metrics

def append_summary(rows: List[Dict]):
    df = pd.DataFrame(rows)
    # summary latest + por RUN_ID
    df.to_csv(os.path.join(RESULTS_DIR, "summary.csv"), index=False)
    df.to_csv(os.path.join(RESULTS_DIR, RUN_ID, "summary.csv"), index=False)

def main():
    ensure_dirs()

    # opcional scoring
    if GENERATE_SCORED_SIGNALS:
        try:
            from models import scoring as scoring_mod
        except Exception as e:
            scoring_mod = None
            print(f"[engine] WARN: scoring no disponible → {e}")

    all_metrics = []

    for symbol in SYMBOLS:
        for tf in TIMEFRAMES:
            print(f"[engine] ▶ {symbol} @ {tf}")
            try:
                df = load_dataset(symbol, tf)
            except FileNotFoundError:
                print(f"  ⚠️ Dataset not found: {symbol} {tf}")
                continue
                
            # scored_signals (latest + por RUN_ID)
            if GENERATE_SCORED_SIGNALS and scoring_mod is not None:
                try:
                    scored = scoring_mod.score_signals(df.copy(), symbol=symbol, timeframe=tf)
                    base = f"scored_signals_{symbol}_{tf}.csv"
                    scored.to_csv(os.path.join(RESULTS_DIR, base), index=True)
                    scored.to_csv(os.path.join(RESULTS_DIR, RUN_ID, base), index=True)
                    print(f"[engine] scored_signals guardado: results\\{base}")
                except Exception as e:
                    print(f"[engine] WARN: fallo score_signals → {e}")

            for strat in STRATEGIES:
                _, m = run_strategy_simulation(df, symbol, tf, strat)
                all_metrics.append(m)
                print(f"  - {m['strategy']}: trades={m['trades']} PF={m['profit_factor']:.2f} "
                      f"WR={m['winrate']:.1f}% Ret={m['total_return_pct']:.1f}% "
                      f"DD={m['max_drawdown_pct']:.1f}% Sh={m['sharpe_trades']:.2f}")

    append_summary(all_metrics)
    print(f"[engine] Summary escrito en results\\summary.csv y results\\{RUN_ID}\\summary.csv")

if __name__ == "__main__":
    main()
