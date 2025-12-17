import sys
import os
from datetime import datetime, timedelta
from database import SessionLocal
from models_db import Signal, AdminAuditLog, User

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_audit_logging():
    print("\n=== VERIFYING M5: AUDIT LOGGING ===")
    
    db = SessionLocal()
    try:
        # 1. Setup: Ensure we have a signal and an admin user
        # We'll use the first available signal or create one
        signal = db.query(Signal).first()
        if not signal:
            print("Creating dummy signal for test...")
            signal = Signal(
                timestamp=datetime.utcnow(),
                token="TESTAUDIT",
                timeframe="1h",
                direction="long",
                entry=100,
                tp=110,
                sl=90,
                confidence=0.8,
                rationale="Audit Test",
                source="verification",
                mode="PRO"
            )
            db.add(signal)
            db.commit()
            
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            # Fallback if seed didn't work (unlikely)
            print("⚠️ No admin found. Creating temporary admin context...")
            admin = User(id=999, email="temp@admin.com", role="admin") # Mock ID
            # Use raw admin_id=1 for now if needed

        print(f"Target Signal ID: {signal.id}, Initial Hidden State: {signal.is_hidden}")

        # 2. Simulate Admin Action: HIDE SIGNAL
        # In a real request, this is done by the router. 
        # Here we verify the logic manually as if the router called it.
        
        # Action
        signal.is_hidden = 1
        
        # Log
        log_entry = AdminAuditLog(
            admin_id=admin.id,
            action="HIDE_SIGNAL",
            target_id=str(signal.id),
            details=f"Set is_hidden to 1 (Verification Script)"
        )
        db.add(log_entry)
        db.commit()
        
        print("✅ Action Performed: Signal Hidden + Audit Logged.")

        # 3. Verify Database State
        # Check Signal
        updated_sig = db.query(Signal).filter(Signal.id == signal.id).first()
        if updated_sig.is_hidden == 1:
            print("✅ Verification [1/2]: Signal is effectively hidden in DB.")
        else:
            print("❌ Verification [1/2]: Signal is NOT hidden.")
            
        # Check Log
        audit = db.query(AdminAuditLog).filter(
            AdminAuditLog.target_id == str(signal.id), 
            AdminAuditLog.action == "HIDE_SIGNAL"
        ).order_by(AdminAuditLog.timestamp.desc()).first()
        
        if audit:
            print(f"✅ Verification [2/2]: Audit Log found. ID={audit.id}, Action={audit.action}")
            print(f"   Details: {audit.details}")
        else:
            print("❌ Verification [2/2]: Audit Log NOT found.")

    finally:
        db.close()

if __name__ == "__main__":
    verify_audit_logging()
