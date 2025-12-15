<div align="center">
  <h1>🚀 TraderCopilot</h1>
  <h3>Institutional-Grade AI Trading Assistant for Retail</h3>
  
  <p>
    <b>Real-time Logic</b> • <b>RAG Context</b> • <b>Agentic Analysis</b>
  </p>

  [![Status](https://img.shields.io/badge/Status-Private_Beta-orange?style=for-the-badge)]()
  [![Stack](https://img.shields.io/badge/Stack-FastAPI_|_React_|_PostgreSQL-blue?style=for-the-badge)]()
  [![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)]()
</div>

---

## 💎 The Vision

**TraderCopilot** is not just a scanner; it is an **active AI agent** designed to democratize institutional-grade market analysis. 

While traditional retail tools offer static charts, TraderCopilot acts as a 24/7 analyst that:
1.  **Monitors** 150+ assets every minute.
2.  **Filters** noise using proprietary algorithms (Lite/Pro logic).
3.  **Contextualizes** price action using RAG (News, On-Chain Data, Sentiment).
4.  **Generates** actionable, risk-managed trade plans.

> *"We don't just show you the chart; we interpret the story behind it."*

---

## 🔥 Key Capabilities

### 📡 Active Market Sentinel
*   **Multi-Timeframe Scanning**: Simultaneous monitoring of Scalp (1m/5m), Swing (1h/4h), and Macro (1d) trends.
*   **Algorithmic Gating**: Signals are classified by tier (Rookie/Trader/Whale) to monetize premium alpha.
*   **Anomaly Detection**: Automatically flags volume spikes and RSI divergences instantly.

### 🧠 The "Advisor" (Agentic AI)
*   **Conversational Alpha**: Chat directly with the system to ask *"Is ETH risky right now?"* or *"Analyze this breakdown."*
*   **RAG-Powered**: Answers are grounded in real data (Price, Indicators, News), not hallucinations.
*   **Risk Guardrails**: The AI proactively suggests Stop Losses and leverage limits based on volatility.

### 🛡️ Automated Evaluation Loop
*   **Self-Correcting**: The system tracks every signal it generates.
*   **PnL Tracking**: Automatically marks signals as `WIN`, `LOSS`, or `BE` (Breakeven) without human intervention.
*   **Leaderboard**: Gamified performance tracking for users (and the AI itself).

---

## 🏗️ System Architecture

TraderCopilot operates on a **Service-Oriented Architecture** designed for high availability and low latency.

```mermaid
graph TD
    User([User]) <--> Client[React Frontend (Vite)]
    Client <--> API[FastAPI Gateway]
    
    subgraph "Core Engine (Private)"
        API <--> Controller[Logic Controller]
        Controller <--> DB[(PostgreSQL)]
        
        Worker[Background Scheduler] --> Binance[(Binance Data)]
        Worker --> Analyzer[Strategy Engine]
        Analyzer --> DB
    end

    Analyzer -.-> DeepSeek[DeepSeek R1 Inference]
```

---

## 🔒 Security & Access

This software is **Proprietary**.
*   **Identity Management**: Secure JWT-based authentication.
*   **Tiered Access**: Role-Based Access Control (RBAC) allows strict gating of features (Scanner, Chat, Pro Data).

---

## 📜 License

**Copyright © 2025 TraderCopilot Team.** All Rights Reserved.
This project is proprietary software. Unauthorized copying, modification, distribution, or use of this file, via any medium, is strictly prohibited.
