# backend/setup_strategies.py
"""
Script de setup inicial para registrar estrategias.

Ejecutar una vez para:
1. Registrar estrategias en el registry
2. Crear configuraciones iniciales en la DB
"""

import sys
from pathlib import Path

# Setup path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from strategies.registry import get_registry
from strategies.example_rsi_macd import RSIMACDDivergenceStrategy
from database import SessionLocal
from models_db import StrategyConfig
import json


def register_built_in_strategies():
    """Registra estrategias built-in en el registry."""
    print("\n📦 Registering built-in strategies...")
    
    registry = get_registry()
    
    # Registrar ejemplo RSI MACD
    registry.register(RSIMACDDivergenceStrategy)
    
    print("✅ Built-in strategies registered")


def setup_db_configs():
    """
    Crea configuraciones iniciales en la DB para estrategias.
    """
    print("\n💾 Setting up DB configurations...")
    
    db = SessionLocal()
    
    try:
        # Configuración para RSI MACD
        existing = db.query(StrategyConfig).filter(
            StrategyConfig.strategy_id == "rsi_macd_divergence_v1"
        ).first()
        
        if not existing:
            config = StrategyConfig(
                strategy_id="rsi_macd_divergence_v1",
                name="RSI + MACD Divergence Detector",
                description="Detecta divergencias entre RSI y MACD para señales contrarian",
                version="1.0.0",
                enabled=0,  # Desactivada por defecto (puedes activarla desde el dashboard)
                interval_seconds=300,  # 5 minutos
                tokens=json.dumps(["ETH", "BTC", "SOL"]),
                timeframes=json.dumps(["1h", "4h"]),
                risk_profile="medium",
                mode="CUSTOM",
                source_type="ENGINE",
                config_json=json.dumps({
                    "rsi_period": 14,
                    "rsi_oversold": 30,
                    "rsi_overbought": 70,
                    "min_confidence": 0.65
                })
            )
            db.add(config)
            db.commit()
            print("  ✅ Created config for: rsi_macd_divergence_v1")
        else:
            print("  ℹ️  Config already exists for: rsi_macd_divergence_v1")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    print("="*60)
    print("⚙️  TraderCopilot - Strategy Setup")
    print("="*60)
    
    # 1. Registrar estrategias en registry
    register_built_in_strategies()
    
    # 2. Crear configs en DB
    setup_db_configs()
    
    print("\n" + "="*60)
    print("✅ Setup completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Start backend: python main.py")
    print("  2. Check strategies: curl http://localhost:8000/strategies/")
    print("  3. Start scheduler: python scheduler.py")
    print("\n💡 Tip: Activate strategies via PATCH /strategies/{id}")
    print("="*60)


if __name__ == "__main__":
    main()
