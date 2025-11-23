# backend/test_signal_hub.py
"""
Script de verificación rápida del Signal Hub.

Ejecutar: python test_signal_hub.py
"""

import sys
from datetime import datetime
from pathlib import Path

# Setup path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("="*60)
print("🧪 Testing Signal Hub - TraderCopilot")
print("="*60)

# Test 1: Import Signal schema
print("\n[1/5] Testing Signal schema import...")
try:
    from core.schemas import Signal, SignalCreate
    print("✅ Signal schema imported successfully")
except Exception as e:
    print(f"❌ Failed to import Signal schema: {e}")
    sys.exit(1)

# Test 2: Import signal logger
print("\n[2/5] Testing signal logger import...")
try:
    from core.signal_logger import log_signal, signal_from_dict
    print("✅ Signal logger imported successfully")
except Exception as e:
    print(f"❌ Failed to import signal logger: {e}")
    sys.exit(1)

# Test 3: Import Strategy base
print("\n[3/5] Testing Strategy base import...")
try:
    from strategies.base import Strategy, StrategyMetadata
    print("✅ Strategy base imported successfully")
except Exception as e:
    print(f"❌ Failed to import Strategy base: {e}")
    sys.exit(1)

# Test 4: Create Signal instance
print("\n[4/5] Testing Signal instantiation...")
try:
    test_signal = Signal(
        timestamp=datetime.utcnow(),
        strategy_id="test_strategy",
        mode="TEST",
        token="ETH",
        timeframe="30m",
        direction="long",
        entry=3675.50,
        tp=3720.00,
        sl=3625.00,
        confidence=0.75,
        rationale="Test signal for verification",
        source="TEST",
        extra={"test": True}
    )
    print(f"✅ Signal instance created: {test_signal.token} {test_signal.direction} @ {test_signal.entry}")
except Exception as e:
    print(f"❌ Failed to create Signal instance: {e}")
    sys.exit(1)

# Test 5: Validate Signal fields
print("\n[5/5] Testing Signal validation...")
try:
    assert test_signal.token == "ETH"
    assert test_signal.mode == "TEST"
    assert test_signal.direction == "long"
    assert test_signal.entry == 3675.50
    assert test_signal.tp == 3720.00
    assert test_signal.sl == 3625.00
    assert test_signal.confidence == 0.75
    assert test_signal.extra["test"] is True
    print("✅ Signal validation passed")
except AssertionError as e:
    print(f"❌ Signal validation failed: {e}")
    sys.exit(1)

# Test 6 (Bonus): Test signal_from_dict helper
print("\n[BONUS] Testing signal_from_dict helper...")
try:
    legacy_dict = {
        "timestamp": "2025-11-21T16:00:00Z",
        "token": "BTC",
        "timeframe": "1h",
        "direction": "short",
        "entry": 42000.00,
        "tp": 41000.00,
        "sl": 42500.00,
        "confidence": 0.68,
        "rationale": "Legacy signal test",
        "source": "LEGACY",
    }
    
    converted_signal = signal_from_dict(
        legacy_dict,
        mode="LITE",
        strategy_id="legacy_adapter"
    )
    
    assert converted_signal.token == "BTC"
    assert converted_signal.mode == "LITE"
    assert converted_signal.strategy_id == "legacy_adapter"
    print("✅ signal_from_dict helper works correctly")
except Exception as e:
    print(f"⚠️  signal_from_dict test failed (non-critical): {e}")

print("\n" + "="*60)
print("🎉 All core tests passed!")
print("="*60)
print("\n✅ Signal Hub is operational and ready for use.")
print("\nNext steps:")
print("  1. Start backend: python main.py")
print("  2. Test endpoints: curl -X POST http://localhost:8000/analyze/lite \\")
print("                       -H 'Content-Type: application/json' \\")
print("                       -d '{\"token\":\"eth\",\"timeframe\":\"30m\"}'")
print("  3. Check logs: ls logs/LITE/")
print("\n📚 Read SIGNAL_HUB.md for complete documentation")
print("="*60)
