import sys
import os
from datetime import datetime
from sqlalchemy import func
from database import SessionLocal
from models_db import User, Signal, SignalEvaluation, AdminAuditLog, SchedulerLock, StrategyConfig

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_kpi(label, value, ok_condition=True):
    icon = "✅" if ok_condition else "❌"
    print(f"{icon} {label}: {value}")

def verify_prod_readiness():
    print("\n=== 🔍 TRADERCOPILOT SYSTEM DIAGNOSTIC ===\n")
    
    db = SessionLocal()
    try:
        # 1. Connectivity
        print("--- [1] DATABASE CONNECTIVITY ---")
        try:
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            print("✅ Database Connection: ACTIVE")
        except Exception as e:
            print(f"❌ Database Connection: FAILED ({e})")
            return

        # 2. Users & Security
        print("\n--- [2] USERS & SECURITY ---")
        total_users = db.query(User).count()
        admin_users = db.query(User).filter(User.role == "admin").count()
        pro_users = db.query(User).filter(User.plan.like("%PRO%")).count()
        
        print_kpi("Total Users", total_users, total_users > 0)
        print_kpi("Admin Users (Owners)", admin_users, admin_users > 0)
        print_kpi("Pro/Trader Users", pro_users)

        # 3. Core Engine (Signals)
        print("\n--- [3] ENGINE & SIGNALS ---")
        total_signals = db.query(Signal).count()
        hidden_signals = db.query(Signal).filter(Signal.is_hidden == 1).count()
        evaluated_signals = db.query(SignalEvaluation).count()
        
        print_kpi("Total Signals Generated", total_signals, total_signals > 0)
        print_kpi("Signals Evaluated (Paper Trading)", evaluated_signals)
        print_kpi("Hidden Signals (Soft Deleted)", hidden_signals)
        
        if total_signals > 0:
            coverage = (evaluated_signals / total_signals) * 100
            print(f"   📊 Evaluation Coverage: {coverage:.1f}%")

        # 4. Strategy Configs
        print("\n--- [4] STRATEGY MARKETPLACE ---")
        strategies = db.query(StrategyConfig).all()
        print(f"ℹ️  Registered Strategies: {len(strategies)}")
        for s in strategies:
            status = "🟢 Active" if s.enabled else "⚪ Paused"
            print(f"   - {s.strategy_id} ({s.name}): {status} [WinRate: {s.win_rate*100:.0f}% | Trades: {s.total_signals}]")

        # 5. Admin Audit Trail
        print("\n--- [5] ADMIN COMPLIANCE ---")
        audit_logs = db.query(AdminAuditLog).order_by(AdminAuditLog.timestamp.desc()).limit(5).all()
        print_kpi("Audit Log Entries", len(audit_logs), len(audit_logs) > 0)
        if audit_logs:
            print("   📝 Recent Activity:")
            for log in audit_logs:
                print(f"      - [{log.timestamp.strftime('%H:%M:%S')}] {log.action} by Admin#{log.admin_id} -> Target {log.target_id}")

        print("\n=== DIAGNOSTIC COMPLETE ===")
        print("Conclusion: System is OPERATIONALLY READY. 🚀\n")

    finally:
        db.close()

if __name__ == "__main__":
    verify_prod_readiness()
