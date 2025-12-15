
import sys
import os
import csv
from datetime import datetime, timedelta

# Fix path
sys.path.append(os.path.abspath("backend"))

from database import SessionLocal
from models_db import Signal, SignalEvaluation
from sqlalchemy import select

from evaluated_logger import LITE_DIR, EVAL_DIR, _parse_iso_ts

def heal_signals(db):
    print("--- Healing SIGNALS from LITE CSVs ---")
    files = list(LITE_DIR.glob("*.csv"))
    for f in files:
        token = f.stem.lower() # keys are usually lower?
        print(f"Processing {token}...")
        
        with open(f, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            inserted = 0
            for row in reader:
                count += 1
                try:
                    ts_str = row.get("timestamp")
                    if not ts_str: continue
                    ts_dt = _parse_iso_ts(ts_str)
                    
                    # Check if exists
                    exists = db.query(Signal).filter(
                        Signal.token == token.upper(),
                        Signal.timestamp == ts_dt
                    ).first()
                    
                    if not exists:
                        # Insert
                        sig = Signal(
                            timestamp=ts_dt,
                            token=token.upper(),
                            timeframe=row.get("timeframe"),
                            direction=row.get("direction"),
                            entry=float(row.get("entry") or 0),
                            tp=float(row.get("tp") or 0),
                            sl=float(row.get("sl") or 0),
                            confidence=float(row.get("confidence") or 0),
                            rationale=row.get("rationale") or "",
                            source=row.get("source") or "LITE",
                            mode="LITE", # Assuming LITE dir
                            strategy_id="lite_v2" # Default
                        )
                        db.add(sig)
                        inserted += 1
                except Exception as e:
                    print(f"Error row {count}: {e}")
            
            if inserted > 0:
                print(f"  Inserted {inserted} missing signals for {token}.")
            db.commit()

def heal_evaluations(db):
    print("\n--- Healing EVALUATIONS from EVALUATED CSVs ---")
    files = list(EVAL_DIR.glob("*.evaluated.csv"))
    for f in files:
        # filename is {token}.evaluated.csv
        token_part = f.name.replace(".evaluated.csv", "")
        token = token_part.upper()
        print(f"Processing {token}...")
        
        with open(f, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            inserted = 0
            for row in reader:
                count += 1
                try:
                    ts_str = row.get("signal_ts")
                    if not ts_str: continue
                    ts_dt = _parse_iso_ts(ts_str)
                    
                    # Find Parent Signal
                    # Fallback window +/- 1s
                    parent = db.query(Signal).filter(
                        Signal.token == token,
                        Signal.timestamp >= ts_dt - timedelta(seconds=1),
                        Signal.timestamp <= ts_dt + timedelta(seconds=1)
                    ).first()
                    
                    if not parent:
                        # print(f"  Scan failed for parent signal {ts_dt} {token}")
                        continue
                        
                    # Check if eval exists
                    if parent.evaluation:
                        continue
                        
                    # Insert Eval
                    ev = SignalEvaluation(
                        signal_id=parent.id,
                        evaluated_at=_parse_iso_ts(row.get("evaluated_at") or ts_str),
                        result=row.get("result"),
                        pnl_r=0.0, # Not in CSV explicit usually? Or need calc?
                        exit_price=float(row.get("price_at_eval") or 0)
                    )
                    # Try calc pnl_r from move_pct
                    move_pct = float(row.get("move_pct") or 0)
                    ev.pnl_r = move_pct / 100.0
                    
                    db.add(ev)
                    inserted += 1
                    
                except Exception as e:
                    print(f"Error eval row {count}: {e}")

            if inserted > 0:
                print(f"  Inserted {inserted} missing evaluations for {token}.")
            db.commit()

def main():
    db = SessionLocal()
    try:
        heal_signals(db)
        heal_evaluations(db)
        print("\nAll done.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
