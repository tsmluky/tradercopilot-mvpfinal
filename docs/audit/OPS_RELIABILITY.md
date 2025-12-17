# ⚙️ Ops Reliability Review

## Idempotency
- **Mechanism**: `models_db.Signal.idempotency_key` (Unique Constraint).
- **Composition**: `strategy_id | token | timeframe | timestamp | user_id | mode` (Cross-Tenant Safe).
- **Behavior**:
    - First Write: SUCCESS (200/201).
    - Second Write: IGNORED (Graceful catch of IntegrityError, logs warning, returns "OK").
- **Verification**: `tools/audit/run_audit_suite.py` verified Idempotency + Collision safety.

## Scheduler Stability
- **Concurrency Control**: Distributed DB Lock (`SchedulerLock` table).
- **TTL**: 30 seconds.
- **Scenario: Double Instance**:
    - Instance A holds lock.
    - Instance B sees valid lock -> Sleeps.
    - **Verified**: `run_audit_suite.py` simulation confirmed B waits.
- **Scenario: Crash**:
    - Instance A dies.
    - 30s later, Lock expires.
    - Instance B takes over.
    - **Verified**: `run_audit_suite.py` confirmed expiration logic.

## Health Probes
- `/health`: App operational.
- `/ready`: DB connection check (`SELECT 1`).
- **Status**: Both endpoints active.
