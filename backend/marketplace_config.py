
from typing import List, Dict, Any

# Define the "Personas" for the Strategy Marketplace
# This maps the "Marketing View" to the "Technical Implementation"

MARKETPLACE_PERSONAS = [
    {
        "id": "trend_king_sol",
        "name": "The Trend King",
        "symbol": "SOL",
        "timeframe": "1d",
        "strategy_id": "donchian_v2", # Maps to technical ID
        "description": "Aggressive trend hunter. Catches the massive waves in Solana. High volatility, massive reward.",
        "risk_level": "High",
        "expected_roi": "290%", # Based on Benchmark
        "win_rate": "46%",
        "frequency": "Low (1 trade / 3 days)",
        "color": "amber", # Frontend styling
        "is_active": True
    },
    {
        "id": "dot_scalper_ai",
        "name": "The Scalper AI",
        "symbol": "DOT",
        "timeframe": "15m",
        "strategy_id": "rsi_divergence_v1",
        "description": "Hyper-active neural scalper. Scrapes small profits from market noise. Keeps the system alive.",
        "risk_level": "Medium",
        "expected_roi": "77%",
        "win_rate": "35%",
        "frequency": "High (16 trades/day)",
        "color": "cyan",
        "is_active": True
    },
    {
        "id": "titan_btc",
        "name": "Titan Fortress",
        "symbol": "BTC",
        "timeframe": "1d",
        "strategy_id": "donchian_v2",
        "description": "The immovable object. Slow, steady accumulation of Bitcoin. Your safety net.",
        "risk_level": "Low",
        "expected_roi": "20%",
        "win_rate": "52%",
        "frequency": "Very Low",
        "color": "slate",
        "is_active": True
    },
    {
        "id": "flow_avax",
        "name": "Flow Master",
        "symbol": "AVAX",
        "timeframe": "1d",
        "strategy_id": "trend_following_native_v1",
        "description": "Smooth operator using Golden Cross logic. Validated technical momentum.",
        "risk_level": "Medium",
        "expected_roi": "28%",
        "win_rate": "55%",
        "frequency": "Medium",
        "color": "indigo",
        "is_active": True
    }
]

def get_active_strategies():
    """Returns list of strategies to run in the scheduler"""
    return [p for p in MARKETPLACE_PERSONAS if p["is_active"]]
