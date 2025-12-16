# backend/strategies/vwap_intraday.py
"""
VWAP Intraday Strategy - Trading alrededor del precio institucional

VWAP (Volume Weighted Average Price) es el precio promedio ponderado por volumen.
Es muy respetado por traders institucionales como el "precio justo" del día.

LONG: Precio rebota en VWAP desde abajo + volumen aumentando
SHORT: Precio es rechazado en VWAP desde arriba + volumen aumentando
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd
import numpy as np

from .base import Strategy, StrategyMetadata
from core.schemas import Signal
from core.market_data_api import get_ohlcv_data


class VWAPIntradayStrategy(Strategy):
    """
    Estrategia VWAP para trading intraday.
    
    Opera rebotes y rechazos del VWAP, que actúa como soporte/resistencia dinámico.
    El volumen es clave: solo operamos cuando hay confirmación de volumen.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.vwap_bands_std = self.config.get("vwap_bands_std", 1.0)  # Desviación estándar para bandas
        self.volume_ma_period = self.config.get("volume_ma_period", 20)
        self.volume_threshold = self.config.get("volume_threshold", 1.2)  # Volumen debe ser 1.2x promedio
        self.tp_pct = self.config.get("tp_pct", 0.015)  # 1.5% TP (intraday más conservador)
        self.sl_pct = self.config.get("sl_pct", 0.008)  # 0.8% SL
        
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            id="vwap_intraday_v1",
            name="VWAP Intraday",
            description="Opera rebotes y rechazos del VWAP con confirmación de volumen.",
            version="1.0.0",
            default_timeframe="15m",
            universe=["*"],
            risk_profile="medium",
            mode="CUSTOM",
            source_type="ENGINE",
            enabled=True,
            config={
                "vwap_bands_std": self.vwap_bands_std,
                "volume_ma_period": self.volume_ma_period,
                "volume_threshold": self.volume_threshold,
                "tp_pct": self.tp_pct,
                "sl_pct": self.sl_pct
            }
        )
    
    def _calculate_vwap(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula VWAP y sus bandas de desviación estándar.
        
        VWAP = Σ(Price × Volume) / Σ(Volume)
        """
        d = df.copy()
        
        # Typical Price (HLC/3)
        d["typical_price"] = (d["high"] + d["low"] + d["close"]) / 3
        
        # VWAP cumulativo (resetea cada día, pero aquí simplificamos con ventana móvil de 100)
        # En producción, deberías resetear en cada sesión de trading
        window = min(100, len(d))
        
        d["pv"] = d["typical_price"] * d["volume"]
        d["cumulative_pv"] = d["pv"].rolling(window=window).sum()
        d["cumulative_volume"] = d["volume"].rolling(window=window).sum()
        
        d["vwap"] = d["cumulative_pv"] / d["cumulative_volume"]
        
        # Calcular desviación estándar del precio respecto a VWAP
        d["price_deviation"] = (d["typical_price"] - d["vwap"]) ** 2
        d["cum_price_dev"] = d["price_deviation"].rolling(window=window).sum()
        d["vwap_std"] = np.sqrt(d["cum_price_dev"] / d["cumulative_volume"])
        
        # Bandas VWAP
        d["vwap_upper"] = d["vwap"] + (self.vwap_bands_std * d["vwap_std"])
        d["vwap_lower"] = d["vwap"] - (self.vwap_bands_std * d["vwap_std"])
        
        # Volumen promedio
        d["volume_ma"] = d["volume"].rolling(window=self.volume_ma_period).mean()
        d["volume_ratio"] = d["volume"] / d["volume_ma"]
        
        return d
    
    def analyze(self, df: pd.DataFrame, token: str, timeframe: str) -> List[Signal]:
        if df.empty or len(df) < 100:
            return []
        
        d = self._calculate_vwap(df)
        d = d.dropna()
        
        if len(d) < 20:
            return []
        
        signals = []
        
        # Solo las últimas 3 velas para detectar setup reciente
        recent = d.tail(3)
        
        if len(recent) < 3:
            return []
        
        last = recent.iloc[-1]
        prev = recent.iloc[-2]
        prev2 = recent.iloc[-3]
        
        close = float(last["close"])
        vwap = float(last["vwap"])
        vwap_upper = float(last["vwap_upper"])
        vwap_lower = float(last["vwap_lower"])
        volume_ratio = float(last["volume_ratio"])
        
        # Setup LONG: Precio rebota en VWAP/banda inferior con volumen
        # Condiciones:
        # 1. Vela anterior tocó o estuvo cerca de VWAP desde abajo
        # 2. Vela actual cierra por encima de VWAP
        # 3. Volumen por encima del promedio
        touched_vwap_from_below = (prev["low"] <= vwap * 1.005 and prev["close"] < vwap)
        closed_above_vwap = close > vwap
        high_volume = volume_ratio >= self.volume_threshold
        
        if touched_vwap_from_below and closed_above_vwap and high_volume:
            entry = close
            tp = close * (1 + self.tp_pct)
            sl = vwap_lower  # SL en banda inferior
            
            confidence = min(0.8, 0.65 + (volume_ratio - self.volume_threshold) * 0.1)
            
            rationale = f"VWAP Bounce (Volume {volume_ratio:.1f}x avg, Price reclaimed VWAP)"
            
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
                    "vwap": round(vwap, 2),
                    "volume_ratio": round(volume_ratio, 2),
                    "setup": "vwap_bounce"
                }
            )
            signals.append(signal)
        
        # Setup SHORT: Precio es rechazado en VWAP/banda superior con volumen
        touched_vwap_from_above = (prev["high"] >= vwap * 0.995 and prev["close"] > vwap)
        closed_below_vwap = close < vwap
        
        if touched_vwap_from_above and closed_below_vwap and high_volume:
            entry = close
            tp = close * (1 - self.tp_pct)
            sl = vwap_upper  # SL en banda superior
            
            confidence = min(0.8, 0.65 + (volume_ratio - self.volume_threshold) * 0.1)
            
            rationale = f"VWAP Rejection (Volume {volume_ratio:.1f}x avg, Price rejected at VWAP)"
            
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
                    "vwap": round(vwap, 2),
                    "volume_ratio": round(volume_ratio, 2),
                    "setup": "vwap_rejection"
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
                print(f"Error in VWAP Intraday for {token}: {e}")
                
        return all_signals
