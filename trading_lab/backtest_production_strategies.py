import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Ensure we can import from demo_execution and core
sys.path.append(os.path.join(os.getcwd(), "demo_execution"))
sys.path.append(os.getcwd())

from demo_execution.strategies.implementations.trend_ma_strategy import TrendMaCrossStrategy
from demo_execution.strategies.implementations.donchian_strategy import DonchianBreakoutStrategy
from trading_rules.indicators import ensure_features
from trading_rules.side_generators import side_ma_cross, side_donchian
from trading_rules.signal_builder import compute_entry_tp_sl

# --- Backtest Engine Helpers ---

def load_data(symbol: str, timeframe: str = "60") -> pd.DataFrame:
    """Loads data from data/ directory."""
    path = f"data/{symbol}_{timeframe}.csv"
    if not os.path.exists(path):
        print(f"❌ Data not found: {path}")
        return pd.DataFrame()
    
    df = pd.read_csv(path)
    
    # Normalize columns
    df.columns = [c.lower() for c in df.columns]
    
    # Parse timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        df = df.sort_values("timestamp").set_index("timestamp")
    
    return df

def evaluate_signals_vectorized(df: pd.DataFrame, signals: pd.DataFrame, tp_atr: float, sl_atr: float) -> pd.DataFrame:
    """
    Simple vectorized evaluation of signals.
    Iterates through signals and checks future price action in df.
    """
    results = []
    
    # Pre-calculate high/low arrays for speed if needed, but simple loop is fine for <10k signals
    # We need to find the signal time in df
    
    for idx, row in signals.iterrows():
        sig_time = row["ts_signal"]
        if sig_time not in df.index:
            continue
            
        # Start checking from NEXT candle
        start_pos = df.index.get_loc(sig_time) + 1
        if start_pos >= len(df):
            continue
            
        entry_price = row["entry_price"]
        tp = row["tp_price"]
        sl = row["sl_price"]
        side = row["side"]
        
        outcome = "TIMEOUT"
        exit_price = df.iloc[-1]["close"]
        bars_held = 0
        
        # Look ahead up to 100 bars (or timeout)
        LIMIT_BARS = 100
        
        future_df = df.iloc[start_pos : start_pos + LIMIT_BARS]
        
        for i, candle in enumerate(future_df.itertuples()):
            bars_held = i + 1
            if side == "LONG":
                if candle.low <= sl:
                    outcome = "LOSS"
                    exit_price = sl
                    break
                if candle.high >= tp:
                    outcome = "WIN"
                    exit_price = tp
                    break
            else: # SHORT
                if candle.high >= sl:
                    outcome = "LOSS"
                    exit_price = sl
                    break
                if candle.low <= tp:
                    outcome = "WIN"
                    exit_price = tp
                    break
        
        pnl = 0.0
        if side == "LONG":
            pnl = (exit_price - entry_price) / entry_price
        else:
            pnl = (entry_price - exit_price) / entry_price
            
        results.append({
            "signal_idx": idx,
            "outcome": outcome,
            "pnl": pnl,
            "bars_held": bars_held,
            "exit_price": exit_price
        })
        
    return pd.DataFrame(results)

def run_full_backtest(strategy_cls, symbol="ETHUSDT", timeframe="60"):
    print(f"\n🔬 Backtesting {strategy_cls.name} on {symbol} ({timeframe}m)...")
    
    # 1. Load Data
    df = load_data(symbol, timeframe)
    if df.empty:
        return
    
    print(f"   Loaded {len(df)} candles.")
    
    # 2. Prepare Features (Using Production Logic)
    df = ensure_features(df)
    
    # 3. Generate Signals (Using Production Logic)
    strat = strategy_cls()
    params = strat.default_params
    
    print(f"   Applying rules with params: {params}")
    
    if isinstance(strat, TrendMaCrossStrategy):
        side_series = side_ma_cross(df, params["fast"], params["slow"])
    elif isinstance(strat, DonchianBreakoutStrategy):
        side_series = side_donchian(df, params["n"], params["atr_pct_min"])
    else:
        print("   Strategy type not supported for auto-backtest.")
        return

    # 4. Extract Signals
    # The 'side_series' has LONG/SHORT on the candle where the condition is met.
    # We need to turn this into a list of discrete signals.
    # We only take the FIRST signal of a sequence or allow re-entry? 
    # For simplicity, we take every transition to non-empty.
    
    signal_rows = []
    
    # Detect changes to avoid repeating LONG LONG LONG
    # shift(1) != current
    is_change = side_series != side_series.shift(1)
    is_signal = (side_series != "") & (side_series != "NO_TRADE") & is_change
    
    signal_indices = df.index[is_signal]
    
    print(f"   Found {len(signal_indices)} raw signal events.")
    
    for ts in signal_indices:
        # Slice df up to this point to simulate "live" call to signal_builder
        # Actually signal_builder just needs the row, but let's be precise
        # We construct a row dict
        
        idx_loc = df.index.get_loc(ts)
        row_slice = df.iloc[idx_loc] # The signal candle
        
        # We need to pass a mini-df or just use the logic manually?
        # compute_entry_tp_sl expects a DF and side_series.
        # It uses the LAST row.
        
        # Optimization: We can just calculate entry/tp/sl for this row manually using the helper
        # But to reuse code, let's pass a 1-row df? No, indicators need history.
        # We already have the full DF with ATR.
        
        # Let's just use the logic from compute_entry_tp_sl but applied to this specific row
        # Re-implementing lightly for speed:
        
        side = side_series.loc[ts]
        close = row_slice["close"]
        atr = row_slice["ATR"]
        
        # Entry is next open (approximated by close here or we look ahead)
        # Let's use Close for simplicity as per previous logic
        entry_price = close 
        
        tp_atr = params["tp_atr"]
        sl_atr = params["sl_atr"]
        
        if side == "LONG":
            tp = entry_price + tp_atr * atr
            sl = entry_price - sl_atr * atr
        else:
            tp = entry_price - tp_atr * atr
            sl = entry_price + sl_atr * atr
            
        signal_rows.append({
            "ts_signal": ts,
            "side": side,
            "entry_price": entry_price,
            "tp_price": tp,
            "sl_price": sl
        })
        
    if not signal_rows:
        print("   No signals generated.")
        return

    signals_df = pd.DataFrame(signal_rows)
    
    # 5. Evaluate
    eval_df = evaluate_signals_vectorized(df, signals_df, params["tp_atr"], params["sl_atr"])
    
    if eval_df.empty:
        print("   Could not evaluate signals (end of data?).")
        return

    # 6. Merge and Report
    full_results = signals_df.join(eval_df.set_index("signal_idx"))
    full_results = full_results.dropna(subset=["outcome"])
    
    wins = full_results[full_results["outcome"] == "WIN"]
    losses = full_results[full_results["outcome"] == "LOSS"]
    
    winrate = len(wins) / len(full_results) * 100
    total_pnl = full_results["pnl"].sum() * 100
    
    print("\n📊 PERFORMANCE REPORT")
    print(f"   Strategy: {strategy_cls.name}")
    print(f"   Total Trades: {len(full_results)}")
    print(f"   Win Rate:     {winrate:.2f}%")
    print(f"   Total PnL:    {total_pnl:.2f}% (uncompounded)")
    print(f"   Avg PnL/Trade:{full_results['pnl'].mean()*100:.2f}%")
    
    # Save to CSV
    fname = f"backtest_results_{strategy_cls.id}_{symbol}.csv"
    full_results.to_csv(fname)
    print(f"   Detailed log saved to: {fname}")

if __name__ == "__main__":
    # Run for both strategies
    run_full_backtest(TrendMaCrossStrategy, symbol="ETHUSDT", timeframe="60")
    run_full_backtest(DonchianBreakoutStrategy, symbol="ETHUSDT", timeframe="60")
