import requests
import json

API_URL = "https://zesty-surprise-production-1f0f.up.railway.app"

def test_analyze_lite():
    print(f"Testing {API_URL}/analyze/lite...")
    payload = {
        "token": "ETH",
        "timeframe": "1h",
        "strategy": "lite_v2" # Optional, but good to be explicit if supported
    }
    
    try:
        response = requests.post(f"{API_URL}/analyze/lite", json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print("✅ Success! Response:")
        print(json.dumps(data, indent=2))
        
        # Basic validation
        required_fields = ["token", "direction", "entry", "tp", "sl"]
        missing = [f for f in required_fields if f not in data]
        
        if missing:
            print(f"❌ Missing fields: {missing}")
        else:
            print("✅ Response structure valid.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Text: {e.response.text}")

if __name__ == "__main__":
    test_analyze_lite()
