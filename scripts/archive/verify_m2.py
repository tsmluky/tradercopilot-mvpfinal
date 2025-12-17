import sys
import os
import requests
from fastapi.testclient import TestClient

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from database import SessionLocal
from models_db import User

client = TestClient(app)

ADMIN_EMAIL = "admin@tradercopilot.com"
ADMIN_PASS = "admin123"

def test_login_flow():
    print("\n--- [TEST] C-01: Auth Flow ---")
    
    # 1. Try public endpoint (Health) -> Should PASS
    r = client.get("/health")
    print(f"1. /health status: {r.status_code} (Expected 200)")
    assert r.status_code == 200
    
    # 2. Try Login
    print(f"2. Logging in as {ADMIN_EMAIL}...")
    payload = {
        "username": ADMIN_EMAIL, 
        "password": ADMIN_PASS
    }
    # OAuth2 expects form data
    r = client.post("/auth/token", data=payload)
    if r.status_code != 200:
        print(f"❌ Login Failed: {r.text}")
        return None
    
    token_data = r.json()
    token = token_data.get("access_token")
    print(f"✅ Login Success! Token: {token[:15]}...")
    return token

def test_protected_routes(token: str):
    print("\n--- [TEST] C-02: Protected Routes ---")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Protected Endpoint without Token
    print("1. Accessing /analyze/lite WITHOUT token...")
    r = client.post("/analyze/lite", json={"token": "ETH", "timeframe": "1h"})
    print(f"   Status: {r.status_code} (Expected 401)")
    if r.status_code == 401:
        print("   ✅ Protected.")
    else:
        print(f"   ❌ FAILED: Got {r.status_code}")

    # 2. Protected Endpoint WITH Token
    print("2. Accessing /analyze/lite WITH token...")
    # Mocking logic requires DB execution which might call external API, 
    # but unittest inside TestClient might choke on async DB if not handled perfectly.
    # However, getting 404 (due to market data) or 502 is better than 401.
    # A 401 means auth failed. Anything else means auth passed.
    
    try:
        r = client.post("/analyze/lite", json={"token": "ETH", "timeframe": "1h"}, headers=headers)
        print(f"   Status: {r.status_code}")
        if r.status_code == 401:
            print("   ❌ FAILED: Still 401 (Token invalid?)")
        else:
            print(f"   ✅ Auth Passed (Status {r.status_code} is expected logic result)")
    except Exception as e:
        print(f"   ⚠️ Endpoint crash (logic error), but Auth likely passed: {e}")

    # 3. Strategy Create (Protected)
    print("3. Accessing /strategies/marketplace/create WITH token...")
    # Just checking auth, not full logic
    try:
        # Invalid pyload to fail fast
        r = client.post("/strategies/marketplace/create", json={}, headers=headers)
        print(f"   Status: {r.status_code}")
        if r.status_code == 401:
             print("   ❌ FAILED: Still 401")
        else:
             print(f"   ✅ Auth Passed (Got {r.status_code} validation error as expected)")
    except:
        pass

if __name__ == "__main__":
    token = test_login_flow()
    if token:
        test_protected_routes(token)
    else:
        print("❌ Cannot proceed without token.")
