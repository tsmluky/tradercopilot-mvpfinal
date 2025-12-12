from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    token = Column(String, index=True)
    timeframe = Column(String)
    direction = Column(String)
    entry = Column(Float)
    tp = Column(Float)
    sl = Column(Float)
    confidence = Column(Float)
    rationale = Column(Text)
    source = Column(String)
    mode = Column(String) # LITE, PRO, ADVISOR
    raw_response = Column(Text, nullable=True)
    strategy_id = Column(String, index=True, nullable=True)
    
    # Relationship to evaluation
    evaluation = relationship("SignalEvaluation", back_populates="signal", uselist=False)

class SignalEvaluation(Base):
    __tablename__ = "signal_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    signal_id = Column(Integer, ForeignKey("signals.id"))
    evaluated_at = Column(DateTime, default=datetime.utcnow)
    result = Column(String) # WIN, LOSS, BE
    pnl_r = Column(Float)
    exit_price = Column(Float)
    
    signal = relationship("Signal", back_populates="evaluation")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)


class StrategyConfig(Base):
    """
    Configuración de estrategias 24/7 para el scheduler.
    
    Cada registro representa una estrategia que puede ejecutarse
    automáticamente en el backend.
    """
    __tablename__ = "strategy_configs"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(String, unique=True, index=True)  # ej: "rsi_macd_v1"
    name = Column(String)  # Nombre legible
    description = Column(Text, nullable=True)
    version = Column(String, default="1.0.0")
    
    # Configuración operativa
    enabled = Column(Integer, default=1)  # 1 = activa, 0 = pausada
    interval_seconds = Column(Integer, default=300)  # Cada cuánto ejecutar (5 min default)
    tokens = Column(String)  # JSON array: ["ETH", "BTC", "SOL"]
    timeframes = Column(String)  # JSON array: ["30m", "1h"]
    
    # Metadatos
    risk_profile = Column(String, default="medium")  # low | medium | high
    mode = Column(String, default="CUSTOM")  # LITE | PRO | CUSTOM
    source_type = Column(String, default="ENGINE")  # ENGINE | LLM | HYBRID
    
    # Estadísticas (actualizadas por evaluaciones)
    total_signals = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    avg_confidence = Column(Float, default=0.0)
    last_execution = Column(DateTime, nullable=True)
    
    # Config JSON (parámetros específicos de la estrategia)
    config_json = Column(Text, nullable=True)  # JSON: {"rsi_period": 14, ...}
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PushSubscription(Base):
    __tablename__ = "push_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, unique=True, index=True)
    p256dh = Column(String)
    auth = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

