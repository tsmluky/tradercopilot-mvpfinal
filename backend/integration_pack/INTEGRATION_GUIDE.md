# Integration Guide: TraderCopilot Backend

This guide explains how to integrate the validated strategies from `trading_lab` into the `TraderCopilot` backend.

## 1. Copy Core Modules
Copy the `trading_rules` folder from `trading_lab` to your backend's core directory.
- Source: `trading_lab/trading_rules`
- Destination: `TraderCopilot/app/core/trading_rules`

## 2. Copy Strategy Implementations
Copy the strategy files from `integration_pack` to your backend's strategies directory.
- Source: `trading_lab/integration_pack/strategies/implementations/*.py`
- Destination: `TraderCopilot/app/strategies/implementations/`

## 3. Register Strategies
Update `TraderCopilot/app/strategies/registry.py` (or equivalent) to import and register the new classes:
```python
from app.strategies.implementations.trend_ma_strategy import TrendMaCrossStrategy
from app.strategies.implementations.donchian_strategy import DonchianBreakoutStrategy

# In your registry initialization:
registry.register(TrendMaCrossStrategy)
registry.register(DonchianBreakoutStrategy)
```

## 4. Implement Market Data Service
You need a real `MarketDataService` that fetches live data from an exchange (e.g., Binance, MEXC).
It must implement the `get_ohlcv(token, timeframe, limit)` method expected by the strategies.

## 5. Update Scheduler
Ensure your `scheduler.py` iterates through registered strategies and executes them using the `MarketDataService`.

## 6. Run
Restart your backend. The strategies will now be available for configuration and execution.
