from database import SessionLocal
from models_db import StrategyConfig

db = SessionLocal()

# Desactivar todas excepto donchian_v2
to_disable = ['ma_cross_v1', 'donchian_breakout_v1', 'bb_mean_reversion_v1', 'rsi_macd_divergence_v1']

for sid in to_disable:
    strat = db.query(StrategyConfig).filter(StrategyConfig.strategy_id == sid).first()
    if strat:
        strat.enabled = 0
        print(f"❌ Desactivada: {sid}")

db.commit()

# Verificar estado final
print("\n=== ESTRATEGIAS ACTIVAS ===")
active = db.query(StrategyConfig).filter(StrategyConfig.enabled == 1).all()
for s in active:
    print(f"✅ {s.strategy_id} - {s.name}")

db.close()
print("\n✅ Listo! Solo queda donchian_v2 activa.")
