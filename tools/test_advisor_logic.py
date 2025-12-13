import sys
import os
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from routers.advisor import advisor_chat, ChatRequest, ChatMessage, ChatContext
from core.ai_service import get_ai_service

# Mock dependencies if needed, or rely on real ones if configured
# For this test, we accept real deps but handle potential DB connection errors gracefully

def test_advisor_logic():
    print("🔬 Testing Advisor Chat Logic...")
    
    # Load env
    load_dotenv(os.path.join('backend', '.env'))
    
    # Check AI Provider
    service = get_ai_service()
    print(f"🤖 AI Service: {service.__class__.__name__}")
    if hasattr(service, 'model_name'):
        print(f"   Model: {service.model_name}")

    # Construct request
    # Context: BTC 1h
    req = ChatRequest(
        messages=[
            ChatMessage(role="user", content="¿Cómo ves el mercado de Bitcoin hoy? ¿Es buen momento para entrar?")
        ],
        context=ChatContext(
            token="BTC",
            timeframe="1h",
            signal_data={"direction": "long", "entry": 98000, "confidence": 0.85}
        )
    )
    
    print("\n📩 Sending Request:")
    print(f"   User: {req.messages[0].content}")
    print(f"   Context: {req.context.token} {req.context.timeframe}")
    
    try:
        response = advisor_chat(req)
        reply_text = response['reply']
        with open("advisor_reply.txt", "w", encoding="utf-8") as f:
            f.write(reply_text)
        print(f"\n✅ Advisor Reply:\n{'-'*60}\n{reply_text[:200]}...\n{'-'*60}")
        print("   (Full reply saved to advisor_reply.txt)")
    except Exception as e:
        error_msg = str(e)
        logger_path = "advisor_error.txt"
        with open(logger_path, "w", encoding="utf-8") as f:
            f.write(error_msg)
        print(f"\n❌ Error logged to {logger_path}")
        print(f"   Snippet: {error_msg[:100]}...")

if __name__ == "__main__":
    test_advisor_logic()
