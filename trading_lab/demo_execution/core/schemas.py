from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Signal(BaseModel):
    strategy_id: str
    token: str
    timeframe: str
    direction: str
    entry_price: float
    tp_price: float
    sl_price: float
    confidence: float = 100.0
    rationale: str = ""
    source: str = "quant_lab"
    created_at: datetime = datetime.utcnow()
    
    # Campos para evaluación posterior
    status: str = "PENDING" # PENDING, EVALUATED
    result: Optional[str] = None # WIN, LOSS
    exit_price: Optional[float] = None
    pnl_pct: Optional[float] = None
