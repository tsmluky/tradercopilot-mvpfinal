import sys
import os
import requests
import time
import subprocess

BASE_URL = "http://127.0.0.1:8000"
FREE_USER = "test@tradercopilot.com"
FREE_PASS = "test1234"

def get_token(email, password):
    try:
        r = requests.post(f"{BASE_URL}/auth/token", data={"username": email, "password": password})
        if r.status_code == 200:
            return r.json()["access_token"]
        print(f"Login failed: {r.text}")
    except Exception as e:
        print(f"Connection failed: {e}")
    return None

def verify_m3():
    print("\n=== VERIFYING M3: MONETIZATION GATING ===")
    
    # 1. Login as FREE user
    print("\n1. Login as FREE user...")
    token = get_token(FREE_USER, FREE_PASS)
    if not token:
        print("❌ Login failed for Free User")
        return
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Try PRO endpoint (Should Fail 403)
    print("\n2. Accessing PRO endpoint (Expect 403)...")
    r = requests.post(f"{BASE_URL}/analyze/pro", json={"token": "BTC", "timeframe": "1h"}, headers=headers)
    if r.status_code == 403:
        print("✅ 403 Forbidden received.")
        print(f"   Payload: {r.json()}")
    else:
        print(f"❌ Failed! Expected 403, got {r.status_code}")
        
    # 3. Upgrade User to PRO via Admin CLI
    print("\n3. Upgrading User to PRO via CLI...")
    cmd = f"python backend/admin_upgrade.py {FREE_USER} PRO"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(res.stdout)
    
    # 4. Try PRO endpoint again (Should Succeed 200)
    # Note: Changes in DB reflect immediately in next request (get_current_user queries DB)
    print("\n4. Accessing PRO endpoint (Expect Success)...")
    
    # IMPORTANT: We need correct headers. Is analyze/pro needing more fields?
    # ProReq: token, timeframe, user_message(opt)
    # But wait, analyze_pro requires 'request' object for rate limiting?
    # And it might fail if dependencies are missing or if deepseek isn't configured,
    # BUT it should NOT return 403. 500 or 200 or 400 is fine.
    
    r = requests.post(f"{BASE_URL}/analyze/pro", json={"token": "BTC", "timeframe": "1h"}, headers=headers)
    
    if r.status_code != 403:
        print(f"✅ Success! Status: {r.status_code} (Not 403)")
    else:
        print(f"❌ Still 403 Forbidden! Upgrade didn't work?")

if __name__ == "__main__":
    verify_m3()
