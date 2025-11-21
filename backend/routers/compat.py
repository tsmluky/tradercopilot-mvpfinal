from __future__ import annotations
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
import os
import pathlib
import json

from dotenv import load_dotenv

# === Cargar .env directamente desde backend/.env ===
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

router = APIRouter()

# ==== /notify/telegram ====


class TelegramIn(BaseModel):
    text: str


@router.post("/notify/telegram")
def notify_telegram(body: TelegramIn):
    import requests

    token = os.getenv("TRADERCOPILOT_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        # Detalle ampliado para depurar qué falta exactamente
        detail = {
            "error": "Missing TELEGRAM envs",
            "token_present": bool(token),
            "chat_id_present": bool(chat_id),
            "env_path": str(ENV_PATH),
        }
        raise HTTPException(status_code=500, detail=json.dumps(detail))

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    r = requests.post(
        url,
        json={"chat_id": chat_id, "text": body.text, "parse_mode": "HTML"},
        timeout=15,
    )
    if not r.ok:
        raise HTTPException(status_code=502, detail=f"Telegram error: {r.text}")
    return {"ok": True}


# ==== /logs/{mode}/{token} -> stream CSV ====


@router.get("/logs/{mode}/{token}")
def read_logs(mode: str, token: str):
    base = BASE_DIR / "logs"
    p = base / mode.upper() / f"{token.lower()}.csv"
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"Log not found: {p.as_posix()}")
    return Response(p.read_text(encoding="utf-8"), media_type="text/csv")


# ==== Adaptadores /analyze/{lite,pro,advisor} ====


class LiteIn(BaseModel):
    token: str
    timeframe: str = "30m"


async def _call_analyze(payload: dict):
    # Preferimos llamada interna al método si existe; si no, fallback HTTP local
    try:
        from ..main import AnalysisRequest, analyze_token

        req = AnalysisRequest(**payload)
        return await analyze_token(req)
    except Exception:
        import httpx
        
        port = os.getenv("PORT", "8010")
        url = os.getenv("SELF_ANALYZE_URL", f"http://127.0.0.1:{port}/analyze")
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, json=payload)
            if r.status_code >= 400:
                raise HTTPException(status_code=r.status_code, detail=r.text)
            try:
                return r.json()
            except Exception:
                return {"raw": r.text}


@router.post("/analyze/lite")
async def analyze_lite(body: LiteIn):
    payload = {
        "token": body.token.lower(),
        "message": (
            f"Genera una señal LITE timeframe {body.timeframe}. "
            "Devuelve JSON compacto con entry/tp/sl/confidence y razón (≤240c)."
        ),
        "mode": "lite",
        "timeframe": body.timeframe,
    }
    return await _call_analyze(payload)


class ProIn(BaseModel):
    token: str
    timeframe: str = "30m"
    context: Optional[dict] = None


@router.post("/analyze/pro")
async def analyze_pro(body: ProIn):
    payload = {
        "token": body.token.lower(),
        "message": (
            "Análisis PRO en bloque #ANALYSIS_START..END con secciones "
            "#CTXT #TA #PLAN #INSIGHT #PARAMS. Sé estricto."
        ),
        "mode": "pro",
        "timeframe": body.timeframe,
    }
    return await _call_analyze(payload)


class AdvisorIn(BaseModel):
    token: str
    direction: str
    entry: float
    tp: float
    sl: float
    size_quote: float


@router.post("/analyze/advisor")
async def analyze_advisor(body: AdvisorIn):
    payload = {
        "token": body.token.lower(),
        "message": (
            f"Asesor de posición abierta: {body.direction} entry={body.entry} "
            f"tp={body.tp} sl={body.sl} size_quote={body.size_quote}. "
            "Devuelve plan operativo y alternativas."
        ),
        "mode": "assist",
    }
    return await _call_analyze(payload)
