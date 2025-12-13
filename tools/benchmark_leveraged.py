
import sys
import os
import pandas as pd
import ccxt
from datetime import datetime, timedelta

# Fix path to include backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.strategies.donchian import DonchianStrategy

def benchmark_leveraged():
    print("🚀 Starting LEVERAGED Benchmark (Volatile!)\n")
    
    tokens = ["BTCUP", "ETHUP"] 
    timeframes = ["4h", "1d"]
    
    results = []
    
    strategy = DonchianStrategy()
    exchange = ccxt.binance()
    
    for token in tokens:
        for tf in timeframes:
            try:
                print(f"[FETCH] {token} {tf}...")
                
                # Direct CCXT Fetch
                symbol = f"{token}/USDT"
                ohlcv = exchange.fetch_ohlcv(symbol, tf, limit=500)
                
                if not ohlcv or len(ohlcv) < 50:
                    print(f"  ⚠️ Not enough data for {token}")
                    continue
                    
                # Parse to DF
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                # Run Analysis
                signals = strategy.analyze(df, token, tf)
                
                # Signal + Volatility Metrics
                start_price = df['close'].iloc[0]
                end_price = df['close'].iloc[-1]
                buy_hold = (end_price - start_price) / start_price * 100
                
                print(f"  📊 {token} {tf} | Signals: {len(signals)} | Buy&Hold: {buy_hold:.2f}%")
                
                results.append({
                    "Token": token,
                    "Timeframe": tf,
                    "Signals": len(signals),
                    "BuyHold_Pct": round(buy_hold, 2)
                })
                
            except Exception as e:
                print(f"  ❌ Error: {e}")

    print("\n=== LEVERAGED REPORT ===")
    print(pd.DataFrame(results))

if __name__ == "__main__":
    benchmark_leveraged()

