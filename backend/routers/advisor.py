
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from core.ai_service import get_ai_service
from rag_context import build_token_context
from core.market_data_api import get_ohlcv_data

router = APIRouter(prefix="/advisor", tags=["advisor"])

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatContext(BaseModel):
    token: Optional[str] = None
    timeframe: Optional[str] = None
    signal_data: Optional[Dict[str, Any]] = None # Active signal details if any

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context: Optional[ChatContext] = None

@router.post("/chat")
def advisor_chat(req: ChatRequest):
    """
    Endpoint for interactive chat with the Advisor.
    It injects market context (RAG + Live Data) into the system prompt if a token is specified.
    Uses generic AI Service (DeepSeek or Gemini).
    """
    
    # 1. Build Dynamic System Context if Token is present
    system_context_block = ""
    if req.context and req.context.token:
        token = req.context.token
        tf = req.context.timeframe or "1h"
        
        # A. Fetch Market Data Snapshot
        try:
            ohlcv = get_ohlcv_data(token, tf, limit=1)
            price = ohlcv[0]["close"] if ohlcv else "Unknown"
        except:
            price = "Unavailable"
            
        # B. Fetch RAG Context
        rag = build_token_context(token)
        
        # C. Build Context Block
        system_context_block = f"""
[CURRENT MARKET CONTEXT for {token.upper()}]
- Price: {price}
- Timeframe: {tf}
- Sentiment: {rag.get('sentiment', 'Neutral')}
- News/Narrative: {rag.get('news', 'No major news')}
"""
        # D. Add Signal Context if coming from a specific signal
        if req.context.signal_data:
            sig = req.context.signal_data
            system_context_block += f"""
[ACTIVE SIGNAL CONTEXT]
- Direction: {sig.get('direction', 'Unknown')}
- Entry: {sig.get('entry')}
- TP: {sig.get('tp')} | SL: {sig.get('sl')}
- Confidence: {sig.get('confidence')}
- Rationale: {sig.get('rationale')}
"""

    # 2. Define System Persona (Unified)
    system_instruction = (
        "Eres el Asesor de Riesgo de TraderCopilot (Risk Advisor AI). Ayudas a los traders a gestionar el riesgo, "
        "sugerir ajustes de posición y analizar escenarios de mercado.\n"
        "Sé conciso, profesional y directo. Céntrate en la gestión de riesgos (RR, tamaño de posición, SL/TP).\n"
        "NO des consejos financieros, solo análisis técnico y escenarios de riesgo.\n"
        "Responde SIEMPRE en ESPAÑOL (Castellano)."
    )

    # 3. Call AI Service
    ai_service = get_ai_service()
    
    # Preparar mensajes
    user_api_messages = [m.dict() for m in req.messages]
    
    # Inyectar contexto de mercado en el último mensaje del usuario para asegurar que la IA lo tenga en cuenta
    if system_context_block:
        last_msg = user_api_messages[-1]
        if last_msg["role"] == "user":
            last_msg["content"] = f"{system_context_block}\n\nPregunta del Usuario: {last_msg['content']}"

    response_text = ai_service.chat(user_api_messages, system_instruction=system_instruction)
    
    return {"reply": response_text}

# ==== Endpoint Analysis Advisor (Legacy V1 Local) ====
from models import AdvisorReq
from core.schemas import Signal
from core.signal_logger import log_signal
from datetime import datetime

@router.post("/")
def analyze_advisor(req: AdvisorReq):
    """
    Analiza una posición abierta y sugiere alternativas.
    Versión local determinista (sin LLM).
    """
    token = req.token.upper()
    
    # Lógica simple de evaluación de riesgo
    risk_per_share = abs(req.entry - req.sl)
    reward_per_share = abs(req.tp - req.entry)
    rr = reward_per_share / risk_per_share if risk_per_share > 0 else 0
    
    risk_score = 0.5
    if rr < 1.0:
        risk_score = 0.9
    elif rr > 2.0:
        risk_score = 0.3
        
    confidence = 0.6
    
    alternatives = []
    if risk_score > 0.7:
        alternatives.append({
            "if": "price consolidates",
            "action": "tighten SL",
            "rr_target": 1.5
        })
    else:
        alternatives.append({
            "if": "volume spikes",
            "action": "add to position",
            "rr_target": 2.5
        })

    response = {
        "token": token,
        "direction": req.direction,
        "entry": req.entry,
        "size_quote": req.size_quote,
        "tp": req.tp,
        "sl": req.sl,
        "alternatives": alternatives,
        "risk_score": round(risk_score, 2),
        "confidence": confidence
    }
    
    # Crear instancia de Signal unificado para ADVISOR
    unified_signal = Signal(
        timestamp=datetime.utcnow(),
        strategy_id="advisor_v1_local",
        mode="ADVISOR",
        token=token,
        timeframe="N/A",  # ADVISOR no tiene timeframe específico
        direction=req.direction,
        entry=req.entry,
        tp=req.tp,
        sl=req.sl,
        confidence=confidence,
        rationale=f"Advisor position check. RR={rr:.2f}",
        source="ADVISOR_V1_LOCAL",
        extra={
            "risk_score": risk_score,
            "rr_ratio": round(rr, 2),
            "size_quote": req.size_quote,
            "alternatives": alternatives,
        }
    )
    
    log_signal(unified_signal)
    
    return response
