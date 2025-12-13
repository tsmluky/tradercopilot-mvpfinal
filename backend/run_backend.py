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
    
    # Run Uvicorn programmatically
    # We use "main:app" string to enable reload support if needed, but here simple start
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Useful for dev
        log_level="info"
    )
