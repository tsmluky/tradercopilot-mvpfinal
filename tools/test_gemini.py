import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from core.ai_service import get_ai_service
from dotenv import load_dotenv

def test_gemini():
    print("🧪 Testing Gemini Integration...")
    
    # Load env
    load_dotenv(os.path.join('backend', '.env'))
    
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        print("❌ GEMINI_API_KEY not found in .env")
        return
        
    print(f"🔑 Key found: {key[:4]}...{key[-4:]}")
    
    service = get_ai_service()
    print(f"🤖 Provider: {service.__class__.__name__}")
    print(f"   Model: {getattr(service, 'model_name', 'Unknown')}")
    
    print("\n💬 Sending test prompt: 'Hola Gemini, ¿cómo estás?'")
    try:
        response = service.chat([{"role": "user", "content": "Hola Gemini, ¿cómo estás? Responde brevemente."}])
        print(f"\n✅ Response received:\n{response}")
    except Exception as e:
        print(f"\n❌ Error during chat: {e}")

if __name__ == "__main__":
    test_gemini()
