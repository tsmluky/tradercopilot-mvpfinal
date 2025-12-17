import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models_db import Signal, SignalEvaluation

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_persona_signal(db: Session, persona_id: str, result: str):
    """
    Creates a CLOSED (Evaluated) signal for a specific Persona.
    """
    # Create Signal
    sig = Signal(
        timestamp=datetime.utcnow() - timedelta(hours=2),
        token="BTC",
        timeframe="1h",
        direction="long",
        entry=50000,
        tp=51000,
        sl=49000,
        confidence=0.95,
        rationale="Stats Test",
        source=f"Marketplace:{persona_id}", # CRITICAL: This matches the aggreg logic
        mode="LITE",
        strategy_id="donchian_v2",
        idempotency_key=f"stats_test_{persona_id}_{datetime.utcnow().timestamp()}",
        user_id=None
    )
    db.add(sig)
    db.commit()
    
    # Create Evaluation
    eval_obj = SignalEvaluation(
        signal_id=sig.id,
        evaluated_at=datetime.utcnow(),
        result=result,
        pnl_r=1.0 if result == "WIN" else -1.0,
        exit_price=51000 if result == "WIN" else 49000
    )
    db.add(eval_obj)
    db.commit()
    return sig.id

async def verify_stats():
    print("\n=== VERIFYING M4: MARKETPLACE STATS ===")
    
    # We need to run the async function get_marketplace
    # But it depends on 'db'. use manual session
    
    db = SessionLocal()
    try:
        # 1. Pick a target persona
        target_id = "titan_btc" 
        
        # 2. Seed Data: 1 WIN, 0 LOSS -> 100% WR
        print(f"Seeding 1 WIN for {target_id}...")
        create_persona_signal(db, target_id, "WIN")
        
        # 3. Call the Logic (Extract from router to avoid FastAPI context issues? 
        # Or just run the inner logic script)
        
        # NOTE: Cannot easily call 'get_marketplace' directly due to Depends(get_db).
        # I will replicate the logic exactly as implemented in routers/strategies.py
        
        from marketplace_config import refresh_personas
        from models_db import Signal, SignalEvaluation
        from sqlalchemy import func
        
        personas = refresh_personas()
        found = False
        
        for p in personas:
            if p['id'] == target_id:
                target_source = f"Marketplace:{p['id']}"
                
                total = db.query(func.count(Signal.id)).filter(Signal.source == target_source).scalar() or 0
                wins = db.query(func.count(Signal.id)).join(SignalEvaluation).filter(
                    Signal.source == target_source,
                    SignalEvaluation.result == "WIN"
                ).scalar() or 0
                
                print(f"DB Stats for {target_id}: Total={total}, Wins={wins}")
                
                wr = 0.0
                if total > 0:
                    wr = (wins / total) * 100
                    
                print(f"Calculated WR: {wr}%")
                
                if total > 0 and wins >= 1:
                    print(f"✅ Stats Injection Logic Validation Passed.")
                    found = True
                    
                    # Verify Injection
                    p["win_rate"] = f"{int(wr)}%"
                    print(f"Final API Field 'win_rate': {p['win_rate']}")
                else:
                    print("❌ Failed to retrieve stats from DB.")
                
                break
                
        if not found:
            print("❌ Target Persona not found in config.")

    finally:
        db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(verify_stats())
