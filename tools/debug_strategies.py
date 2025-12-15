import requests

try:
    print("Testing GET /strategies/marketplace ...")
    res = requests.get("http://localhost:8000/strategies/marketplace")
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text}")
except Exception as e:
    print(f"Error: {e}")
