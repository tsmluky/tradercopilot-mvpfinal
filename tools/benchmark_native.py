
import asyncio
from datetime import datetime, timedelta
import pandas as pd
import pytz
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from strategies.TrendFollowingNative import TrendFollowingNative
from market_data_api import get_ohlcv_data

async def run_native_benchmark():
    print("🚀 Benchmarking TrendFollowingNative...")
    
    tokens = ["BTC", "ETH", "SOL", "AVAX"]
    timeframes = ["1h", "4h", "1d"]
    days = 180
    
    strategy = TrendFollowingNative()
    results = []
    
    for token in tokens:
        for tf in timeframes:
            print(f"Testing {token} {tf}...")
            try:
                # 1. Fetch Data
                raw_data = get_ohlcv_data(token, tf, limit=1500) # Approx 2 months for 1h, plenty for others
                if not raw_data:
                    print(f"Skipping {token} {tf} (No Data)")
                    continue
                
                df = pd.DataFrame(raw_data, columns=["timestamp", "open", "high", "low", "close", "volume"])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                df.set_index("timestamp", inplace=True)
                
                # 2. Run Strategy
                signals = strategy.analyze(df, token, tf)
                
                # 3. Simple Backtest (Calculate PnL)
                initial_capital = 1000
                capital = initial_capital
                position = None # (entry_price, size, sl, tp)
                trades = 0
                wins = 0
                
                # Sort signals by time just in case
                signals.sort(key=lambda s: s.timestamp)
                
                for i in range(len(df)):
                    candle = df.iloc[i]
                    current_time = candle.name
                    close = candle["close"]
                    high = candle["high"]
                    low = candle["low"]
                    
                    # Manage Open Position
                    if position:
                        entry, size, sl, tp, direction = position
                        
                        # Check Stops
                        hit_tp = (high >= tp) if direction == "long" else (low <= tp)
                        hit_sl = (low <= sl) if direction == "long" else (high >= sl)
                        
                        if hit_tp:
                            pnl = (tp - entry) * size if direction == "long" else (entry - tp) * size
                            capital += pnl
                            trades += 1
                            wins += 1 # Win
                            position = None
                            # print(f"  WIN: {pnl:.2f}")
                        elif hit_sl:
                            pnl = (sl - entry) * size if direction == "long" else (entry - sl) * size
                            capital += pnl
                            trades += 1
                            # print(f"  LOSS: {pnl:.2f}")
                            position = None
                            
                    # Open New Position (if none open)
                    # Find signal for this candle
                    # In real backtest we'd use more complex logic, here we just check if a signal was generated *at* this time
                    # Actually strategy.analyze returns signals *at* the time they trigger. 
                    # We need to match signal timestamp to candle timestamp.
                    
                    if not position:
                        relevant_sig = next((s for s in signals if s.timestamp == current_time), None)
                        if relevant_sig:
                            entry = close # Assume close execution
                            sl = relevant_sig.sl
                            tp = relevant_sig.tp
                            risk = abs(entry - sl)
                            if risk == 0: continue
                            
                            # Risk 2%
                            risk_amount = capital * 0.02
                            size = risk_amount / risk
                            
                            position = (entry, size, sl, tp, relevant_sig.direction)
                            
                roi = ((capital - initial_capital) / initial_capital) * 100
                res = {
                    "token": token,
                    "tf": tf,
                    "trades": trades,
                    "win_rate": round((wins/trades)*100, 1) if trades > 0 else 0,
                    "roi": round(roi, 2),
                    "final_cap": round(capital, 2)
                }
                results.append(res)
                print(f"  -> ROI: {res['roi']}% | Trades: {trades} | WR: {res['win_rate']}%")
                
            except Exception as e:
                print(f"Error {token} {tf}: {e}")
                
    # Print Summary
    print("\n" + "="*50)
    print("NATIVE STRATEGY BENCHMARK RESULTS (180 Days)")
    print("="*50)
    print(f"{'TOKEN':<10} {'TF':<5} {'TRADES':<8} {'WR%':<6} {'ROI%':<8}")
    print("-" * 50)
    for r in results:
         print(f"{r['token']:<10} {r['tf']:<5} {r['trades']:<8} {r['win_rate']:<6} {r['roi']:<8}")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(run_native_benchmark())
