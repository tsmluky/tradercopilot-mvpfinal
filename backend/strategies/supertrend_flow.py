# backend/strategies/supertrend_flow.py
"""
SuperTrend Flow Strategy - Seguimiento de tendencia puro

SuperTrend es un indicador basado en ATR que sigue la tendencia del mercado.
Es muy simple pero efectivo, especialmente en mercados con tendencias claras.

LONG: Cuando precio cruza por encima de SuperTrend
SHORT: Cuando precio cruza por debajo de SuperTrend
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd
import numpy as np

from .base import Strategy, StrategyMetadata
from core.schemas import Signal
from market_data_api import get_ohlcv_data


class SuperTrendFlowStrategy(Strategy):
    """
    Estrategia de seguimiento de tendencia usando el indicador SuperTrend.
    
    SuperTrend combina ATR (volatilidad) con price action para identificar
    la dirección de la tendencia. Es excelente para capturar grandes movimientos.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.atr_period = self.config.get("atr_period", 10)
        self.atr_multiplier = self.config.get("atr_multiplier", 3.0)  # Factor de SuperTrend
        self.tp_atr_mult = self.config.get("tp_atr_mult", 3.0)  # R:R alto para tendencias
        self.sl_atr_mult = self.config.get("sl_atr_mult", 1.5)
        
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            id="supertrend_flow_v1",
            name=f"SuperTrend Flow {self.atr_period}/{self.atr_multiplier}",
            description="Seguimiento de tendencia puro con SuperTrend indicator.",
            version="1.0.0",
            default_timeframe="4h",
            universe=["*"],
            risk_profile="medium",
            mode="CUSTOM",
            source_type="ENGINE",
            enabled=True,
            config={
                "atr_period": self.atr_period,
                "atr_multiplier": self.atr_multiplier,
                "tp_atr_mult": self.tp_atr_mult,
                "sl_atr_mult": self.sl_atr_mult
            }
        )
    
    def _calculate_supertrend(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula el indicador SuperTrend.
        
        SuperTrend = (High + Low) / 2 ± (Multiplier × ATR)
        """
        d = df.copy()
        
        # ATR
        d["tr"] = np.maximum(
            d["high"] - d["low"],
            np.maximum(
                abs(d["high"] - d["close"].shift(1)),
                abs(d["low"] - d["close"].shift(1))
            )
        )
        d["atr"] = d["tr"].rolling(window=self.atr_period).mean()
        
        # Banda básica
        hl2 = (d["high"] + d["low"]) / 2
        d["upper_band"] = hl2 + (self.atr_multiplier * d["atr"])
        d["lower_band"] = hl2 - (self.atr_multiplier * d["atr"])
        
        # SuperTrend final (con lógica de cambio de banda)
        d["supertrend"] = 0.0
        d["trend"] = 1  # 1 = uptrend, -1 = downtrend
        
        for i in range(1, len(d)):
            # Ajustar bandas según precio anterior
            if d["close"].iloc[i-1] <= d["upper_band"].iloc[i-1]:
                d.loc[d.index[i], "upper_band"] = min(d["upper_band"].iloc[i], d["upper_band"].iloc[i-1])
            
            if d["close"].iloc[i-1] >= d["lower_band"].iloc[i-1]:
                d.loc[d.index[i], "lower_band"] = max(d["lower_band"].iloc[i], d["lower_band"].iloc[i-1])
            
            # Determinar SuperTrend
            if d["close"].iloc[i] > d["upper_band"].iloc[i-1]:
                d.loc[d.index[i], "trend"] = 1
                d.loc[d.index[i], "supertrend"] = d["lower_band"].iloc[i]
            elif d["close"].iloc[i] < d["lower_band"].iloc[i-1]:
                d.loc[d.index[i], "trend"] = -1
                d.loc[d.index[i], "supertrend"] = d["upper_band"].iloc[i]
            else:
                d.loc[d.index[i], "trend"] = d["trend"].iloc[i-1]
                if d["trend"].iloc[i] == 1:
                    d.loc[d.index[i], "supertrend"] = d["lower_band"].iloc[i]
                else:
                    d.loc[d.index[i], "supertrend"] = d["upper_band"].iloc[i]
        
        return d
    
    def analyze(self, df: pd.DataFrame, token: str, timeframe: str) -> List[Signal]:
        if df.empty or len(df) < 50:
            return []
        
        d = self._calculate_supertrend(df)
        d = d.dropna()
        
        if len(d) < 10:
            return []
        
        signals = []
        
        # Detectar cambio de tendencia (cruce de SuperTrend)
        # Solo generar señal si hay cambio en las últimas 2 velas
        if len(d) >= 2:
            prev_trend = d["trend"].iloc[-2]
            current_trend = d["trend"].iloc[-1]
            
            # Cambio a UPTREND (de -1 a 1)
            if prev_trend == -1 and current_trend == 1:
                close = float(d["close"].iloc[-1])
                supertrend = float(d["supertrend"].iloc[-1])
                atr = float(d["atr"].iloc[-1]) if not pd.isna(d["atr"].iloc[-1]) else close * 0.02
                
                entry = close
                tp = close + self.tp_atr_mult * atr
                sl = supertrend  # SL en el SuperTrend (muy tight)
                
                # Calcular distancia al SL para confidence
                sl_distance_pct = abs((sl - entry) / entry) * 100
                confidence = min(0.8, max(0.6, 0.8 - (sl_distance_pct / 10)))
                
                rationale = f"SuperTrend Uptrend (Price crossed above SuperTrend @ {supertrend:.2f})"
                
                signal = Signal(
                    timestamp=d.index[-1] if isinstance(d.index[-1], datetime) else datetime.utcnow(),
                    strategy_id=self.metadata().id,
                    mode="CUSTOM",
                    token=token.upper(),
                    timeframe=timeframe,
                    direction="long",
                    entry=round(entry, 2),
                    tp=round(tp, 2),
                    sl=round(sl, 2),
                    confidence=round(confidence, 2),
                    rationale=rationale,
                    source="ENGINE",
                    extra={
                        "supertrend": round(supertrend, 2),
                        "atr": round(atr, 2),
                        "trend_change": "bullish"
                    }
                )
                signals.append(signal)
            
            # Cambio a DOWNTREND (de 1 a -1)
            elif prev_trend == 1 and current_trend == -1:
                close = float(d["close"].iloc[-1])
                supertrend = float(d["supertrend"].iloc[-1])
                atr = float(d["atr"].iloc[-1]) if not pd.isna(d["atr"].iloc[-1]) else close * 0.02
                
                entry = close
                tp = close - self.tp_atr_mult * atr
                sl = supertrend  # SL en el SuperTrend
                
                sl_distance_pct = abs((sl - entry) / entry) * 100
                confidence = min(0.8, max(0.6, 0.8 - (sl_distance_pct / 10)))
                
                rationale = f"SuperTrend Downtrend (Price crossed below SuperTrend @ {supertrend:.2f})"
                
                signal = Signal(
                    timestamp=d.index[-1] if isinstance(d.index[-1], datetime) else datetime.utcnow(),
                    strategy_id=self.metadata().id,
                    mode="CUSTOM",
                    token=token.upper(),
                    timeframe=timeframe,
                    direction="short",
                    entry=round(entry, 2),
                    tp=round(tp, 2),
                    sl=round(sl, 2),
                    confidence=round(confidence, 2),
                    rationale=rationale,
                    source="ENGINE",
                    extra={
                        "supertrend": round(supertrend, 2),
                        "atr": round(atr, 2),
                        "trend_change": "bearish"
                    }
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
                    ohlcv = get_ohlcv_data(token, timeframe, limit=1000)
                    if not ohlcv: continue
                    df = pd.DataFrame(ohlcv)
                
                if "timestamp" in df.columns:
                    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                    df.set_index("timestamp", inplace=True)
                    
                all_signals.extend(self.analyze(df, token, timeframe))
            except Exception as e:
                print(f"Error in SuperTrend Flow for {token}: {e}")
                
        return all_signals
