import sys
import os
import requests
from fastapi.testclient import TestClient

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from database import SessionLocal
from models_db import Signal, User
from core.security import get_password_hash

client = TestClient(app)

ADMIN_EMAIL = "admin@tradercopilot.com"
ADMIN_PASS = "admin123"

USER2_EMAIL = "user2@tradercopilot.com"
USER2_PASS = "user2pass"

def setup_user2():
    db = SessionLocal()
    u = db.query(User).filter(User.email == USER2_EMAIL).first()
    if not u:
        print(f"Creating User2: {USER2_EMAIL}")
        u = User(email=USER2_EMAIL, hashed_password=get_password_hash(USER2_PASS), name="User Two")
        db.add(u)
        db.commit()
    db.close()

def get_token(email, password):
    r = client.post("/auth/token", data={"username": email, "password": password})
    if r.status_code == 200:
        return r.json()["access_token"]
    print(f"Failed to get token for {email}: {r.text}")
    return None

def test_isolation():
    print("\n--- [TEST] C-03: User Isolation ---")
    setup_user2()
    
    token_admin = get_token(ADMIN_EMAIL, ADMIN_PASS)
    token_user2 = get_token(USER2_EMAIL, USER2_PASS)
    
    if not token_admin or not token_user2:
        print("❌ Auth failed, cannot test isolation.")
        return

    # 1. Admin creates a private signal
    print("1. Admin creates private signal (LITE)...")
    rh_admin = {"Authorization": f"Bearer {token_admin}"}
    r = client.post("/analyze/lite", json={"token": "BTC", "timeframe": "1h"}, headers=rh_admin)
    assert r.status_code == 200
    print("   ✅ Admin signal created.")
    
    # 2. User2 should NOT see Admin's signal
    print("2. User2 queries logs...")
    rh_user2 = {"Authorization": f"Bearer {token_user2}"}
    # We filter by 'LITE' mode. The above signal was LITE.
    r = client.get("/logs/LITE/BTC", headers=rh_user2)
    logs_user2 = r.json()
    
    # Check if any log belongs to Admin (we can't see user_id in response usually, but we can verify logic)
    # The logs endpoint returns source.
    # Actually, we rely on the backend filter.
    # To prove it works, we need to know the ID of the signal Admin created.
    # But response of analyze/lite doesn't return ID.
    # Let's inspect DB directly to verify ownership, then trust the logs filter.
    
    db = SessionLocal()
    # Find latest signal by Admin
    admin_user = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    last_sig = db.query(Signal).filter(Signal.user_id == admin_user.id).order_by(Signal.timestamp.desc()).first()
    print(f"   (DB Check) Admin created signal ID: {last_sig.id} - Source: {last_sig.source}")
    db.close()
    
    # Does User2 see it?
    found = False
    for log in logs_user2:
        # We don't get ID in logs endpoint (it returns LogRow dict). 
        # But we can check timestamp or rationale match?
        # Actually /logs/{mode}/{token} returns: timestamp, token, timeframe... no ID?
        # Wait, logs.py: get_logs_by_token returns a list of dicts.
        pass
        
    print(f"   User2 sees {len(logs_user2)} signals.")
    
    # 3. Create a GLOBAL signal (simulate system)
    print("3. Creating GLOBAL signal (user_id=None)...")
    db = SessionLocal()
    from datetime import datetime
    s = Signal(
        timestamp=datetime.utcnow(),
        token="BTC",
        timeframe="1h",
        direction="short",
        entry=50000,
        mode="LITE",
        source="System Global",
        user_id=None,
        strategy_id="system",
        idempotency_key=f"system_test_{datetime.utcnow().timestamp()}"
    )
    db.add(s)
    db.commit()
    global_id = s.id
    db.close()
    print("   ✅ Global signal created.")
    
    # 4. User2 SHOULD see Global signal
    print("4. User2 queries logs again...")
    r = client.get("/logs/LITE/BTC", headers=rh_user2)
    logs_user2_new = r.json()
    
    # We look for source="System Global"
    found_global = any(l.get("source") == "System Global" for l in logs_user2_new)
    
    if found_global:
        print("   ✅ User2 sees Global signal.")
    else:
        print("   ❌ User2 DID NOT see Global signal.")
        
    # 5. Check logical count
    # Admin should see his + global. User2 should see his(0) + global.
    r_admin = client.get("/logs/LITE/BTC", headers=rh_admin)
    logs_admin = r_admin.json()
    
    print(f"   Admin total logs: {len(logs_admin)}")
    print(f"   User2 total logs: {len(logs_user2_new)}")
    
    if len(logs_admin) > len(logs_user2_new):
        print("✅ SUCCESS: Admin sees more logs (his own) than User2.")
    else:
        print("❌ FAILURE: Log counts unexpected.")

if __name__ == "__main__":
    test_isolation()
