import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.getcwd())

from strategies.ma_cross import MACrossStrategy
from strategies.DonchianBreakoutV2 import DonchianBreakoutV2 as DonchianStrategy
from core.schemas import Signal

def test_strategy(strategy_class, name):
    print(f"\n--- Testing {name} ---")
    strategy = strategy_class()
    
    # Test generate_signals (Live/Mock Data Fetch)
    print(f"Generating signals for ETHUSDT 1h...")
    try:
        signals = strategy.generate_signals(["ETHUSDT"], "1h")
        print(f"Generated {len(signals)} signals.")
        if signals:
            last_sig = signals[-1]
            print(f"Last Signal: {last_sig.direction} @ {last_sig.entry} (Time: {last_sig.timestamp})")
            print(f"Rationale: {last_sig.rationale}")
            print(f"Extra: {last_sig.extra}")
        else:
            print("No signals generated (this might be normal if conditions aren't met).")
            
    except Exception as e:
        print(f"❌ Error generating signals: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Live Strategy Test")
    test_strategy(MACrossStrategy, "MACrossStrategy")
    test_strategy(DonchianStrategy, "DonchianStrategy")
