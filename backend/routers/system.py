from fastapi import APIRouter
from database import engine, Base
import os
import shutil

router = APIRouter()

@router.post("/reset")
def system_reset():
    """
    FACTORY RESET: Borra la base de datos y logs.
    """
    print("!!! INITIATING FACTORY RESET !!!")
    
    # 1. Drop tables
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("DB Tables dropped and recreated.")
    except Exception as e:
        print(f"Error resetting DB: {e}")

    # 2. Clear Logs CSV Folder
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    if os.path.exists(logs_dir):
        try:
            shutil.rmtree(logs_dir)
            os.makedirs(logs_dir, exist_ok=True)
            print("Logs folder wiped.")
        except Exception as e:
            print(f"Error wiping logs: {e}")
            
    return {"status": "ok", "message": "System Factory Reset Complete"}

@router.get("/health")
def health_check():
    return {"status": "ok", "db": "connected"}
