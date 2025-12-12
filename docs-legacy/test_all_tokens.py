import requests
import json

API_URL = "https://zesty-surprise-production-1f0f.up.railway.app"
TOKENS = ["ETH", "BTC", "SOL"]

def test_all_tokens():
    print(f"Testing API for all tokens...\n")
    
    for token in TOKENS:
        print(f"--- Testing {token} ---")
        payload = {"token": token, "timeframe": "1h"}
        
        try:
            resp = requests.post(f"{API_URL}/analyze/lite", json=payload, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"✅ Success: {data.get('direction')} @ {data.get('entry')}")
                print(f"   Token: {data.get('token')}, Confidence: {data.get('confidence')}")
            else:
                print(f"❌ Error {resp.status_code}")
                print(f"   Response: {resp.text[:200]}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print()

if __name__ == "__main__":
    test_all_tokens()
