
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load env
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_dir, ".env"))

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ API Key missing")
    exit(1)

genai.configure(api_key=api_key)

candidates = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-001",
    "gemini-1.5-flash-002",
    "gemini-1.5-pro",
    "gemini-2.5-flash", 
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite-001",
    "gemini-pro"
]

print(f"🔑 Testing {len(candidates)} models with Key: {api_key[:5]}...")

for model_name in candidates:
    print(f"\n👉 Testing: {model_name} ... ", end="", flush=True)
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, reply with OK.")
        print(f"✅ SUCCESS!")
        print(f"   Response: {response.text.strip()}")
        print(f"   🏆 WINNER: {model_name}")
        break  # Stop at first success
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            print("❌ 404 (Not Found)")
        elif "429" in error_msg or "ResourceExhausted" in error_msg:
            print("❌ 429 (Rate Limit / Quota)")
        else:
            print(f"❌ Error: {error_msg[:50]}...")
