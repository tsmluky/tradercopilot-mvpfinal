# 🚀 Quick Start Guide - TraderCopilot MVP

## For Testers & Early Users

Welcome! This guide will get you up and running in **5 minutes**.

---

## ⚡ Super Quick Start

### Step 1: Install Dependencies

```bash
# Backend
cd backend
pip install fastapi uvicorn sqlalchemy aiosqlite requests pandas

# Frontend
cd ../web
npm install
```

### Step 2: Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
pwsh tools/start_dev.ps1 -Port 8010
```

**Terminal 2 - Frontend:**
```bash
cd web
npm run dev
```

### Step 3: Open Your Browser

Go to: **http://localhost:3000**

---

## 🎯 What to Test

### 1. Generate a Quick Signal (LITE Mode)

1. Click **Terminal** in sidebar
2. Select **BTC** and **30m** timeframe
3. Click **RUN** button
4. You'll see:
   - Entry price
   - Take Profit (TP)
   - Stop Loss (SL)
   - Confidence score
   - Risk/Reward ratio

### 2. Get Deep Analysis (PRO Mode)

1. Switch to **PRO** mode (toggle at top)
2. Select **ETH** and **1h** timeframe
3. Click **RUN**
4. Review the comprehensive analysis:
   - Market context
   - Technical indicators
   - Sentiment analysis
   - On-chain metrics
   - Trading plan with multiple strategies

### 3. Use the Trading Advisor

1. Switch to **ADVISOR** mode
2. Fill in your trade details:
   - Token: BTC
   - Direction: Long
   - Entry: 65000
   - Size: 1000 USDT
   - TP: 67000
   - SL: 64000
3. Click **START SESSION**
4. Ask questions like:
   - "Is this risk acceptable?"
   - "Should I tighten my stop loss?"
   - "What if price consolidates?"

### 4. Check Your Performance

1. Click **Logs** in sidebar
2. View all your past signals
3. Filter by token or mode
4. See timestamps and parameters

### 5. View Dashboard Stats

1. Click **Dashboard**
2. See:
   - Win rate (24h)
   - Active signals
   - Total evaluations
   - Recent activity

---

## 📊 Understanding the Charts

- **Blue area**: Price movement
- **Blue dashed line**: Entry point
- **Green line**: Take Profit target
- **Red line**: Stop Loss level

The chart shows **real-time data from Binance**.

---

## 💡 Pro Tips

1. **Start with LITE mode** to get familiar
2. **Use PRO mode** when you need detailed analysis
3. **ADVISOR mode** is great for second opinions on trades
4. **Check the Logs** to track your signal history
5. **Different timeframes** give different perspectives:
   - 5m/15m: Scalping
   - 30m/1h: Day trading
   - 4h: Swing trading

---

## 🐛 Common Issues

### "Backend not responding"
- Make sure backend is running on port 8010
- Check Terminal 1 for errors

### "Chart not loading"
- Backend might be starting up (wait 10 seconds)
- Check if Binance API is accessible in your region

### "No data in logs"
- Generate some signals first (use LITE mode)
- Logs will appear after you click RUN

---

## 📝 Feedback

Please test and provide feedback on:

✅ **Usability**: Is it easy to use?
✅ **Speed**: Are responses fast enough?
✅ **Accuracy**: Do signals make sense?
✅ **Design**: Is the UI clear and professional?
✅ **Features**: What's missing? What would you add?

---

## 🎯 Test Scenarios

Try these scenarios:

1. **Scenario 1: Quick Trade Idea**
   - Use LITE mode
   - Generate signals for BTC, ETH, SOL
   - Compare confidence scores

2. **Scenario 2: Deep Research**
   - Use PRO mode
   - Analyze one token in detail
   - Read all sections of the analysis

3. **Scenario 3: Position Review**
   - Use ADVISOR mode
   - Input a hypothetical trade
   - Ask multiple questions

4. **Scenario 4: Performance Tracking**
   - Generate 5-10 signals
   - Check Logs page
   - Review Dashboard stats

---

## ⚠️ Important Notes

- This is an **MVP (Minimum Viable Product)**
- Data is **for testing only**, not financial advice
- No real money should be used based on these signals
- Authentication is mock (single user mode)

---

## 📞 Report Issues

Found a bug or have suggestions?

1. Note the steps to reproduce
2. Take a screenshot if relevant
3. Share with the development team

---

**Happy Testing! 🚀**
