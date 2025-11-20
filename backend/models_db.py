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
