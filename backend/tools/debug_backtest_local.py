
import sys
import os
import traceback

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.backtest_engine import BacktestEngine

def run_debug():
    print("🚀 Starting Debug Backtest...")
    try:
        engine = BacktestEngine(initial_capital=1000)
        
        # Test Params
        strategy = "rsi_divergence"
        token = "SOL"
        timeframe = "1h"
        days = 30
        
        print(f"Running {strategy} on {token} ({timeframe}, {days}d)...")
        
        results = engine.run(strategy, token, timeframe, days)
        
        print("\n✅ Success!")
        print("PnL:", results["metrics"]["total_pnl"])
        print("Trades:", results["metrics"]["total_trades"])
        print("Curve Points:", len(results.get("curve", [])))
        
    except Exception as e:
        print("\n❌ CRITICAL FAILURE:")
        traceback.print_exc()

if __name__ == "__main__":
    run_debug()
