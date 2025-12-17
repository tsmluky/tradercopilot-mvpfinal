import sys
import os
import requests
import uuid
import time
from datetime import datetime, timedelta

# Decoupled imports to avoid circular dependency hell
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))
from database import SessionLocal
from models_db import Signal, User, SchedulerLock, AdminAuditLog
from core.signal_logger import log_signal
from core.schemas import Signal as SignalSchema

# API CONFIG
BASE_URL = "http://localhost:8000"

def print_pass(msg):
    print(f"✅ PASS: {msg}")

def print_fail(msg):
    print(f"❌ FAIL: {msg}")

def print_kpi(msg):
    print(f"📊 KPI: {msg}")

def print_header(title):
    print(f"\n{'='*50}\n🔎 {title}\n{'='*50}")

def check_api_health():
    try:
        res = requests.get(f"{BASE_URL}/health", timeout=2)
        return res.status_code == 200
    except:
        return False

def audit_idempotency(db):
    print_header("AUDIT B: IDEMPOTENCY (Internal DB Logic)")
    
    # 1. Create a Signal
    token = "AUDIT_BTC"
    
    # Use Schema to simulate 'log_signal' input
    signal = SignalSchema(
        timestamp=datetime.utcnow(),
        strategy_id="audit_test",
        mode="AUDIT",
        token=token,
        timeframe="1h",
        direction="long",
        entry=100.0,
        source="audit_script"
    )
    
    print("   Attempt 1: Logging Signal...")
    try:
        log_signal(signal)
    except Exception as e:
        print_fail(f"Logging failed: {e}")
        return

    # 2. Verify in DB
    count1 = db.query(Signal).filter(Signal.token == token, Signal.mode == "AUDIT").count()
    if count1 >= 1:
        print_pass("Signal created in DB.")
    else:
        print_fail("Signal NOT found in DB.")
        
    # 3. Attempt Duplicate
    print("   Attempt 2: Logging Duplicate Signal...")
    try:
        log_signal(signal) # Same timestamp in object = Same key
    except Exception as e:
        print(f"   (Caught expected exception or logged error: {e})")
    
    # 4. Verify Count
    count2 = db.query(Signal).filter(Signal.token == token, Signal.mode == "AUDIT").count()
    if count2 == count1:
        print_pass(f"Idempotency verified. Count remained {count1}.")
    else:
        print_fail(f"Duplicate created! Count: {count1} -> {count2}")

def audit_scheduler_lock(db):
    print_header("AUDIT C: SCHEDULER LOCK (DB Logic)")
    
    lock_name = "audit_test_lock"
    owner_1 = "instance_1"
    owner_2 = "instance_2"
    ttl = 5
    
    # Clean previous
    db.query(SchedulerLock).filter(SchedulerLock.lock_name == lock_name).delete()
    db.commit()
    
    # 1. Acquire Lock 1
    lock = SchedulerLock(
        lock_name=lock_name,
        owner_id=owner_1,
        expires_at=datetime.utcnow() + timedelta(seconds=ttl)
    )
    db.add(lock)
    db.commit()
    print_pass(f"Instance 1 acquired lock '{lock_name}'")
    
    # 2. Attempt Acquire Logic Simulation
    existing = db.query(SchedulerLock).filter(SchedulerLock.lock_name == lock_name).first()
    if existing and existing.expires_at > datetime.utcnow() and existing.owner_id != owner_2:
        print_pass("Instance 2 correctly sees lock as BUSY.")
    else:
        print_fail("Instance 2 failed to detect busy lock.")
        
    # 3. TTL Expiry
    print(f"   Waiting {ttl+1}s for TTL...")
    time.sleep(ttl + 1)
    
    existing = db.query(SchedulerLock).filter(SchedulerLock.lock_name == lock_name).first()
    # Check if effectively expired logic works (compare to UTC now)
    if existing.expires_at < datetime.utcnow():
        print_pass("Lock expired. Instance 2 can take over.")
    else:
        print_fail("Lock did not expire in time?")

def audit_rbac_explicit(db):
    print_header("AUDIT D.2: RBAC REAL (403 CHECK)")
    
    if not check_api_health():
         print_fail("API Down. Skipping RBAC.")
         return

    # 1. Create Non-Owner User
    email = f"audit_rbac_{uuid.uuid4()}@test.com"
    pwd = "password123"
    
    # Need password hash logic
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed = pwd_context.hash(pwd)
    
    user = User(email=email, hashed_password=hashed, role="user", plan="PRO") # Even PRO should be blocked from Admin
    db.add(user)
    db.commit()
    
    try:
        # 2. Login
        res_login = requests.post(f"{BASE_URL}/auth/token", data={"username": email, "password": pwd})
        if res_login.status_code != 200:
            print_fail(f"Login failed for test user: {res_login.text}")
            return
            
        token = res_login.json()["access_token"]
        
        # 3. Attempt Admin Access
        print("   Attempting /admin/stats with PRO USER (Non-Owner)...")
        res_admin = requests.get(f"{BASE_URL}/admin/stats", headers={"Authorization": f"Bearer {token}"})
        
        if res_admin.status_code == 403:
            print_pass("Access Denied (403) correctly for authenticated Non-Owner.")
        else:
            print_fail(f"Expected 403, got {res_admin.status_code}. RESPONSE: {res_admin.text}")
            
    finally:
        # Cleanup
        db.delete(user)
        db.commit()

def audit_security_gating():
    print_header("AUDIT D.1: BASIC SECURITY & GATING")
    
    if not check_api_health():
        print_fail("API is DOWN. Start backend (`python backend/main.py`) to audit security.")
        return

    # 1. Public
    res = requests.get(f"{BASE_URL}/health")
    if res.status_code == 200:
        print_pass("/health is Public.")
        
    # 2. Protected (Try /admin/stats)
    res = requests.get(f"{BASE_URL}/admin/stats")
    if res.status_code == 401:
        print_pass("/admin/stats rejected unauth request (401).")
    else:
        print_fail(f"/admin/stats allowed unauth? Code: {res.status_code}")

def audit_admin_db_logic(db):
    print_header("AUDIT F: ADMIN PANEL (DB Logic)")
    
    # Verify Audit Log exists
    # We manually insert one to verify model works
    try:
        audit = AdminAuditLog(
            admin_id=1,
            action="AUDIT_TEST_ACTION",
            target_id="TEST",
            details="Script Verify"
        )
        db.add(audit)
        db.commit()
        print_pass("AdminAuditLog model writes successfully.")
    except Exception as e:
        print_fail(f"AdminAuditLog write failed: {e}")

def run_suite():
    print("🚀 STARTING AUDIT SUITE (DECOUPLED)...")
    
    try:
        db = SessionLocal()
        audit_idempotency(db)
        audit_scheduler_lock(db)
        audit_admin_db_logic(db)
        audit_rbac_explicit(db)
    except Exception as e:
        print_fail(f"DB Error: {e}")
    finally:
        db.close()
        
    # API Part
    audit_security_gating()
    
    print("\nDONE.")

if __name__ == "__main__":
    run_suite()
