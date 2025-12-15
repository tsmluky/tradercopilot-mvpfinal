import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def run_test():
    print(f"Testing Delete Flow on {BASE_URL}...")

    # 1. Create Dummy
    persona_data = {
        "name": "Delete Me",
        "description": "Temp agent to test deletion",
        "symbol": "BTC",
        "timeframe": "1h",
        "strategy_id": "ma_cross",
        "risk_level": "High",
        "expected_roi": "100%",
        "win_rate": "50%",
        "frequency": "Day Trader"
    }

    print("1. Creating Persona...")
    res = requests.post(f"{BASE_URL}/strategies/marketplace/create", json=persona_data)
    if res.status_code != 200:
        print(f"FAILED to create: {res.text}")
        return
    
    data = res.json()
    p_id = data['id']
    print(f"   Created ID: {p_id}")

    # 2. Verify it exists
    print("2. Verifying existence in Marketplace...")
    res = requests.get(f"{BASE_URL}/strategies/marketplace")
    personas = res.json()
    found = any(p['id'] == p_id for p in personas)
    if not found:
        print("FAILED: Persona not found in list immediately after creation.")
        return
    print("   Confirmed existence.")

    # 3. Delete it
    print(f"3. Deleting {p_id}...")
    res = requests.delete(f"{BASE_URL}/strategies/marketplace/{p_id}")
    if res.status_code != 200:
        print(f"FAILED to delete: {res.text}")
        return
    print("   Delete API returned Success.")

    # 4. Verify it is gone via API
    print("4. Verifying removal from Marketplace list...")
    res = requests.get(f"{BASE_URL}/strategies/marketplace")
    personas = res.json()
    found_still = any(p['id'] == p_id for p in personas)
    
    if found_still:
        print("FAILED: Persona STILL EXISTS in API list after deletion!")
    else:
        print("SUCCESS: Persona removed from API list.")

    # 5. Check file content manually (Simulate persistence check)
    try:
        with open("backend/marketplace_config.py", "r", encoding="utf-8") as f:
            content = f.read()
            if p_id in content:
                print("FAILED: Persona ID found in marketplace_config.py file content! (Persistence failed)")
            else:
                print("SUCCESS: Persona ID not found in file (Persistence success).")
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    run_test()
