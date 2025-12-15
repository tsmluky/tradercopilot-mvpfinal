
import asyncio
import os
import sys

# Windows asyncio policy
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
load_dotenv()

print("1. Importing main...")
try:
    from main import startup
    print("SUCCESS: Imported main.startup")
except Exception as e:
    print(f"FAIL: Import error: {e}")
    sys.exit(1)

print("2. Running startup event...")
async def run_test():
    try:
        await startup()
        print("SUCCESS: Startup event completed (DB Connected).")
    except Exception as e:
        print(f"FAIL: Startup error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_test())
