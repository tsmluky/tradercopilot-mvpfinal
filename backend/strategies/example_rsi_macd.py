# backend/strategies/example_rsi_macd.py
"""
Ejemplo de estrategia custom usando la clase base Strategy.

Esta estrategia combina RSI y MACD para detectar divergencias
y generar señales contrarian.

Este es un ejemplo didáctico de cómo integrar estrategias de trading_lab
en el Signal Hub de TraderCopilot.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from .base import Strategy, StrategyMetadata
from core.schemas import Signal


class RSIMACDDivergenceStrategy(Strategy):
    """
    Estrategia que detecta divergencias entre RSI y MACD.
    
    Señales:
    - LONG: RSI hace mínimo más alto + MACD hace mínimo más bajo (divergencia alcista)
    - SHORT: RSI hace máximo más bajo + MACD hace máximo más alto (divergencia bajista)
    
    Perfil de riesgo: MEDIUM
    Timeframe recomendado: 1h, 4h
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Args:
            config: Configuración custom, ej:
                {
                    "rsi_period": 14,
                    "rsi_oversold": 30,
                    "rsi_overbought": 70,
                    "min_confidence": 0.65
                }
        """
        self.config = config or {}
        self.rsi_period = self.config.get("rsi_period", 14)
        self.rsi_oversold = self.config.get("rsi_oversold", 30)
        self.rsi_overbought = self.config.get("rsi_overbought", 70)
        self.min_confidence = self.config.get("min_confidence", 0.65)
    
    def metadata(self) -> StrategyMetadata:
        """Metadatos de la estrategia."""
        return StrategyMetadata(
            id="rsi_macd_divergence_v1",
            name="RSI + MACD Divergence Detector",
            description=(
                "Detecta divergencias entre RSI y MACD para señales contrarian. "
                "Estrategia de reversión a la media con confirmación técnica."
            ),
            version="1.0.0",
            default_timeframe="1h",
            universe=["ETH", "BTC", "SOL", "BNB"],  # Tokens soportados
            risk_profile="medium",
            mode="CUSTOM",
            source_type="ENGINE",
            enabled=True,
            config={
                "rsi_period": self.rsi_period,
                "rsi_oversold": self.rsi_oversold,
                "rsi_overbought": self.rsi_overbought,
                "min_confidence": self.min_confidence,
            }
        )
    
    def generate_signals(
        self,
        tokens: List[str],
        timeframe: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Signal]:
        """
        Genera señales para los tokens especificados.
        
        Args:
            tokens: Lista de tokens a analizar
            timeframe: Timeframe del análisis
            context: Contexto adicional con market data
        
        Returns:
            Lista de señales generadas (puede ser vacía si no hay setups)
        """
        # Validar tokens soportados
        valid_tokens = self.validate_tokens(tokens)
        if not valid_tokens:
            return []
        
        signals = []
        
        for token in valid_tokens:
            # En producción, aquí iría la lógica real:
            # 1. Obtener datos OHLCV (desde context o API)
            # 2. Calcular RSI y MACD
            # 3. Detectar divergencias
            # 4. Generar señal si hay setup válido
            
            # Para este ejemplo, simulamos la detección:
            setup = self._detect_setup(token, timeframe, context)
            
            if setup:
                signal = self._create_signal(token, timeframe, setup)
                if signal.confidence and signal.confidence >= self.min_confidence:
                    signals.append(signal)
        
        return signals
    
    def _detect_setup(
        self,
        token: str,
        timeframe: str,
        context: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Detecta si hay un setup válido para el token.
        
        En producción, aquí va la lógica de indicadores técnicos.
        Para el ejemplo, devolvemos un setup simulado.
        
        Returns:
            Dict con info del setup o None si no hay
        """
        # SIMULACIÓN: En producción reemplazar con cálculos reales
        
        # Ejemplo de cálculo real (comentado):
        # from indicators.market import get_market_data
        # df, market = get_market_data(token, timeframe)
        # rsi = market.get("rsi")
        # macd = market.get("macd")
        # 
        # # Lógica de divergencia
        # if rsi < self.rsi_oversold and macd < -5:
        #     return {
        #         "direction": "long",
        #         "rsi": rsi,
        #         "macd": macd,
        #         "confidence": 0.75,
        #         "rationale": f"Bullish divergence: RSI {rsi:.1f}, MACD crossing up"
        #     }
        
        # Para demo, retornamos None (sin setup)
        return None
    
    def _create_signal(
        self,
        token: str,
        timeframe: str,
        setup: Dict[str, Any]
    ) -> Signal:
        """
        Crea una instancia Signal a partir de un setup detectado.
        
        Args:
            token: Token del setup
            timeframe: Timeframe
            setup: Info del setup detectado
        
        Returns:
            Instancia de Signal
        """
        direction = setup.get("direction", "neutral")
        entry = setup.get("entry", 0.0)
        
        # Calcular TP/SL según dirección
        if direction == "long":
            tp = entry * 1.05  # +5% objetivo
            sl = entry * 0.97  # -3% riesgo (R:R = 1.67)
        elif direction == "short":
            tp = entry * 0.95
            sl = entry * 1.03
        else:
            tp = entry
            sl = entry
        
        return Signal(
            timestamp=datetime.utcnow(),
            strategy_id=self.metadata().id,
            mode="CUSTOM",
            token=token.upper(),
            timeframe=timeframe,
            direction=direction,
            entry=round(entry, 2),
            tp=round(tp, 2),
            sl=round(sl, 2),
            confidence=setup.get("confidence", 0.5),
            rationale=setup.get("rationale", "RSI MACD divergence detected"),
            source="LAB",
            extra={
                "rsi": setup.get("rsi"),
                "macd": setup.get("macd"),
                "strategy_version": self.metadata().version,
            }
        )


# === Ejemplo de uso ===

if __name__ == "__main__":
    # Crear instancia de la estrategia
    strategy = RSIMACDDivergenceStrategy(config={
        "rsi_oversold": 25,
        "rsi_overbought": 75,
        "min_confidence": 0.70
    })
    
    # Ver metadatos
    meta = strategy.metadata()
    print(f"Estrategia: {meta.name}")
    print(f"ID: {meta.id}")
    print(f"Versión: {meta.version}")
    print(f"Tokens soportados: {meta.universe}")
    print(f"Risk Profile: {meta.risk_profile}")
    
    # Generar señales
    tokens = ["ETH", "BTC", "SOL"]
    timeframe = "1h"
    
    signals = strategy.generate_signals(tokens, timeframe)
    
    print(f"\nSeñales generadas: {len(signals)}")
    for signal in signals:
        print(f"  - {signal.token} {signal.direction} @ {signal.entry}")
        print(f"    TP: {signal.tp} | SL: {signal.sl}")
        print(f"    Confidence: {signal.confidence}")
        print(f"    Rationale: {signal.rationale}")
