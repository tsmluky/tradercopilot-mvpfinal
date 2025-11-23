import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.getcwd())

from database import SessionLocal
from models_db import Signal

def check_signals():
    db = SessionLocal()
    try:
        # Buscar señales recientes (últimos 5 min)
        since = datetime.utcnow() - timedelta(minutes=5)
        signals = db.query(Signal).filter(
            Signal.timestamp >= since
        ).order_by(Signal.timestamp.desc()).all()
        
        print(f"Found {len(signals)} signals generated in the last 5 minutes:")
        for s in signals:
            print(f" - {s.timestamp} | {s.token} | {s.strategy_id} | {s.mode} | {s.direction}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_signals()
