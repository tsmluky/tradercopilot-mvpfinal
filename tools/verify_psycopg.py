import asyncio
import sys
import os

# 1. Force Loop Policy
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import psycopg

def get_railway_url():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend", ".env")
    with open(env_path, "r") as f:
        for line in f:
            if "shinkansen.proxy.rlwy.net" in line and "DATABASE_URL" in line:
                return line.replace("#", "").replace("DATABASE_URL=", "").strip()
    return None

DB_URL = get_railway_url()
if not DB_URL:
    print("❌ No URL found")
    sys.exit(1)

# Ensure sslmode=require
if "sslmode=require" not in DB_URL:
    sep = "&" if "?" in DB_URL else "?"
    DB_URL += f"{sep}sslmode=require"

print(f"Testing URL: {DB_URL}")

def test_sync():
    print("\n--- Sync Test (psycopg3) ---")
    try:
        with psycopg.connect(DB_URL) as conn:
            print("✅ Sync Connected!")
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                print(f"   Query Result: {cur.fetchone()}")
    except Exception as e:
        print(f"❌ Sync Failed: {e}")

async def test_async():
    print("\n--- Async Test (psycopg3) ---")
    try:
        # Note: psycopg.AsyncConnection is the way in v3
        async with await psycopg.AsyncConnection.connect(DB_URL) as conn:
            print("✅ Async Connected!")
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                print(f"   Query Result: {await cur.fetchone()}")
    except Exception as e:
        print(f"❌ Async Failed: {e}")

if __name__ == "__main__":
    test_sync()
    asyncio.run(test_async())
