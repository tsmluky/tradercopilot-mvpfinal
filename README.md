# TraderCopilot 🚀
**AI-Powered Institutional Trading Intelligence**

TraderCopilot is a next-generation trading platform that combines **Quantitative Analysis**, **Autonomous Strategies**, and **Generative AI** into a unified workspace. It is designed to empower traders with real-time insights, automated signal execution, and deep market intelligence.

![Dashboard Preview](./docs/dashboard_preview.png)

## 🌟 Key Features

### 1. 🧠 AI Signal Hub
- **Hybrid Intelligence**: Fuses mathematical indicators (RSI, MACD, BB) with AI logic.
- **Real-Time Feed**: Live signal stream with confidence scores and RAG-enriched rationale.
- **DeepSeek Integration**: "Ask Advisor" feature enables conversational analysis of any asset.

### 2. 🤖 Strategy Marketplace
- **Autonomous Personas**: Pre-configured strategies (e.g., *Titan BTC*, *The Scalper*) that run 24/7.
- **Paper Trading Engine**: Real-time evaluation of signals against live market data.
- **Verified Performance**: Strategies display dynamic "Win Rate" and "Total Signals" based on tracking.

### 3. 🛡️ Admin & Logic Control
- **God-Mode Dashboard**: Full view of all users, signals, and system health.
- **Soft-Delete System**: Manage bad signals without losing audit trails.
- **Entitlements Engine**: Robust RBAC (Free/Pro/Owner) to monetize premium features.

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, Pydantic.
- **Frontend**: React 18, TypeScript, TailwindCSS, Recharts.
- **Database**: PostgreSQL (Production) / SQLite (Dev).
- **AI/LLM**: DeepSeek-V3 via API + Local RAG Context.

## 🚀 Quickstart

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 2. Frontend Setup
```bash
cd web
npm install
npm run dev
```

### 3. Usage
- **Frontend**: http://localhost:5173
- **Swagger API**: http://localhost:8000/docs
- **Login**: `admin@tradercopilot.com` / `admin123` (Owner Access)

## 🔒 Security
- **JWT Authentication**: Secure session management.
- **Role-Based Access**: Strict `require_owner` dependencies for admin routes.
- **Audit Logging**: Immutable logs for all sensitive administrative actions.

---
*Built for the Future of Trading.*
