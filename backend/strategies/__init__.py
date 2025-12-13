# backend/strategies/__init__.py
"""
Strategy Base Module for TraderCopilot Signal Hub.
"""

from .base import Strategy, StrategyMetadata

# Import Strategy Implementations
from .donchian import DonchianStrategy
from .DonchianBreakoutV2 import DonchianBreakoutV2
from .ma_cross import MACrossStrategy
from .supertrend_flow import SuperTrendFlowStrategy
from .bb_mean_reversion import BBMeanReversionStrategy
from .rsi_divergence import RSIDivergenceStrategy
from .vwap_intraday import VWAPIntradayStrategy
from .TrendFollowingNative import TrendFollowingNative


__all__ = [
    "Strategy",
    "StrategyMetadata",
    "DonchianStrategy",
    "DonchianBreakoutV2",
    "MACrossStrategy",
    "SuperTrendFlowStrategy",
    "BBMeanReversionStrategy",
    "RSIDivergenceStrategy",
    "VWAPIntradayStrategy",
    "TrendFollowingNative",

]
