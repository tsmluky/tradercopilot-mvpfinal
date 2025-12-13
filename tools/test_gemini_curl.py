import os
import requests
import json
from dotenv import load_dotenv

def test_curl():
    load_dotenv(os.path.join('backend', '.env'))
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("No API Key")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    print(f"Testing URL: ...{url[-10:]}")
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        try:
            data = response.json()
            if "models" in data:
                print("Available Models:")
                for m in data["models"]:
                    if "generateContent" in m.get("supportedGenerationMethods", []):
                        print(f" - {m['name']} ({m.get('displayName')})")
            elif "error" in data:
                print(f"Error: {data['error']['message']}")
            else:
                print(f"Response: {response.text[:500]}")
        except:
             print(f"Response (Raw): {response.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_curl()
