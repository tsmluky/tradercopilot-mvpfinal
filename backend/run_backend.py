import sys
import os
import asyncio
import uvicorn
from dotenv import load_dotenv

# 1. Force Windows Selector Loop Policy BEFORE anything else
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print("[INFO] Applied WindowsSelectorEventLoopPolicy for asyncpg compatibility.")

if __name__ == "__main__":
    # Ensure env is loaded
    load_dotenv()
    
    print("[INFO] Starting TraderCopilot Backend via run_backend.py...")
    
    # Import app directly to avoid import issues and ensure policy applies
    from main import app
    
    # Run Uvicorn programmatically
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
