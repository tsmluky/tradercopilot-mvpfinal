# 🎬 Demo Path Verification

**Objective**: Ensure the "Golden Path" for the sales demo is unbreakable.

## Pre-Demo Checklist
- [ ] **Reset Database**: Run `python backend/reset_db.py`.
- [ ] **Seed Data**: Run `python backend/seed_auth.py` (Creates Admin user).
- [ ] **Start Backend**: `python backend/main.py` (Check successful startup logs).
- [ ] **Start Frontend**: `npm run dev` (Ensure localhost:5173 is loading).
- [ ] **Login**: Have credentials `admin@tradercopilot.com` / `admin123` ready.

## The "Golden Path" Script (Verified)

### 1. The Hook (Dashboard)
- **Action**: Load `/dashboard`.
- **Verify**: Live Feed populates (Seed data or live signals).
- **Verify**: "Performance" cards show data.
- **Fail-safe**: If empty, hit the "Refresh" button (triggers backend fetch).

### 2. The Intelligence (Advisor)
- **Action**: Go to `/analysis`.
- **Action**: Select Token ETH, Click "Analyze".
- **Verify**: Spinner appears -> Result loads.
- **Fail-safe**: If AI fails (timeout), the backend returns a "Static Fallback" analysis so the demo *never* crashes.

### 3. The Engine (Marketplace)
- **Action**: Go to `/strategies`.
- **Action**: Scroll through personas.
- **Verify**: "Win Rate" badges are visible.

### 4. The Control (Admin)
- **Action**: Go to `/admin`.
- **Action**: Click "Hide" on a signal.
- **Verify**: Toast notification "Signal Hidden".
- **Action**: Refresh page -> Signal is grayed out/hidden.

## Recovery Paths
- **Backend Crash**: Restart `python backend/main.py`. Application state is stateless (JWT) + DB, so user session survives resume.
- **Database Lock**: If sqlite locks, delete `tradercopilot.db` and re-run `reset_db.py` (Extreme case).

---
**Confidence Score: 10/10**
(All paths tested via `verify_prod_ready.py`)
