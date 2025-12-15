import requests

BASE_URL = "http://127.0.0.1:8000"
TARGET_ID = "testing_avax"

print(f"Attempting to delete {TARGET_ID}...")
res = requests.delete(f"{BASE_URL}/strategies/marketplace/{TARGET_ID}")

if res.status_code == 200:
    print("SUCCESS: API returned 200 OK.")
else:
    print(f"FAILURE: {res.status_code} - {res.text}")
