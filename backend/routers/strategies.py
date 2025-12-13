# backend/routers/strategies.py
"""
Endpoints API para gestión de estrategias.

Permite al dashboard:
- Listar estrategias disponibles
- Activar/desactivar estrategias
- Ver estadísticas de performance
- Ejecutar estrategias manualmente (testing)
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from database import SessionLocal
from models_db import StrategyConfig
from strategies.registry import get_registry
from core.signal_logger import log_signal
from pydantic import BaseModel
from marketplace_config import MARKETPLACE_PERSONAS, get_active_strategies

router = APIRouter(prefix="/strategies", tags=["strategies"])

@router.get("/marketplace", response_model=List[Dict[str, Any]])
async def get_marketplace():
    """Retorna la configuración de 'Personas' del Marketplace."""
from models_db import Signal, SignalEvaluation

@router.get("/marketplace/{persona_id}/history")
async def get_persona_history(persona_id: str, db: Session = Depends(get_db)):
    """
    Obtiene el historial de señales generadas por una Persona específica.
    Filtra por source="Marketplace:{persona_id}"
    """
    # Validar persona
    valid_ids = [p["id"] for p in MARKETPLACE_PERSONAS]
    if persona_id not in valid_ids:
        # Fallback para permitir debugear IDs viejos si existen
        # raise HTTPException(status_code=404, detail="Persona not found")
        pass

    target_source = f"Marketplace:{persona_id}"
    
    # Query Signals sorted by time desc
    signals = db.query(Signal).filter(
        Signal.source == target_source
    ).order_by(Signal.timestamp.desc()).limit(100).all()
    
    # Enriquecer con evaluación si existe
    history = []
    for sig in signals:
        eval_data = None
        if sig.evaluation:
            eval_data = {
                "result": sig.evaluation.result,
                "pnl_r": sig.evaluation.pnl_r,
                "exit_price": sig.evaluation.exit_price,
                "closed_at": sig.evaluation.evaluated_at.isoformat() if sig.evaluation.evaluated_at else None
            }
            
        history.append({
            "id": sig.id,
            "timestamp": sig.timestamp.isoformat() + "Z",
            "token": sig.token,
            "direction": sig.direction,
            "entry": sig.entry,
            "tp": sig.tp,
            "sl": sig.sl,
            "result": eval_data
        })
        
    return history



# === Models ===

class StrategyMetadataResponse(BaseModel):
    """Metadatos de una estrategia para el frontend."""
    id: str
    name: str
    description: str
    version: str
    default_timeframe: str
    universe: List[str]
    risk_profile: str
    mode: str
    source_type: str
    enabled: bool
    
    # Stats (si está en DB)
    total_signals: Optional[int] = 0
    win_rate: Optional[float] = 0.0
    last_execution: Optional[datetime] = None


class StrategyConfigUpdate(BaseModel):
    """Actualización de configuración de estrategia."""
    enabled: Optional[bool] = None
    interval_seconds: Optional[int] = None
    tokens: Optional[List[str]] = None
    timeframes: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None


class ExecuteStrategyRequest(BaseModel):
    """Request para ejecutar estrategia manualmente."""
    tokens: List[str]
    timeframe: str = "30m"
    context: Optional[Dict[str, Any]] = None


# === Dependency ===

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# === Endpoints ===

@router.get("/", response_model=List[StrategyMetadataResponse])
async def list_strategies(db: Session = Depends(get_db)):
    """
    Lista todas las estrategias disponibles.
    
    Combina:
    - Estrategias registradas en el registry (código)
    - Configuración de DB (si existe)
    """
    registry = get_registry()
    all_metas = registry.list_all()
    
    results = []
    
    for meta in all_metas:
        # Buscar config en DB
        db_config = db.query(StrategyConfig).filter(
            StrategyConfig.strategy_id == meta.id
        ).first()
        
        result = StrategyMetadataResponse(
            id=meta.id,
            name=meta.name,
            description=meta.description,
            version=meta.version,
            default_timeframe=meta.default_timeframe,
            universe=meta.universe,
            risk_profile=meta.risk_profile,
            mode=meta.mode,
            source_type=meta.source_type,
            enabled=db_config.enabled == 1 if db_config else meta.enabled,
            total_signals=db_config.total_signals if db_config else 0,
            win_rate=db_config.win_rate if db_config else 0.0,
            last_execution=db_config.last_execution if db_config else None,
        )
        results.append(result)
    
    return results


@router.get("/{strategy_id}")
async def get_strategy(strategy_id: str, db: Session = Depends(get_db)):
    """Obtiene detalles de una estrategia específica."""
    registry = get_registry()
    strategy = registry.get(strategy_id)
    
    if not strategy:
        raise HTTPException(status_code=404, detail=f"Strategy '{strategy_id}' not found")
    
    meta = strategy.metadata()
    
    # Buscar config en DB
    db_config = db.query(StrategyConfig).filter(
        StrategyConfig.strategy_id == strategy_id
    ).first()
    
    return {
        "metadata": meta.dict(),
        "config": json.loads(db_config.config_json) if db_config and db_config.config_json else {},
        "stats": {
            "total_signals": db_config.total_signals if db_config else 0,
            "win_rate": db_config.win_rate if db_config else 0.0,
            "avg_confidence": db_config.avg_confidence if db_config else 0.0,
            "last_execution": db_config.last_execution.isoformat() + "Z" if db_config and db_config.last_execution else None,
        }
    }


@router.patch("/{strategy_id}")
async def update_strategy_config(
    strategy_id: str,
    update: StrategyConfigUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza configuración de una estrategia.
    
    Permite:
    - Activar/desactivar (enabled)
    - Cambiar intervalo de ejecución
    - Modificar tokens/timeframes
    - Actualizar config específico
    """
    # Verificar que la estrategia existe en registry
    registry = get_registry()
    strategy = registry.get(strategy_id)
    
    if not strategy:
        raise HTTPException(status_code=404, detail=f"Strategy '{strategy_id}' not found in registry")
    
    # Buscar o crear config en DB
    db_config = db.query(StrategyConfig).filter(
        StrategyConfig.strategy_id == strategy_id
    ).first()
    
    if not db_config:
        # Crear nuevo
        meta = strategy.metadata()
        db_config = StrategyConfig(
            strategy_id=meta.id,
            name=meta.name,
            description=meta.description,
            version=meta.version,
            enabled=1,
            tokens=json.dumps(meta.universe),
            timeframes=json.dumps([meta.default_timeframe]),
            risk_profile=meta.risk_profile,
            mode=meta.mode,
            source_type=meta.source_type,
        )
        db.add(db_config)
    
    # Aplicar updates
    if update.enabled is not None:
        db_config.enabled = 1 if update.enabled else 0
    
    if update.interval_seconds is not None:
        db_config.interval_seconds = update.interval_seconds
    
    if update.tokens is not None:
        db_config.tokens = json.dumps(update.tokens)
    
    if update.timeframes is not None:
        db_config.timeframes = json.dumps(update.timeframes)
    
    if update.config is not None:
        db_config.config_json = json.dumps(update.config)
    
    db_config.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(db_config)
        return {"status": "ok", "strategy_id": strategy_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating strategy: {str(e)}")


@router.post("/{strategy_id}/execute")
async def execute_strategy_manual(
    strategy_id: str,
    req: ExecuteStrategyRequest,
    db: Session = Depends(get_db)
):
    """
    Ejecuta una estrategia manualmente (útil para testing).
    
    No afecta al scheduler automático.
    """
    registry = get_registry()
    
    # Obtener config de DB si existe
    db_config = db.query(StrategyConfig).filter(
        StrategyConfig.strategy_id == strategy_id
    ).first()
    
    config_dict = {}
    if db_config and db_config.config_json:
        config_dict = json.loads(db_config.config_json)
    
    # Instanciar estrategia
    strategy = registry.get(strategy_id, config=config_dict)
    
    if not strategy:
        raise HTTPException(status_code=404, detail=f"Strategy '{strategy_id}' not found")
    
    # Ejecutar
    try:
        signals = strategy.generate_signals(
            tokens=req.tokens,
            timeframe=req.timeframe,
            context=req.context or {}
        )
        
        # Loguear señales
        for signal in signals:
            log_signal(signal)
        
        return {
            "status": "ok",
            "signals_generated": len(signals),
            "signals": [
                {
                    "token": s.token,
                    "direction": s.direction,
                    "entry": s.entry,
                    "tp": s.tp,
                    "sl": s.sl,
                    "confidence": s.confidence,
                }
                for s in signals
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing strategy: {str(e)}")
