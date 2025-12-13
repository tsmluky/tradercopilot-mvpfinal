
from .base import Strategy, StrategyMetadata
from core.schemas import Signal
from datetime import datetime
from typing import List, Optional, Dict, Any
import pandas as pd
import pandas_ta as ta

class BBMeanReversionStrategy(Strategy):
    """
    Estrategia "Mean Reversion" basada en el torneo.
    Compra en la banda inferior y vende en la superior, buscando retorno a la media.
    Filtra con RSI para evitar operar contra tendencias muy fuertes sin agotamiento.
    """
    
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            id="bb_mean_reversion",
            name="Bollinger Reversion",
            description="Mean Reversion using Bollinger Bands (20, 2.0) + RSI Filter.",
            version="1.0.0",
            universe=["BTC", "ETH", "SOL"], # Main assets
            risk_profile="medium",
            mode="CUSTOM",
            source_type="ENGINE",
            category="REVERSION", # New Category
            default_timeframe="1h"
        )

    def generate_signals(
        self,
        tokens: List[str],
        timeframe: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Signal]:
        signals = []
        
        # En producción/backtest, "data" suele venir en el contexto
        if not context or "data" not in context:
            # Si no hay datos inyectados, en un entorno real aquí se pedirían a la API
            # Para este MVP asumimos que el scheduler/engine inyecta los datos
            return []

        data_map = context["data"]

        for token in tokens:
            df = data_map.get(token)
            if df is None or df.empty:
                continue
            
            # Necesitamos al menos ~30 velas para BB y RSI
            if len(df) < 50:
                continue

            # Copia defensiva
            d = df.copy()

            # --- Indicadores Técnicos ---
            # Bollinger Bands (20, 2.0)
            bb = ta.bbands(d['close'], length=20, std=2.0)
            if bb is None: continue
            
            # RSI (14)
            rsi = ta.rsi(d['close'], length=14)
            if rsi is None: continue

            # Unir al DF
            # Nombres por defecto pandas_ta: BBL_20_2.0, BBM_20_2.0, BBU_20_2.0, RSI_14
            d = pd.concat([d, bb, rsi], axis=1)
            
            # --- Lógica de Señal (NO REPAINTING) ---
            # Usamos la ÚLTIMA VELA CERRADA.
            # En backtest, el engine nos pasa datos hasta 'i', siendo iloc[-1] la vela "actual" o recién cerrada.
            # Asumiremos que iloc[-1] es la vela sobre la que tomamos decisión (Close price defined).
            
            row = d.iloc[-1]
            
            close = row['close']
            lower = row['BBL_20_2.0']
            upper = row['BBU_20_2.0']
            mid   = row['BBM_20_2.0'] # Media Simple 20
            rsi_val = row['RSI_14']
            
            if pd.isna(lower) or pd.isna(rsi_val):
                continue
            
            # Determinar Timestamp correcto
            # Si 'timestamp_dt' existe (backend legacy), usarlo, sino convertir
            ts_val = datetime.utcnow()
            if 'timestamp' in d.columns:
                try:
                    # El timestamp de la vela suele ser el Open Time.
                    # La señal se emite al cierre, así que es válida AHORA.
                    ts_raw = d.index[-1] if isinstance(d.index[-1], pd.Timestamp) else pd.to_datetime(d['timestamp'].iloc[-1], unit='ms')
                    ts_val = ts_raw
                except:
                    pass
            
            signal = None
            
            # --- Setup LONG ---
            # --- Setup LONG ---
            # Precio < Banda Inferior & RSI < 35 (Sobrevendido)
            if close < lower and rsi_val < 35:
                dist = mid - close
                # Conservative TP: 80% of distance to mean (accounts for MA moving down)
                tp = close + (dist * 0.8) 
                sl = close - (dist * 0.6) # Stop un poco por debajo
                
                signal = Signal(
                    timestamp=ts_val,
                    token=token,
                    timeframe=timeframe,
                    direction="long",
                    entry=round(close, 2),
                    tp=round(tp, 2),
                    sl=round(sl, 2),
                    confidence=0.85, 
                    rationale=f"Reversion Long: Price < LowerBB ({lower:.2f}) & RSI {rsi_val:.1f} < 35",
                    source="bb_mean_reversion",
                    strategy_id=self.metadata().id,
                    mode="CUSTOM",
                    category="REVERSION",
                    extra={
                        "rsi": round(rsi_val, 1),
                        "bb_lower": round(lower, 2),
                        "bb_upper": round(upper, 2)
                    }
                )

            # --- Setup SHORT ---
            # Precio > Banda Superior & RSI > 65 (Sobrecomprado)
            elif close > upper and rsi_val > 65:
                dist = close - mid
                # Conservative TP: 80% of distance to mean
                tp = close - (dist * 0.8)
                sl = close + (dist * 0.6)
                
                signal = Signal(
                    timestamp=ts_val,
                    token=token,
                    timeframe=timeframe,
                    direction="short",
                    entry=round(close, 2),
                    tp=round(tp, 2),
                    sl=round(sl, 2),
                    confidence=0.85,
                    rationale=f"Reversion Short: Price > UpperBB ({upper:.2f}) & RSI {rsi_val:.1f} > 65",
                    source="bb_mean_reversion",
                    strategy_id=self.metadata().id,
                    mode="CUSTOM",
                    category="REVERSION",
                    extra={
                        "rsi": round(rsi_val, 1),
                        "bb_lower": round(lower, 2),
                        "bb_upper": round(upper, 2)
                    }
                )

            if signal:
                signals.append(signal)

        return signals
