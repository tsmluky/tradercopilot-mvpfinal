
import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_service import get_ai_service
from dotenv import load_dotenv

# Load env vars
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_dir, ".env"))

print("=== TESTING AI SERVICE ===")

try:
    service = get_ai_service()
    print(f"Service loaded: {service.__class__.__name__}")
    
    # Check key presence
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print(f"Gemini Key found: {gemini_key[:5]}...")
    else:
        print("Gemini Key NOT found in env variables loaded by script.")

    if isinstance(service, type(None)):
        print("❌ Error: get_ai_service returned None")
        sys.exit(1)

    print("\nSending test message: 'Hola, confirma que me recibes.'")
    
    response = service.chat([{"role": "user", "content": "Hola, confirma que me recibes y dime qué modelo eres (si lo sabes)."}])
    
    print("\n=== RESPONSE ===")
    print(response)
    print("================\n")
    
    if "Error" in response:
        print("❌ Test FAILED")
    else:
        print("✅ Test PASSED")

except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
