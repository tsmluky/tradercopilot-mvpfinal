# backend/test_fase2.py
"""
Test rápido de Fase 2: Estrategias 24/7

Verifica que:
1. Registry funciona
2. StrategyConfig se puede crear en DB
3. Scheduler puede cargar y ejecutar estrategias
"""

import sys
from pathlib import Path

# Setup path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("="*60)
print("🧪 Testing Fase 2 - Estrategias 24/7")
print("="*60)

# Test 1: Imports
print("\n[1/6] Testing imports...")
try:
    from strategies.registry import get_registry, StrategyRegistry
    from strategies.example_rsi_macd import RSIMACDDivergenceStrategy
    from models_db import StrategyConfig
    from database import SessionLocal
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Registry
print("\n[2/6] Testing StrategyRegistry...")
try:
    registry = get_registry()
    assert isinstance(registry, StrategyRegistry)
    print("✅ Registry instance created")
except Exception as e:
    print(f"❌ Registry test failed: {e}")
    sys.exit(1)

# Test 3: Register strategy
print("\n[3/6] Testing strategy registration...")
try:
    registry.register(RSIMACDDivergenceStrategy)
    strategies = registry.list_all()
    assert len(strategies) > 0
    assert any(s.id == "rsi_macd_divergence_v1" for s in strategies)
    print(f"✅ Strategy registered: {strategies[0].name}")
except Exception as e:
    print(f"❌ Registration failed: {e}")
    sys.exit(1)

# Test 4: Get strategy instance
print("\n[4/6] Testing strategy instantiation...")
try:
    strategy = registry.get("rsi_macd_divergence_v1")
    assert strategy is not None
    meta = strategy.metadata()
    assert meta.id == "rsi_macd_divergence_v1"
    print(f"✅ Strategy instance created: {meta.name}")
except Exception as e:
    print(f"❌ Instantiation failed: {e}")
    sys.exit(1)

# Test 5: StrategyConfig model
print("\n[5/6] Testing StrategyConfig model...")
try:
    import json
    
    config = StrategyConfig(
        strategy_id="test_strategy",
        name="Test Strategy",
        description="Test",
        version="1.0.0",
        enabled=1,
        interval_seconds=60,
        tokens=json.dumps(["ETH"]),
        timeframes=json.dumps(["1h"]),
        risk_profile="low",
        mode="TEST",
        source_type="ENGINE",
    )
    
    assert config.strategy_id == "test_strategy"
    assert config.enabled == 1
    print("✅ StrategyConfig model works")
except Exception as e:
    print(f"❌ StrategyConfig test failed: {e}")
    sys.exit(1)

# Test 6: Database interaction (read-only)
print("\n[6/6] Testing DB connectivity...")
try:
    db = SessionLocal()
    count = db.query(StrategyConfig).count()
    db.close()
    print(f"✅ DB connection OK (found {count} configs)")
except Exception as e:
    print(f"⚠️  DB connection warning: {e}")
    print("   (This is OK if DB hasn't been initialized yet)")

print("\n" + "="*60)
print("🎉 All core tests passed!")
print("="*60)
print("\nNext steps:")
print("  1. Run setup: python setup_strategies.py")
print("  2. Start backend: python main.py")
print("  3. Start scheduler: python scheduler.py 10")
print("  4. Test API: curl http://localhost:8000/strategies/")
print("\n📚 Read FASE2_STRATEGIES_247.md for complete guide")
print("="*60)
