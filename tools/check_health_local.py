import requests
import time

def check():
    url = "http://127.0.0.1:8000/health"
    print(f"Checking {url}...")
    try:
        response = requests.get(url, timeout=2)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            print("✅ Backend is UP and reachable.")
        else:
            print("⚠️ Backend is UP but returned non-200.")
    except Exception as e:
        print(f"❌ Could not connect: {e}")
        print("Possible causes:")
        print("1. Backend is not running.")
        print("2. It's listening on a different port (check console output).")
        print("3. Firewall is blocking connection.")

if __name__ == "__main__":
    check()
