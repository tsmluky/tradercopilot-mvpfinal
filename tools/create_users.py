import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

users = [
    {"email": "admin@tradercopilot.com", "password": "admin", "name": "Administrator"},
    {"email": "demo@tradercopilot.com", "password": "demo", "name": "Demo User"}
]

def create_users():
    print(f"Connecting to {BASE_URL}...")
    
    # Check health
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code != 200:
            print(f"❌ Backend not healthy: {r.status_code}")
            return
    except Exception as e:
        print(f"❌ Could not connect to backend: {e}")
        return

    for u in users:
        print(f"Creating user {u['email']}...", end=" ")
        try:
            # Endpoint is /auth/register?email=...&password=...&name=...
            # Query params based on router definition
            params = {
                "email": u["email"],
                "password": u["password"],
                "name": u["name"]
            }
            res = requests.post(f"{BASE_URL}/auth/register", params=params)
            
            if res.status_code == 200:
                print("✅ Created")
            elif res.status_code == 400 and "already registered" in res.text:
                print("⚠️  Already exists")
            else:
                print(f"❌ Failed: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_users()
