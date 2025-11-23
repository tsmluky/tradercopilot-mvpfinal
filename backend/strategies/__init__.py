# backend/strategies/__init__.py
"""
Strategy Base Module for TraderCopilot Signal Hub.

Este módulo define la interfaz base para TODAS las estrategias,
permitiendo integrar fácilmente:
- Estrategias cuantitativas de trading_lab
- Reglas deterministas (LITE)
- Estrategias LLM-based (PRO/ADVISOR)
- Estrategias custom de usuarios
"""

from .base import Strategy, StrategyMetadata

__all__ = [
    "Strategy",
    "StrategyMetadata",
]
