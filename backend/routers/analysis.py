from fastapi import APIRouter, HTTPException
import traceback
from typing import Dict, Any, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field

# Imports internos
from indicators.market import get_market_data
from models import LiteReq, ProReq
from core.schemas import Signal
from core.signal_logger import log_signal
# Logic imports
from core.analysis_logic import (
    _build_lite_from_market,
    _load_brain_context,
    _inject_rag_into_lite_rationale,
    _build_pro_markdown
)

router = APIRouter()

# ==== 9. Endpoint LITE ====

@router.post("/lite")
def analyze_lite(req: LiteReq):
    """
    Wrapper seguro para capturar errores 500 y mostrarlos en el frontend.
    """
    try:
        return _analyze_lite_unsafe(req)
    except Exception as e:
        print(f"CRITICAL ERROR IN ANALYZE_LITE: {e}")
        traceback.print_exc()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "token": req.token,
            "timeframe": req.timeframe,
            "direction": "neutral",
            "entry": 0.0,
            "tp": 0.0,
            "sl": 0.0,
            "confidence": 0.0,
            "rationale": f"CRASH DEBUG: {str(e)}",
            "source": "debug-handler",
            "indicators": {}
        }

def _analyze_lite_unsafe(req: LiteReq):
    """
    Lógica real de Lite Analysis (Refactored to logic module).
    """
    try:
        # 1. Market Data
        # Call market_data_api directly or use helper?
        # In main it used: from indicators.market import get_market_data
        df, market = get_market_data(req.token, req.timeframe, limit=300)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Market data error: {e}")

    # 2. Build Base Signal (Logic)
    lite_signal, indicators = _build_lite_from_market(req.token, req.timeframe, market)

    # 3. RAG/Context Injection (Optional)
    try:
        final_rationale = _inject_rag_into_lite_rationale(req.token, req.timeframe, lite_signal, market)
        lite_signal.rationale = final_rationale
    except Exception as e:
        print(f"RAG Injection Failed: {e}")

    # 4. Log & Response
    # Convert to unified Signal model for logging
    log_payload = lite_signal.dict()
    # Need to adapt to unified Signal manually or use helper?
    # In main.py lines 800+ it did manual logging.
    # Let's use the Unified Signal schema directly if possible, or mapping.
    # Actually, lite_signal is LiteSignal model.
    
    # Create Unified Signal for Logger
    unified_sig = Signal(
        timestamp=lite_signal.timestamp,
        strategy_id="lite_v2_router",
        mode="LITE",
        token=lite_signal.token,
        timeframe=lite_signal.timeframe,
        direction=lite_signal.direction,
        entry=lite_signal.entry,
        tp=lite_signal.tp,
        sl=lite_signal.sl,
        confidence=lite_signal.confidence,
        rationale=lite_signal.rationale,
        source=lite_signal.source,
        extra=indicators
    )
    
    log_signal(unified_sig)

    response = lite_signal.model_dump()
    response["indicators"] = indicators
    return response


# ==== 10. Endpoint PRO ====

@router.post("/pro")
async def analyze_pro(req: ProReq):
    """
    Generates a deep AI analysis using Gemini/DeepSeek.
    """
    # 1. Get LITE foundation
    # We re-run lite logic to get the technical base
    try:
        df, market = get_market_data(req.token, req.timeframe, limit=300)
        lite_signal, indicators = _build_lite_from_market(req.token, req.timeframe, market)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build base technicals: {e}")

    # 2. Load Deep Context (RAG)
    brain_context = _load_brain_context(req.token, market_data=market)

    # 3. Generate Analysis
    markdown_report = await _build_pro_markdown(req, lite_signal, indicators, brain_context)

    # 4. Log (Optional, maybe we only log LITE signals?)
    # PRO requests are expensive, usually we check if we want to log them.
    # For now, just return.

    return {
        "markdown": markdown_report,
        "token": req.token,
        "mode": "PRO",
        "timestamp": datetime.utcnow().isoformat()
    }

