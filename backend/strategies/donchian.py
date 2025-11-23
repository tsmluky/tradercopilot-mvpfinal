# backend/strategies/donchian.py
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd
import numpy as np

from .base import Strategy, StrategyMetadata
from core.schemas import Signal
from market_data_api import get_ohlcv_data

class DonchianStrategy(Strategy):
    """
    Estrategia de Ruptura de Canal Donchian.
    
    Genera señales cuando el precio rompe el máximo/mínimo de N periodos.
    Filtra por volatilidad (ATR) y tendencia (EMA200).
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.period = self.config.get("period", 20)
        self.atr_pct_min = self.config.get("atr_pct_min", 0.005)
        self.tp_atr_mult = self.config.get("tp_atr_mult", 1.8)
        self.sl_atr_mult = self.config.get("sl_atr_mult", 1.0)
        
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            id="donchian_breakout_v1",
            name=f"Donchian Breakout {self.period}",
            description="Estrategia de ruptura de canal con filtro de tendencia y volatilidad.",
            version="1.0.0",
            default_timeframe="4h",
            universe=["*"],
            risk_profile="high",
            mode="CUSTOM",
            source_type="ENGINE",
            enabled=True,
            config={
                "period": self.period,
                "atr_pct_min": self.atr_pct_min,
                "tp_atr_mult": self.tp_atr_mult,
                "sl_atr_mult": self.sl_atr_mult
            }
        )

    def analyze(self, df: pd.DataFrame, token: str, timeframe: str) -> List[Signal]:
        if df.empty or len(df) < 200: # Necesitamos 200 para EMA200
            return []

        d = df.copy()
        
        # Indicadores
        d["donch_high"] = d["high"].rolling(window=self.period).max().shift(1)
        d["donch_low"] = d["low"].rolling(window=self.period).min().shift(1)
        d["ema200"] = d["close"].ewm(span=200, adjust=False).mean()
        
        # ATR
        d["tr"] = np.maximum(
            d["high"] - d["low"],
            np.maximum(
                abs(d["high"] - d["close"].shift(1)),
                abs(d["low"] - d["close"].shift(1))
            )
        )
        d["atr"] = d["tr"].rolling(window=14).mean()
        
        # Identificar condiciones vectorizadas
        atr_pct = (d["atr"] / d["close"]).fillna(0)
        is_volatile = atr_pct >= self.atr_pct_min
        
        # Shift para comparar cierre con EMA previa (trend filter)
        # Usamos la EMA de la vela anterior para determinar tendencia antes de la ruptura
        trend_bullish = d["close"] > d["ema200"]
        trend_bearish = d["close"] < d["ema200"]
        
        # Breakouts
        breakout_high = (d["high"] > d["donch_high"]) & is_volatile & trend_bullish
        breakout_low = (d["low"] < d["donch_low"]) & is_volatile & trend_bearish
        
        signals = []
        
        # Indices donde ocurre breakout
        # Combinamos índices
        signal_indices = d.index[breakout_high | breakout_low]
        
        for ts in signal_indices:
            row = d.loc[ts]
            close = float(row["close"])
            atr = float(row["atr"]) if not pd.isna(row["atr"]) else close * 0.01
            
            if breakout_high[ts]:
                direction = "long"
                tp = close + self.tp_atr_mult * atr
                sl = close - self.sl_atr_mult * atr
                rationale = f"Donchian Breakout HIGH ({self.period}) + Trend Bullish"
                extra = {"donch_high": round(row["donch_high"], 2), "ema200": round(row["ema200"], 2)}
            else:
                direction = "short"
                tp = close - self.tp_atr_mult * atr
                sl = close + self.sl_atr_mult * atr
                rationale = f"Donchian Breakout LOW ({self.period}) + Trend Bearish"
                extra = {"donch_low": round(row["donch_low"], 2), "ema200": round(row["ema200"], 2)}
                
            signal_ts = ts if isinstance(ts, datetime) else datetime.utcnow()
            
            signal = Signal(
                timestamp=signal_ts,
                strategy_id=self.metadata().id,
                mode="CUSTOM",
                token=token.upper(),
                timeframe=timeframe,
                direction=direction,
                entry=round(close, 2),
                tp=round(tp, 2),
                sl=round(sl, 2),
                confidence=0.75,
                rationale=rationale,
                source="ENGINE",
                extra=extra
            )
            signals.append(signal)
            
        return signals

    def generate_signals(self, tokens: List[str], timeframe: str, context: Optional[Dict[str, Any]] = None) -> List[Signal]:
        valid_tokens = self.validate_tokens(tokens)
        all_signals = []
        
        for token in valid_tokens:
            try:
                if context and "data" in context and token in context["data"]:
                    raw_data = context["data"][token]
                    df = pd.DataFrame(raw_data) if isinstance(raw_data, list) else raw_data
                else:
                    ohlcv = get_ohlcv_data(token, timeframe, limit=300) # Necesitamos más historia para EMA200
                    if not ohlcv: continue
                    df = pd.DataFrame(ohlcv)
                
                if "timestamp" in df.columns:
                    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                    df.set_index("timestamp", inplace=True)
                    
                all_signals.extend(self.analyze(df, token, timeframe))
            except Exception as e:
                print(f"Error in Donchian for {token}: {e}")
                
        return all_signals
