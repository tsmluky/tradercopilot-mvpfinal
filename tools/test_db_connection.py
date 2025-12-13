import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from dotenv import load_dotenv

# Robust .env loading
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "..", "backend", ".env")
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# FORCE PSYCOPG
DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg://")
if "postgresql+psycopg://" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

if "sslmode=require" not in DATABASE_URL:
    sep = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL += f"{sep}sslmode=require"
# Clean up potential asyncpg residue
DATABASE_URL = DATABASE_URL.replace("ssl=require", "")

print(f"Testing URL: {DATABASE_URL}")

async def main():
    try:
        engine = create_async_engine(DATABASE_URL, echo=True)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"✅ Connection Successful! Result: {result.scalar()}")
        await engine.dispose()
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
