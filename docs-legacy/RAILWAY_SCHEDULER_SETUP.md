# 🚂 Railway Deployment - Scheduler Configuration

## Current Status
- ✅ Backend API: Deployed and running
- ✅ Frontend: Deployed and running
- ✅ PostgreSQL Database: Connected
- ❌ **Scheduler: NOT CONFIGURED (needs setup)**

---

## Step-by-Step: Deploy Scheduler to Railway

### Option 1: Using Railway CLI (Recommended)

#### 1. Install Railway CLI
```powershell
# Using npm
npm install -g @railway/cli

# Or download from https://docs.railway.app/develop/cli
```

#### 2. Login to Railway
```powershell
railway login
```

#### 3. Link to your project
```powershell
cd c:\Users\lukx\Desktop\TraderCopilot
railway link
# Select your project from the list
```

#### 4. Add Procfile
Railway needs a `Procfile` to know what processes to run.

Create `Procfile` in the project root:
```
web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
worker: cd backend && python scheduler.py
```

#### 5. Push to Railway
```powershell
git add .
git commit -m "Add scheduler worker process"
git push origin main

# Railway will auto-deploy
```

#### 6. Verify in Railway Dashboard
- Go to https://railway.app/
- Select your project
- You should see TWO processes:
  - `web` (backend API)
  - `worker` (scheduler)

---

### Option 2: Using Railway Dashboard (Alternative)

#### 1. Commit and Push Code
```powershell
git add .
git commit -m "Add RSI Divergence + increase candles to 1000"
git push origin main
```

#### 2. Go to Railway Dashboard
- Navigate to https://railway.app/
- Select your TraderCopilot project
- Click on the backend service

#### 3. Add Worker Process
**IMPORTANT**: Railway doesn't support multiple processes from one service easily.

**Best Approach**: Create a SECOND service for the scheduler.

**Steps**:
1. In your Railway project, click **"+ New"**
2. Select **"GitHub Repo"**
3. Choose the SAME repository (TraderCopilot)
4. Name it: **"tradercopilot-scheduler"**
5. In Settings → Start Command, set:
   ```
   cd backend && python scheduler.py
   ```
6. Copy all environment variables from the backend service:
   - `DATABASE_URL`
   - `DEEPSEEK_API_KEY`
   - Any other env vars
7. Deploy!

---

### Option 3: Single Dyno with Background Task (Quick & Dirty)

Modify `backend/main.py` to run scheduler in background:

```python
import threading
from scheduler import run_scheduler

# At the end of main.py, add:
@app.on_event("startup")
async def startup_event():
    # Run scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
```

Then update `scheduler.py`:

```python
def run_scheduler():
    """Run the scheduler loop"""
    while True:
        try:
            execute_strategies()
        except Exception as e:
            print(f"Scheduler error: {e}")
        time.sleep(60)
```

**Pros**: Single dyno, simple  
**Cons**: Not ideal for production (scheduler stops if API crashes)

---

## Recommended: Option 2 (Separate Scheduler Service)

This is the most robust approach for production.

### Why?
- **Isolation**: If scheduler fails, API still works (and vice versa)
- **Scalability**: Can scale scheduler independently
- **Monitoring**: Separate logs for each service
- **Reliability**: Railway will auto-restart if either crashes

---

## Environment Variables Needed

Both backend AND scheduler need these:

```
DATABASE_URL=postgresql://...  (from Railway PostgreSQL)
DEEPSEEK_API_KEY=sk-...
PYTHON_VERSION=3.10
```

---

## Verify Deployment

### 1. Check Logs
In Railway dashboard:
- Click on scheduler service
- Go to "Deployments" tab
- Check logs for:
  ```
  ✅ Registered strategy: ...
  ✅ Executing strategies...
  ✅ Donchian Breakout V2: Checking...
  ```

### 2. Check Database
Run this locally to verify signals are being generated:

```powershell
.\check_db_signals.ps1
```

You should see recent signals with timestamps from the last few minutes.

### 3. Monitor Performance
```powershell
# Check if strategies are running
.\view_signals.ps1

# See latest signals
.\view_signals.ps1 -Last 10
```

---

## Troubleshooting

### "Module not found" errors
**Fix**: Ensure `requirements.txt` is up to date:

```powershell
cd backend
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### "Database connection failed"
**Fix**: Verify `DATABASE_URL` environment variable is set in BOTH services.

### "Scheduler not executing"
**Fix**: Check scheduler logs for errors. Ensure it's using Railway PostgreSQL (not local SQLite).

---

## Files to Create

I'll create these files for you:
1. ✅ `Procfile` - Process definitions
2. ✅ `railway.json` - Railway config (optional)
3. ✅ `requirements.txt` - Updated dependencies

---

**Next Step**: Choose an option (I recommend Option 2) and I'll guide you through it step by step.
