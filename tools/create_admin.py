import sys
import os
import asyncio
from dotenv import load_dotenv

# 1. Setup paths and env BEFORE imports
# Adjust path to include 'backend' so imports work
current_dir = os.getcwd()
backend_dir = os.path.join(current_dir, 'backend')
sys.path.append(backend_dir)

# Load environment variables from backend/.env
env_path = os.path.join(backend_dir, '.env')
load_dotenv(env_path)

print(f"Loading env from: {env_path}")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")

# 2. Imports
from database import engine, Base, AsyncSessionLocal
from models_db import User
from core.security import get_password_hash
from sqlalchemy import select

async def main():
    print("Connecting to database...")
    
    # Ensure tables exist (in case this is a fresh fresh DB)
    async with engine.begin() as conn:
        print("Ensuring tables exist...")
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        email = "admin@tradercopilot.com"
        
        # Check if exists
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        
        if user:
            print(f"User {email} already exists. Resetting password...")
            user.hashed_password = get_password_hash("admin")
            await session.commit()
            print("Password updated to 'admin'.")
        else:
            print(f"Creating user {email}...")
            new_user = User(
                email=email,
                hashed_password=get_password_hash("admin"),
                name="Systems Admin",
                role="admin"
            )
            session.add(new_user)
            await session.commit()
            print("User created successfully.")

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")
