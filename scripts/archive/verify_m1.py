import sys
import os
import uuid
import time
from datetime import datetime
from fastapi.testclient import TestClient

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from database import SessionLocal
from models_db import Signal, SchedulerLock
from core.signal_logger import log_signal
from core.schemas import Signal as SignalSchema

client = TestClient(app)

def test_endpoints():
    print("\n--- [TEST] B-07: Health & Ready Endpoints ---")
    
    # Health
    try:
        r = client.get("/health")
        assert r.status_code == 200
        print(f"✅ /health: {r.json()}")
    except Exception as e:
        print(f"❌ /health FAILED: {e}")

    # Ready
    try:
        r = client.get("/ready")
        assert r.status_code == 200
        print(f"✅ /ready: {r.json()}")
    except Exception as e:
        print(f"❌ /ready FAILED: {e}")

def test_idempotency_and_upsert():
    print("\n--- [TEST] B-04/B-05: Idempotency & Upsert ---")
    
    # Create a deterministic signal
    fixed_ts = datetime.utcnow().replace(microsecond=0)
    strategy_id = "test_verifier"
    token = "TEST_ETH"
    mode = "LITE"
    
    sig_payload = SignalSchema(
        timestamp=fixed_ts,
        strategy_id=strategy_id,
        mode=mode,
        token=token,
        timeframe="1h",
        direction="long",
        entry=1000.0,
        tp=1100.0,
        sl=900.0,
        confidence=0.99,
        rationale="Verification Test",
        source="Verifier"
    )
    
    # 1. Log First Time
    print("👉 Attempting 1st Insert...")
    log_signal(sig_payload)
    
    # Check DB count
    db = SessionLocal()
    count_1 = db.query(Signal).filter(Signal.token == token, Signal.strategy_id == strategy_id).count()
    db.close()
    print(f"   Count after 1st: {count_1} (Expected >= 1)")

    # 2. Log Second Time (Exact Duplicate)
    print("👉 Attempting 2nd Insert (Duplicate)...")
    try:
        log_signal(sig_payload)
        print("   ✅ No crash on duplicate insert (Upsert/Ignore worked!)")
    except Exception as e:
        print(f"   ❌ CRASHED on duplicate: {e}")
        
    # Check DB count again
    db = SessionLocal()
    count_2 = db.query(Signal).filter(Signal.token == token, Signal.strategy_id == strategy_id).count() 
    db.close()
    print(f"   Count after 2nd: {count_2} (Expected same as {count_1})")
    
    if count_1 == count_2:
        print("✅ SUCCESS: Count did not increase, duplicate ignored.")
    else:
        print("❌ FAILURE: Count increased!")

def test_scheduler_lock():
    print("\n--- [TEST] B-06: Scheduler Lock ---")
    from scheduler import StrategyScheduler
    
    db = SessionLocal()
    
    # Scheduler A
    sched_a = StrategyScheduler(loop_interval=1)
    sched_a.lock_name = "test_lock"
    
    # Scheduler B
    sched_b = StrategyScheduler(loop_interval=1)
    sched_b.lock_name = "test_lock" # Same lock name
    
    print("👉 Scheduler A attempting lock...")
    res_a = sched_a.acquire_lock(db)
    print(f"   Scheduler A result: {res_a} (Expected True)")
    
    print("👉 Scheduler A attempting re-acquire (refresh)...")
    res_a_2 = sched_a.acquire_lock(db)
    print(f"   Scheduler A refresh: {res_a_2} (Expected True)")
    
    print("👉 Scheduler B attempting lock (should fail)...")
    res_b = sched_b.acquire_lock(db)
    print(f"   Scheduler B result: {res_b} (Expected False)")
    
    if res_a and res_a_2 and not res_b:
        print("✅ SUCCESS: Locking logic behaves correctly.")
    else:
        print("❌ FAILURE: Locking logic invalid.")
        
    # Cleanup
    db.query(SchedulerLock).filter(SchedulerLock.lock_name == "test_lock").delete()
    db.query(Signal).filter(Signal.token == "TEST_ETH").delete()
    db.commit()
    db.close()

if __name__ == "__main__":
    test_endpoints()
    test_idempotency_and_upsert()
    test_scheduler_lock()
    print("\n--- Verification Complete ---")
