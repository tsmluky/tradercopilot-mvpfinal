
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from core.backtest_engine import BacktestEngine

def run_debug():
    engine = BacktestEngine(initial_capital=1000)
    
    print("\n--- TEST: Running Bollinger Reversion (BacktestEngine) ---")
    try:
        # Usamos los mismos params que en UI: 1h, 30 days
        results = engine.run(
            strategy_id="bb_mean_reversion",
            symbol="ETH", # ETH funcionaba bien en torneo
            timeframe="1h",
            days=30
        )
        
        metrics = results['metrics']
        print("\n--- RESULTS ---")
        print(json.dumps(metrics, indent=2))
        
        trades = results['trades']
        print(f"\nTotal Trades: {len(trades)}")
        if trades:
            print("Last 3 trades:")
            for t in trades[-3:]:
                print(t)
                
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_debug()
