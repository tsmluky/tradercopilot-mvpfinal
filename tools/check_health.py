import requests
import time

def check_health():
    url = "http://127.0.0.1:8000/health"
    print(f"Pinging {url}...")
    try:
        start = time.time()
        res = requests.get(url, timeout=5)
        elapsed = time.time() - start
        print(f"Status: {res.status_code}")
        print(f"Body: {res.text}")
        print(f"Time: {elapsed:.2f}s")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    check_health()
