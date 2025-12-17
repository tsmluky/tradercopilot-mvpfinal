from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import SessionLocal
from models_db import Signal, SignalEvaluation
from pydantic import BaseModel
from datetime import datetime
from routers.auth import get_current_user
from models_db import User, Signal, SignalEvaluation

router = APIRouter(tags=["logs"])

class LogEntry(BaseModel):
    id: int
    timestamp: datetime
    token: str
    timeframe: str
    direction: str
    entry: float
    tp: float
    sl: float
    confidence: float
    source: str  # Changed from strategy_id to match DB schema
    mode: str
    status: str = "OPEN"
    pnl: Optional[float] = None
    
    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/recent", response_model=List[LogEntry])
def get_recent_logs(
    limit: int = 20, 
    mode: Optional[str] = None, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene las señales más recientes (User + System).
    """
    try:
        from sqlalchemy import or_
        query = db.query(Signal).filter(
            or_(Signal.user_id == current_user.id, Signal.user_id == None)
        ).order_by(desc(Signal.timestamp))
        
        if mode:
            query = query.filter(Signal.mode == mode)
            
        signals = query.limit(limit).all()
        
        # Enriquecer con evaluación si existe
        results = []
        for sig in signals:
            # Buscar evaluación
            eval_entry = db.query(SignalEvaluation).filter(
                SignalEvaluation.signal_id == sig.id
            ).first()
            
            status = "OPEN"
            pnl = None
            
            if eval_entry:
                status = eval_entry.result  # WIN, LOSS, BE
                pnl = eval_entry.pnl_r
            
            results.append(LogEntry(
                id=sig.id,
                timestamp=sig.timestamp,
                token=sig.token or "UNKNOWN",
                timeframe=sig.timeframe or "1h",
                direction=sig.direction or "neutral",
                entry=sig.entry or 0.0,
                tp=sig.tp or 0.0,
                sl=sig.sl or 0.0,
                confidence=sig.confidence or 0.0,
                source=sig.source or sig.strategy_id or "System",
                mode=sig.mode or "LITE",
                status=status,
                pnl=pnl
            ))
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching logs: {str(e)}")

@router.get("/{mode}/{token}")
def get_logs_by_token(
    mode: str, 
    token: str, 
    limit: int = 50, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint de compatibilidad para fetchLogs.
    Devuelve logs filtrados por modo y token (User + System).
    """
    try:
        from sqlalchemy import or_
        query = db.query(Signal).filter(
            Signal.mode == mode.upper(),
            or_(Signal.user_id == current_user.id, Signal.user_id == None)
        )
        
        if token.lower() != "all":
            query = query.filter(Signal.token == token.upper())
            
        signals = query.order_by(desc(Signal.timestamp)).limit(limit).all()
        
        # Mapear a formato simple
        return [
            {
                "timestamp": s.timestamp.isoformat(),
                "token": s.token,
                "timeframe": s.timeframe,
                "direction": s.direction,
                "entry": s.entry,
                "tp": s.tp,
                "sl": s.sl,
                "confidence": s.confidence,
                "source": s.source  # Changed from strategy_id
            }
            for s in signals
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching logs: {str(e)}")
