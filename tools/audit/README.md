# 🔎 TraderCopilot Audit Suite

This directory contains optional verification scripts used to validate the system's "Sale-Ready" status.

## Contents
- `run_audit_suite.py`: A comprehensive test runner that checks:
    - **Idempotency**: Ensures no duplicate signals are processed.
    - **Concurrency**: Verifies scheduler locking mechanisms.
    - **Security (RBAC)**: Confirms Unauthorized (401) and Forbidden (403) protections.
    - **DB Health**: Checks schema integrity.

## Usage
These scripts are intended for **Development/Auditing** use only. Do not run in Production during high-load periods as they inject test data (though properly scoped to `mock` or `audit` modes).

```bash
# Requires backend running (localhost:8000) for Security tests
python tools/audit/run_audit_suite.py
```

## Safety
- All test data uses specific prefixes (`AUDIT_`) or temporary users that are cleaned up.
- Zero secrets are stored in these scripts.
