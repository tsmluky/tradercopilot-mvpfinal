import sys
import os
import asyncio
from sqlalchemy.future import select

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

async def fix_auth():
    print("🚀 Starting Auth Fix...")
    try:
        from database import AsyncSessionLocal, engine, Base
        from models_db import User
        from core.security import get_password_hash
        
        # 1. Ensure Tables Exist
        print("🛠️  Ensuring tables exist...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables checked/created.")
        
        # 2. Check/Create User
        async with AsyncSessionLocal() as session:
            email = "admin@tradercopilot.com"
            print(f"👤 Checking user {email}...")
            
            result = await session.execute(select(User).where(User.email == email))
            user = result.scalars().first()
            
            if user:
                print("✅ Admin user already exists.")
                # Force reset password to be sure
                print("🔄 Resetting password to 'admin'...")
                user.hashed_password = get_password_hash("admin")
                session.add(user)
                await session.commit()
                print("✅ Password reset.")
                
            else:
                print("⚠️  Admin user missing. Creating...")
                new_user = User(
                    email=email,
                    hashed_password=get_password_hash("admin"),
                    name="Administrator",
                    role="admin"
                )
                session.add(new_user)
                await session.commit()
                print("✅ Admin user created successfully.")

            # Create Demo User too
            email_demo = "demo@tradercopilot.com"
            result = await session.execute(select(User).where(User.email == email_demo))
            demo = result.scalars().first()
            if not demo:
                 print("👤 Creating demo user...")
                 bg_user = User(email=email_demo, hashed_password=get_password_hash("demo"), name="Demo", role="user")
                 session.add(bg_user)
                 await session.commit()
                 print("✅ Demo user created.")
            else:
                 print("✅ Demo user exists. Resetting password...")
                 demo.hashed_password = get_password_hash("demo")
                 session.add(demo)
                 await session.commit()
                 print("✅ Demo password reset.")

    except Exception as e:
        print(f"❌ Error during Auth Fix: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(fix_auth())
