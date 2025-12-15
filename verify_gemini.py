
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar .env
load_dotenv("backend/.env")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # Try fallback to deepseek key just to see if user put google key there (unlikely but consistent with my code)
    api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    print("NO_API_KEY")
    exit(1)

print(f"Using API Key: {api_key[:5]}...{api_key[-3:]}")

try:
    genai.configure(api_key=api_key)
    models_to_test = ["gemini-2.5-flash"]
    
    for m_name in models_to_test:
        print(f"\nTesting {m_name}...")
        try:
            model = genai.GenerativeModel(m_name)
            response = model.generate_content("Say 'OK'")
            print(f"SUCCESS {m_name}: {response.text.strip()}")
        except Exception as e:
            print(f"FAILED {m_name}: {e}")

except Exception as e:
    print(f"GLOBAL ERROR: {e}")
