import time
import requests
import random
from datetime import datetime

API_URL = "https://zesty-surprise-production-1f0f.up.railway.app"
TOKENS = ["ETH", "BTC", "SOL"]
TIMEFRAMES = ["15m", "1h", "4h"]

def generate_traffic():
    print(f"🚀 Starting Live Signal Generator targeting {API_URL}")
    print("Press Ctrl+C to stop")
    
    iteration = 0
    while True:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")
        
        for token in TOKENS:
            for tf in TIMEFRAMES:
                # Randomly skip some to make it look natural
                if random.random() < 0.3:
                    continue
                    
                try:
                    # Call Analyze LITE
                    # This triggers the backend to fetch data, analyze, and LOG the signal to DB
                    payload = {"token": token, "timeframe": tf}
                    resp = requests.post(f"{API_URL}/analyze/lite", json=payload, timeout=10)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        direction = data.get("direction", "unknown")
                        print(f"✅ {token} {tf}: Generated {direction} signal")
                    else:
                        print(f"⚠️ {token} {tf}: API Error {resp.status_code}")
                        
                except Exception as e:
                    print(f"❌ Error {token} {tf}: {e}")
                    
                # Sleep a bit between requests to not hammer the server
                time.sleep(1)
        
        print("😴 Sleeping 30s...")
        time.sleep(30)

if __name__ == "__main__":
    generate_traffic()
