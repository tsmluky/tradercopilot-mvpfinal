from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Railway provides DATABASE_URL for PostgreSQL
# Locally we use SQLite
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.strip()
    print(f"[DB DEBUG] Original URL starts with: {DATABASE_URL[:15]}...")
    
    # Production (Railway) - PostgreSQL
    # Railway provides postgres:// but SQLAlchemy needs postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # For async, use postgresql+asyncpg://
    if "postgresql://" in DATABASE_URL and "+asyncpg" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    print(f"[DB DEBUG] Final Async URL starts with: {DATABASE_URL[:25]}...")
    
    DATABASE_URL_SYNC = DATABASE_URL.replace("+asyncpg", "")
    print(f"[DB] Using PostgreSQL (Production)")
else:
    # Development - SQLite
    DATABASE_URL = "sqlite+aiosqlite:///./tradercopilot.db"
    DATABASE_URL_SYNC = "sqlite:///./tradercopilot.db"
    print(f"[DB] Using SQLite (Development)")

# == ASYNC ==
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
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
