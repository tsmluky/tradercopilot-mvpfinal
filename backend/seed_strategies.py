import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.getcwd())

from database import SessionLocal
from models_db import StrategyConfig
from strategies.registry import get_registry
from strategies.ma_cross import MACrossStrategy
from strategies.donchian import DonchianStrategy
from strategies.bb_mean_reversion import BBMeanReversionStrategy

def seed_strategies():
    db = SessionLocal()
    registry = get_registry()
    
    # Registrar clases para obtener metadatos
    registry.register(MACrossStrategy)
    registry.register(DonchianStrategy)
    registry.register(BBMeanReversionStrategy)
    
    strategies_to_seed = [
        MACrossStrategy(),
        DonchianStrategy(),
        BBMeanReversionStrategy()
    ]
    
    print("🌱 Seeding strategies...")
    
    for strategy in strategies_to_seed:
        meta = strategy.metadata()
        
        # Buscar si ya existe
        existing = db.query(StrategyConfig).filter(
            StrategyConfig.strategy_id == meta.id
        ).first()
        
        if existing:
            print(f"  - Updating {meta.name} ({meta.id})")
            existing.name = meta.name
            existing.config_json = json.dumps(meta.config)
            existing.tokens = json.dumps(["ETH", "BTC", "SOL"]) # Default tokens
            existing.timeframes = json.dumps(["15m", "1h", "4h"]) # Default timeframes
            existing.enabled = True
            existing.interval_seconds = 60 # Run every minute for testing
        else:
            print(f"  - Creating {meta.name} ({meta.id})")
            new_config = StrategyConfig(
                strategy_id=meta.id,
                name=meta.name,
                config_json=json.dumps(meta.config),
                tokens=json.dumps(["ETH", "BTC", "SOL"]),
                timeframes=json.dumps(["15m", "1h", "4h"]),
                enabled=True,
                interval_seconds=60, # Run every minute for testing
                last_execution=None
            )
            db.add(new_config)
            
    try:
        db.commit()
        print("✅ Strategies seeded successfully!")
    except Exception as e:
        print(f"❌ Error seeding strategies: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_strategies()
