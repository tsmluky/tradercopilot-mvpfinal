import socket
import ssl
import os
import sys
import asyncio
from urllib.parse import urlparse

# Manual DATABASE_URL prompt because .env might be commented out
# Or we can try to parse it manually from the file text if needed.
# For now, I'll ask the script to read the *commented* one if active is generic.

def get_railway_url():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend", ".env")
    with open(env_path, "r") as f:
        for line in f:
            if "shinkansen.proxy.rlwy.net" in line:
                # remove # and whitespace
                return line.replace("#", "").replace("DATABASE_URL=", "").strip()
    return None

DB_URL = get_railway_url()
if not DB_URL:
    print("❌ Could not find Railway URL in .env")
    sys.exit(1)

print(f"Target: {DB_URL}")
parsed = urlparse(DB_URL)
HOST = parsed.hostname
PORT = parsed.port or 5432
USER = parsed.username
PASS = parsed.password
DBNAME = parsed.path.lstrip("/")

print(f"\n--- 1. TCP Connection Test ({HOST}:{PORT}) ---")
try:
    sock = socket.create_connection((HOST, PORT), timeout=5)
    print("✅ TCP Socket Connected!")
    sock.close()
except Exception as e:
    print(f"❌ TCP Connection Failed: {e}")

print(f"\n--- 2. SSL Handshake Test ---")
try:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    sock = socket.create_connection((HOST, PORT), timeout=5)
    ssock = context.wrap_socket(sock, server_hostname=HOST)
    print(f"✅ SSL Handshake Success! Cipher: {ssock.cipher()}")
    ssock.close()
except Exception as e:
    print(f"❌ SSL Failed: {e}")

print(f"\n--- 3. Psycopg (Sync) Test ---")
try:
    import psycopg
    conn_str = f"host={HOST} port={PORT} dbname={DBNAME} user={USER} password={PASS} sslmode=require"
    conn = psycopg.connect(conn_str)
    print("✅ Psycopg SYNC Connected!")
    conn.close()
except Exception as e:
    print(f"❌ Psycopg SYNC Failed: {e}")

print(f"\n--- 4. Asyncpg Test ---")
async def test_asyncpg():
    try:
        import asyncpg
        # Try default
        print("   > Attempting default asyncpg connect...")
        conn = await asyncpg.connect(DB_URL, ssl="require")
        print("✅ Asyncpg Connected!")
        await conn.close()
    except Exception as e:
        print(f"   > Asyncpg Defaults Failed: {e}")
        
        # Try with custom context
        try:
            print("   > Attempting asyncpg with custom SSL Context...")
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            conn = await asyncpg.connect(DB_URL, ssl=ctx)
            print("✅ Asyncpg (Custom SSL) Connected!")
            await conn.close() 
        except Exception as ex2:
            print(f"❌ Asyncpg Custom SSL Failed: {ex2}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_asyncpg())
