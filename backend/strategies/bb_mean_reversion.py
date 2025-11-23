# backend/strategies/bb_mean_reversion.py
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd
import numpy as np

from .base import Strategy, StrategyMetadata
from core.schemas import Signal
from market_data_api import get_ohlcv_data

class BBMeanReversionStrategy(Strategy):
    """
    Estrategia de Reversión a la Media con Bandas de Bollinger.
    
    Opera cuando el precio toca las bandas exteriores en un mercado lateral (rango).
    Define rango usando la distancia entre EMA50 y EMA200.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.bb_period = self.config.get("bb_period", 20)
        self.bb_std = self.config.get("bb_std", 2.0)
        self.regime_thr = self.config.get("regime_thr", 0.01)
        self.tp_atr_mult = self.config.get("tp_atr_mult", 1.2)
        self.sl_atr_mult = self.config.get("sl_atr_mult", 0.8)
        
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            id="bb_mean_reversion_v1",
            name=f"BB Mean Reversion {self.bb_period}",
            description="Reversión a la media en mercados laterales usando Bollinger Bands.",
            version="1.0.0",
            default_timeframe="15m",
            universe=["*"],
            risk_profile="medium",
            mode="CUSTOM",
            source_type="ENGINE",
            enabled=True,
            config={
                "bb_period": self.bb_period,
                "bb_std": self.bb_std,
                "regime_thr": self.regime_thr,
                "tp_atr_mult": self.tp_atr_mult,
                "sl_atr_mult": self.sl_atr_mult
            }
        )

    def analyze(self, df: pd.DataFrame, token: str, timeframe: str) -> List[Signal]:
        if df.empty or len(df) < 200:
            return []

        d = df.copy()
        
        # Bollinger Bands
        d["ma"] = d["close"].rolling(self.bb_period).mean()
        d["std"] = d["close"].rolling(self.bb_period).std(ddof=0)
        d["upper"] = d["ma"] + self.bb_std * d["std"]
        d["lower"] = d["ma"] - self.bb_std * d["std"]
        d["pct_b"] = (d["close"] - d["lower"]) / (d["upper"] - d["lower"])
        
        # Regime Filter (Range vs Trend)
        d["ema50"] = d["close"].ewm(span=50, adjust=False).mean()
        d["ema200"] = d["close"].ewm(span=200, adjust=False).mean()
        d["regime_val"] = (d["ema50"] - d["ema200"]).abs() / d["close"]
        d["is_ranging"] = d["regime_val"] < self.regime_thr
        
        # ATR
        d["tr"] = np.maximum(
            d["high"] - d["low"],
            np.maximum(
                abs(d["high"] - d["close"].shift(1)),
                abs(d["low"] - d["close"].shift(1))
            )
        )
        d["atr"] = d["tr"].rolling(window=14).mean()
        
        signals = []
        
        # Filtrar donde is_ranging es True
        ranging_d = d[d["is_ranging"]]
        
        # Buscar toques de bandas
        # Long: pct_b < 0.05
        long_signals = ranging_d[ranging_d["pct_b"] < 0.05]
        
        # Short: pct_b > 0.95
        short_signals = ranging_d[ranging_d["pct_b"] > 0.95]
        
        # Procesar Longs
        for ts, row in long_signals.iterrows():
            close = float(row["close"])
            atr = float(row["atr"]) if not pd.isna(row["atr"]) else close * 0.01
            
            direction = "long"
            tp = close + self.tp_atr_mult * atr
            sl = close - self.sl_atr_mult * atr
            rationale = "Oversold in Range (Lower BB touch)"
            
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
                confidence=0.7,
                rationale=rationale,
                source="ENGINE",
                extra={"pct_b": round(row["pct_b"], 2), "regime": "RANGING"}
            )
            signals.append(signal)
            
        # Procesar Shorts
        for ts, row in short_signals.iterrows():
            close = float(row["close"])
            atr = float(row["atr"]) if not pd.isna(row["atr"]) else close * 0.01
            
            direction = "short"
            tp = close - self.tp_atr_mult * atr
            sl = close + self.sl_atr_mult * atr
            rationale = "Overbought in Range (Upper BB touch)"
            
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
                confidence=0.7,
                rationale=rationale,
                source="ENGINE",
                extra={"pct_b": round(row["pct_b"], 2), "regime": "RANGING"}
            )
            signals.append(signal)
            
        # Ordenar por timestamp
        signals.sort(key=lambda x: x.timestamp)
            
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
                    ohlcv = get_ohlcv_data(token, timeframe, limit=300)
                    if not ohlcv: continue
                    df = pd.DataFrame(ohlcv)
                
                if "timestamp" in df.columns:
                    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                    df.set_index("timestamp", inplace=True)
                    
                all_signals.extend(self.analyze(df, token, timeframe))
            except Exception as e:
                print(f"Error in BBMR for {token}: {e}")
                
        return all_signals
