
import sys
import os
import json
from datetime import datetime

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from strategies.registry import get_registry
from strategies.ma_cross import MACrossStrategy
from strategies.bb_mean_reversion import BBMeanReversionStrategy

# Register them manually just in case, or rely on import if they are in registry.py init?
# main.py does the registration. We should replicate that here.
registry = get_registry()
registry.register(MACrossStrategy)
registry.register(BBMeanReversionStrategy)

def test_strategy(strategy_id, tokens, timeframe):
    print(f"\nExample Run: {strategy_id} on {tokens} ({timeframe}) - {datetime.utcnow()}")
    strategy = registry.get(strategy_id)
    if not strategy:
        print(f"❌ Strategy {strategy_id} not found")
        return

    print(f"Strategy Name: {strategy.metadata().name}")
    
    # Run
    try:
        signals = strategy.generate_signals(tokens, timeframe)
        print(f"✅ Generated {len(signals)} signals")
        
        # Sort by timestamp desc
        signals.sort(key=lambda s: s.timestamp, reverse=True)
        
        # Show top 5
        for s in signals[:5]:
            print(f"[{s.timestamp}] {s.token} {s.direction.upper()} @ {s.entry} (Conf: {s.confidence})")
            print(f"   Rationale: {s.rationale}")
            
    except Exception as e:
        print(f"❌ Error running strategy: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test MA Cross
    test_strategy("ma_cross_v1", ["BTC", "ETH"], "1h")
    
    # Test BB Reversion
    # Note: I need to check the ID in the file, assuming bb_mean_reversion_v1?
    test_strategy("bb_mean_reversion_v1", ["BTC", "ETH"], "1h")
