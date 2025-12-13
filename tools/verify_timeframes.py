
import sys
import os
import json
import time

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from core.backtest_engine import BacktestEngine

def run_verify():
    engine = BacktestEngine(initial_capital=1000)
    
    timeframes = ["4h", "1h"]
    strat = "bb_mean_reversion"
    token = "ETH"
    days = 180 # Stress test data fetching
    
    for tf in timeframes:
        print(f"\n========================================")
        print(f"Testing {strat} on {token} {tf} ({days} days)")
        print(f"========================================")
        start_time = time.time()
        
        try:
            results = engine.run(
                strategy_id=strat,
                symbol=token,
                timeframe=tf,
                days=days
            )
            
            elapsed = time.time() - start_time
            metrics = results['metrics']
            print(f"✅ SUCCESS in {elapsed:.2f}s")
            print(f"Win Rate: {metrics['win_rate']}% | PnL: {metrics['total_pnl']}")
            print(f"Total Trades: {metrics['total_trades']}")
            print(f"Data Points in Curve: {len(results['curve'])}")
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    run_verify()
