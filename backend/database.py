from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import ssl
from dotenv import load_dotenv

# Load .env file FIRST
load_dotenv()

# Railway provides DATABASE_URL for PostgreSQL
# Locally we use SQLite
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.strip()
    print(f"[DB DEBUG] Original URL starts with: {DATABASE_URL[:15]}...")
    
    # Fallback for malformed URLs (e.g. file paths without schema)
    if "://" not in DATABASE_URL:
        print(f"[DB WARNING] DATABASE_URL '{DATABASE_URL}' lacks schema. Assuming SQLite.")
        DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_URL}"
        DATABASE_URL_SYNC = f"sqlite:///{DATABASE_URL.split(':///')[-1]}"
    else:
        # Production (Railway) - PostgreSQL
        # Railway provides postgres:// but SQLAlchemy needs postgresql://
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
        # For async, use postgresql+psycopg://
        # For async, use postgresql+asyncpg://
        if "postgresql://" in DATABASE_URL and "+asyncpg" not in DATABASE_URL:
            DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        # Asyncpg needs explicit SSL context on Windows often
        async_connect_args = {}
        if "rlwy.net" in DATABASE_URL:
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            async_connect_args["ssl"] = ctx

        # Clean up URL params that might conflict
        DATABASE_URL = DATABASE_URL.replace("ssl=require", "")
        DATABASE_URL = DATABASE_URL.replace("sslmode=require", "")

        DATABASE_URL_SYNC = DATABASE_URL.replace("+asyncpg", "")

        # Fix for Railway/Psycopg2: Force sslmode=require
        if "rlwy.net" in DATABASE_URL_SYNC and "sslmode" not in DATABASE_URL_SYNC:
             separator = "&" if "?" in DATABASE_URL_SYNC else "?"
             DATABASE_URL_SYNC += f"{separator}sslmode=require"
    
    print(f"[DB DEBUG] Final Async URL starts with: {DATABASE_URL[:25]}...")
    print(f"[DB] Using Configured Database")
else:
    # Development - SQLite
    DATABASE_URL = "sqlite+aiosqlite:///./tradercopilot.db"
    DATABASE_URL_SYNC = "sqlite:///./tradercopilot.db"
    print(f"[DB] Using SQLite (Development)")

# Ensure DB directory exists for SQLite
if "sqlite" in DATABASE_URL:
    try:
        # Extract path from URL (e.g. sqlite+aiosqlite:///./backend/data/db.sqlite -> ./backend/data)
        db_path = DATABASE_URL.split(":///")[-1]
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"[DB] Created missing directory: {db_dir}")
    except Exception as e:
        print(f"[DB WARNING] Could not ensure DB directory exists: {e}")

# == ASYNC ==
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args=async_connect_args if "postgresql" in DATABASE_URL else {}
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# == SYNC (for save_strict_log and other sync tools) ==
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as sessionmaker_sync

engine_sync = create_engine(
    DATABASE_URL_SYNC,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL_SYNC else {}
)
SessionLocal = sessionmaker_sync(autocommit=False, autoflush=False, bind=engine_sync)


Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
