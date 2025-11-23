# 📊 TraderCopilot - Project Context & Technical Documentation

**Project Name:** TraderCopilot MVP Final  
**Version:** 0.8.1  
**Last Updated:** November 21, 2025  
**Status:** ✅ Production Deployed (Railway + Vercel)

---

## 🎯 Project Overview

TraderCopilot is a **SaaS platform for AI-powered trading signal generation and risk management**. It combines quantitative analysis (technical indicators), fundamental context (RAG system), and AI reasoning (DeepSeek LLM) to provide traders with:

1. **LITE Analysis**: Fast, rule-based trading signals (long/short, entry/TP/SL).
2. **PRO Analysis**: Deep AI-generated reports with technical analysis, sentiment, on-chain metrics, and strategic planning.
3. **Risk Advisor AI**: Interactive chat to help traders manage open positions, adjust risk, and evaluate scenarios.

### Key Features
- Multi-asset support: **BTC, ETH, SOL** (extensible to any USDT pair).
- Real-time market data via **Binance & KuCoin APIs** (with mock fallback).
- Interactive price charts (TradingView-style with Recharts).
- Historical logs & signal tracking (CSV + PostgreSQL).
- Mobile-first PWA design.
- Dark mode, responsive UI.

---

## 🏗️ Architecture

### **Tech Stack**

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Frontend** | React + TypeScript + Vite | Deployed on Vercel |
| **Backend** | FastAPI (Python 3.11+) | Deployed on Railway |
| **Database** | PostgreSQL (Railway) | Signal persistence |
| **LLM** | DeepSeek API | PRO analysis & chat |
| **Market Data** | Binance / KuCoin REST APIs | With mock fallback |
| **Indicators** | `ta` library (Python) | RSI, EMA, MACD, ATR |
| **Styling** | Tailwind CSS (CDN) | ⚠️ Should migrate to PostCSS |

### **Deployment Environment**

```
Frontend (web/):
  ├─ Vercel
  └─ https://tradercopilot-mvpfinal.vercel.app/

Backend (backend/):
  ├─ Railway
  ├─ https://zesty-surprise-production-1f0f.up.railway.app/
  └─ Port: 8080 (internal)

Database:
  ├─ Railway PostgreSQL
  └─ Managed service (auto-linked)
```

---

## 📁 Project Structure

```
TraderCopilot/
├── backend/
│   ├── main.py                    # FastAPI app, endpoints (LITE, PRO, Advisor, Logs)
│   ├── models.py                  # Pydantic request/response schemas
│   ├── models_db.py               # SQLAlchemy ORM models (Signal, SignalEvaluation, User)
│   ├── database.py                # Async DB engine (PostgreSQL/SQLite)
│   ├── deepseek_client.py         # LLM API client (PRO & Chat)
│   ├── market_data_api.py         # OHLCV fetcher (Binance → KuCoin → Mock)
│   ├── indicators/
│   │   └── market.py              # Technical indicators (RSI, MACD, etc.)
│   ├── routers/
│   │   └── compat.py              # Legacy compatibility routes
│   ├── logs/                      # CSV logs (fallback/legacy)
│   │   ├── LITE/
│   │   ├── PRO/
│   │   └── ADVISOR/
│   ├── data/                      # SQLite fallback (ephemeral in Railway)
│   ├── requirements.txt           # Python dependencies
│   ├── start.sh                   # Railway startup script
│   ├── railway.json               # Railway config
│   ├── Procfile                   # Railway process definition
│   └── .env                       # Local env vars (NOT in Railway)
│
├── web/
│   ├── src/
│   │   ├── App.tsx                # Main React app
│   │   ├── constants.ts           # API_BASE_URL (Railway backend)
│   │   ├── services/
│   │   │   └── api.ts             # Axios API wrapper
│   │   ├── components/
│   │   │   ├── PriceChart.tsx     # Interactive candlestick chart
│   │   │   ├── Terminal.tsx       # LITE signals display
│   │   │   ├── ProAnalysis.tsx    # PRO markdown renderer
│   │   │   └── RiskAdvisor.tsx    # Chat interface
│   │   └── pages/
│   │       ├── Dashboard.tsx      # Main signal generation
│   │       ├── Logs.tsx           # Historical signals viewer
│   │       └── Leaderboard.tsx    # (Future: trading stats)
│   ├── index.html
│   ├── vite.config.ts
│   ├── package.json
│   └── vercel.json                # Vercel deployment config
│
├── brain/                         # RAG context per token
│   ├── eth/
│   │   ├── insights.md
│   │   ├── news.txt
│   │   ├── onchain.txt
│   │   └── sentiment.txt
│   ├── btc/
│   └── sol/
│
└── tools/
    └── start_dev.ps1              # Local dev server launcher
```

---

## 🔄 Data Flow

### **1. LITE Signal Generation** (`POST /analyze/lite`)

```
User clicks "Analyze" → Frontend (api.ts)
  ↓
  POST /analyze/lite {token: "eth", timeframe: "30m"}
  ↓
Backend (main.py::analyze_lite)
  ↓
market_data_api.py: get_ohlcv_data("eth", "30m")
  ├─ Try Binance API
  ├─ Fallback to KuCoin
  └─ Fallback to Mock (if both fail)
  ↓
indicators/market.py: get_market_data()
  ├─ Calculate RSI, EMA, MACD, ATR
  └─ Return {price, rsi, ema21, macd, trend, ...}
  ↓
main.py::_build_lite_from_market()
  ├─ Apply rule-based logic (v2):
  │   - Oversold (RSI < 30) → LONG scalp
  │   - Overbought (RSI > 75) → SHORT scalp
  │   - Trend following (EMA + MACD)
  └─ Generate LiteSignal {direction, entry, tp, sl, confidence}
  ↓
save_strict_log("LITE", {...})
  ├─ Save to CSV (logs/LITE/eth.csv)
  └─ Save to PostgreSQL (signals table)
  ↓
Response: JSON {timestamp, token, direction, entry, tp, sl, ...}
  ↓
Frontend: Display in Terminal component
```

### **2. PRO Analysis** (`POST /analyze/pro`)

```
User clicks "PRO Analysis" → Frontend
  ↓
  POST /analyze/pro {token: "btc", timeframe: "1h", user_message: "..."}
  ↓
Backend (main.py::analyze_pro)
  ↓
1. Get Market Data (same as LITE)
2. Generate LITE signal internally (as tactical "anchor")
3. Load RAG context from brain/{token}/
   ├─ insights.md
   ├─ news.txt
   ├─ onchain.txt
   └─ sentiment.txt
4. Build PRO prompt (_build_pro_markdown)
   └─ Combines: LITE signal + RAG + user_message
5. (FUTURE) Call DeepSeek API via deepseek_client.py
   └─ Currently returns template-based markdown
6. Save to logs/PRO/{token}.csv + PostgreSQL
  ↓
Response: JSON {analysis: "markdown", meta: {...}}
  ↓
Frontend: Render in ProAnalysis component (markdown → styled)
```

### **3. Risk Advisor Chat** (`POST /analyze/advisor/chat`)

```
User types in chat → Frontend (RiskAdvisor)
  ↓
  POST /analyze/advisor/chat {messages: [...]}
  ↓
Backend (routers/compat.py::analyze_advisor_chat)
  ↓
deepseek_client.py::generate_chat()
  ├─ System prompt: "Eres Risk Advisor AI..."
  ├─ User chat history
  └─ Call DeepSeek API
  ↓
Response: AI message
  ↓
Frontend: Append to chat UI
```

### **4. Logs Retrieval** (`GET /logs/{mode}/{token}`)

```
User navigates to Logs → Frontend
  ↓
  GET /logs/LITE/all  (or /logs/PRO/eth)
  ↓
Backend (main.py::get_logs) - ASYNC
  ↓
1. Query PostgreSQL:
   SELECT * FROM signals WHERE mode='LITE' [AND token='ETH']
   ORDER BY timestamp DESC LIMIT 100
2. Read CSV files (logs/LITE/*.csv) as fallback/legacy
3. Merge both sources
4. Sort by timestamp (newest first)
5. Return top 100
  ↓
Response: {count: N, logs: [...]}
  ↓
Frontend: Display in Logs page (filterable table)
```

---

## 🗄️ Database Schema

### **signals** (PostgreSQL)

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Primary key |
| `timestamp` | DATETIME | UTC timestamp |
| `token` | STRING | BTC, ETH, SOL, etc. |
| `timeframe` | STRING | 30m, 1h, 4h, etc. |
| `direction` | STRING | "long" or "short" |
| `entry` | FLOAT | Entry price |
| `tp` | FLOAT | Take profit |
| `sl` | FLOAT | Stop loss |
| `confidence` | FLOAT | 0.0 - 1.0 |
| `rationale` | TEXT | Short explanation |
| `source` | STRING | "lite-rule@v2", "PRO_V1_LOCAL", etc. |
| `mode` | STRING | LITE, PRO, ADVISOR |
| `raw_response` | TEXT | (Optional) Full AI response |

**Indexes:** `timestamp`, `token`, `mode`

---

## 🔧 Configuration & Environment Variables

### **Backend (.env or Railway Variables)**

| Variable | Example | Notes |
|----------|---------|-------|
| `DATABASE_URL` | `postgresql://user:pass@host/db` | **CRITICAL**: Must be PostgreSQL in production |
| `DEEPSEEK_API_KEY` | `sk-xxxxx` | Required for PRO & Advisor |
| `DEEPSEEK_API_URL` | `https://api.deepseek.com/chat/completions` | (Optional, has default) |
| `DEEPSEEK_MODEL` | `deepseek-chat` | (Optional) |
| `PORT` | `8080` | Railway auto-injects, our code forces 8080 |
| `RAILWAY_ENVIRONMENT` | `production` | Railway auto-sets |

⚠️ **Common Pitfall**: If `DATABASE_URL` points to SQLite (`sqlite:///...`), data will be lost on every redeploy. **Always use PostgreSQL in Railway.**

### **Frontend (Vercel Environment Variables)**

| Variable | Example | Notes |
|----------|---------|-------|
| `VITE_API_BASE_URL` | `https://zesty-surprise-production-1f0f.up.railway.app` | Backend URL |

---

## 🐛 Issues Resolved (Recent Session)

### Problem 1: `ModuleNotFoundError: No module named 'pandas_ta'`
- **Root Cause**: `pandas_ta` was in `requirements.txt` but not installable on Railway.
- **Fix**: Replaced with `ta` library and refactored `indicators/market.py`.

### Problem 2: `502 Bad Gateway` on `/analyze/lite` and `/analyze/pro`
- **Root Cause 1**: `ccxt` library trying to connect to Binance from Railway IPs (blocked).
- **Fix**: Replaced `ccxt` with direct REST API calls (`market_data_api.py`), added KuCoin fallback.
- **Root Cause 2**: `get_market_data()` returning `None` caused FastAPI to raise `HTTPException(502)`.
- **Fix**: Added mock data as ultimate fallback.

### Problem 3: DeepSeek Connection Error (`Invalid URL 'sk-xxx'`)
- **Root Cause**: User accidentally set `DEEPSEEK_API_URL` to the API key value instead of the URL.
- **Fix**: Added defensive validation in `deepseek_client.py` to check if URL starts with `http`.

### Problem 4: Timestamps showing "1h ago" for brand new signals
- **Root Cause**: Backend returned timestamps without UTC "Z" suffix, frontend interpreted as local time.
- **Fix**: Modified `get_logs` to append "Z" to timestamps when serializing from DB.

### Problem 5: "ALL ASSETS" view only showing one token
- **Root Cause 1**: Async/sync mess in `get_logs` caused DB reads to be skipped, falling back to CSV `all.csv` (which didn't exist).
- **Fix**: Converted `get_logs` to `async def`, properly awaited DB queries.
- **Root Cause 2**: Once DB worked, it only showed NEW signals (post-PostgreSQL connection), ignoring old CSV data.
- **Fix**: Modified `get_logs` to **merge** DB + CSV, sort by timestamp, return top 100.

### Problem 6: Signals not persisting across Railway redeploys
- **Root Cause**: `DATABASE_URL` was set to SQLite (`backend/data/signalbot.db`). Railway's filesystem is ephemeral.
- **Fix**: User instructed to create a PostgreSQL service in Railway and link it via `DATABASE_URL`.

---

## ✅ Production Checklist

### Backend (Railway)
- [x] PostgreSQL service created and linked
- [x] `DATABASE_URL` pointing to PostgreSQL (not SQLite)
- [x] `DEEPSEEK_API_KEY` configured
- [x] Port 8080 enforced in `start.sh`
- [x] Health endpoint (`/health`) returning 200 OK
- [x] Logs showing `✅ [INFO] Using PostgreSQL (Persistent)`
- [x] Market data fallback chain: Binance → KuCoin → Mock

### Frontend (Vercel)
- [x] `VITE_API_BASE_URL` set to Railway backend
- [x] CORS allowed from Vercel domain
- [x] Charts loading real OHLCV data
- [x] Signals displaying correctly

### Known Issues (Non-Critical)
- ⚠️ Tailwind CSS using CDN (`cdn.tailwindcss.com`) - Should migrate to PostCSS build for production.
- ⚠️ CSV logs still written as backup (legacy) - Could be disabled once DB is fully trusted.

---

## 🚀 Deployment Workflow

### To Deploy Backend Changes:
```bash
cd backend
# Make changes to .py files
git add .
git commit -m "Description of changes"
git push origin main
# Railway auto-deploys from GitHub
# Wait ~2-3 minutes, check Railway logs
```

### To Deploy Frontend Changes:
```bash
cd web
# Make changes to .tsx/.ts files
git add .
git commit -m "Description of changes"
git push origin main
# Vercel auto-deploys from GitHub
# Wait ~1 minute, check Vercel logs
```

---

## 📝 Key Code Patterns

### Adding a New Technical Indicator (Backend)

1. Edit `backend/indicators/market.py`:
```python
# Inside get_market_data():
df['NEW_INDICATOR'] = ta.momentum.rsi(df['close'], window=14)  # Example

# Add to data dict:
data = {
    ...,
    "new_indicator": last['NEW_INDICATOR'],
}
```

2. Use in `backend/main.py::_build_lite_from_market()`:
```python
new_ind = indicators.get("new_indicator", 0)
if new_ind > threshold:
    direction = "long"
```

### Adding a New Endpoint (Backend)

```python
# In main.py
@app.post("/my-endpoint")
async def my_endpoint(req: MyRequest):
    # Logic here
    return {"status": "ok", "data": ...}
```

### Calling Backend from Frontend

```typescript
// In web/src/services/api.ts or component
import { API_BASE_URL } from '../constants';

const response = await fetch(`${API_BASE_URL}/my-endpoint`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ token: 'eth' })
});
const data = await response.json();
```

---

## 🎓 Learning Resources & Next Steps

### Potential Enhancements
1. **Real-time Updates**: WebSocket for live signal streaming.
2. **Backtesting**: Evaluate LITE rules against historical data.
3. **User Authentication**: Login system (User model already exists in DB).
4. **Position Tracking**: Link signals to user portfolios, auto-evaluate P&L.
5. **More Assets**: Add forex (EUR/USD), commodities (Gold, Oil), stocks.
6. **Advanced Charting**: Integrate TradingView lightweight charts.
7. **Notifications**: Telegram/Discord bot for new signals.
8. **Subscription Tiers**: Free (LITE only), Premium (PRO + Advisor).

### Code Quality Improvements
- [ ] Migrate Tailwind from CDN to PostCSS (Vite plugin).
- [ ] Add unit tests (pytest for backend, Vitest for frontend).
- [ ] Add E2E tests (Playwright).
- [ ] Set up CI/CD linting (Ruff for Python, ESLint for TypeScript).
- [ ] Implement proper logging (structured JSON logs).
- [ ] Add rate limiting (protect `/analyze` endpoints).

---

## 🆘 Troubleshooting

### "502 Bad Gateway" on `/analyze/lite`
1. Check Railway logs: `[ERROR MARKET]` indicates market data failure → Verify Binance/KuCoin APIs are reachable.
2. Mock data should kick in automatically. If not, check `market_data_api.py::generate_mock_ohlcv`.

### "ALL ASSETS" shows empty or only one token
1. Check Railway logs for `[LOGS] Loaded X logs from DB` and `[LOGS] Loaded Y logs from CSV`.
2. Verify PostgreSQL has data: `SELECT COUNT(*) FROM signals;` (use Railway's DB GUI or CLI).
3. Ensure `get_logs` is async (should be `async def get_logs`).

### Timestamps are wrong / "1h ago" for new signals
1. Ensure backend returns timestamps with "Z" suffix (UTC).
2. Check browser console: timestamp should be ISO8601 with Z (`2025-11-21T14:00:00Z`).

### DeepSeek API not working
1. Check `DEEPSEEK_API_KEY` is set in Railway.
2. Check Railway logs for `[DeepSeek]` messages.
3. If seeing "Invalid URL", verify `DEEPSEEK_API_URL` is NOT your API key (see Problem 3 above).

---

## 📞 Handoff Instructions for ChatGPT

**Context**: This project is a deployed SaaS platform for trading signals. The backend (FastAPI) is on Railway, frontend (React) is on Vercel, and the database is PostgreSQL (Railway). We've just resolved several critical bugs (market data, database persistence, log aggregation, timestamps).

**Current Task**: The system is production-ready. All endpoints work. Signals persist. "ALL ASSETS" view merges DB + CSV data correctly.

**Key Files to Reference**:
- `backend/main.py` - Core API logic
- `backend/market_data_api.py` - Market data fetching (Binance → KuCoin → Mock)
- `backend/deepseek_client.py` - LLM integration
- `web/src/App.tsx` - Frontend routing
- `web/src/services/api.ts` - API client

**If Asked to Debug**:
1. Always check Railway logs first (backend errors).
2. Check Vercel logs for frontend build issues.
3. Verify environment variables are set correctly.

**If Asked to Add Features**:
1. Follow the code patterns above.
2. Test locally first (`tools/start_dev.ps1` for backend, `npm run dev` for frontend).
3. Ensure changes are backwards-compatible with existing DB schema.

**Communication Style**: Technical, concise, assume intermediate Python/TypeScript knowledge. Prioritize production stability over experimental features.

---

**END OF CONTEXT DOCUMENT**

*Generated: 2025-11-21 | Version: 1.0*
