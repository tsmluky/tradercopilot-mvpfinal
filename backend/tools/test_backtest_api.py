
import requests
import json

url = "http://127.0.0.1:8000/backtest/run"
payload = {
    "strategy_id": "rsi_divergence", # Assuming filename is rsi_divergence.py
    "token": "sol",
    "timeframe": "1h",
    "days": 60, # Longer test to force signals
    "initial_capital": 1000
}

print("🚀 Sending Backtest Request...")
try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        print("✅ Success!")
        print(json.dumps(data["metrics"], indent=2))
        print(f"Trades: {len(data['trades'])}")
        print(f"Curve Points: {len(data.get('curve', []))}")
        if data.get('curve'):
            print("First Curve Point:", data['curve'][0])
            print("Last Curve Point:", data['curve'][-1])
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"❌ Connection Error: {e}")
