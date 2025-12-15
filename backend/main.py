import sys
import os
import asyncio
import csv
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, HTTPException, Request
from dotenv import load_dotenv

# ==== 1. Configuración de entorno ====
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
load_dotenv(os.path.join(current_dir, ".env"))

# ==== 2. Imports locales ====
from indicators.market import get_market_data  # Capa Quant
from models import LiteReq, LiteSignal, ProReq, AdvisorReq  # Modelos oficiales LITE/PRO
from pydantic import BaseModel

# === 2b. Imports del Signal Hub unificado ===
from core.schemas import Signal
from core.signal_logger import log_signal, signal_from_dict

# === 2c. RAG Context ===
from rag_context import build_token_context

# ==== 3. FastAPI App ====

# FIX: Windows + Async PG functionality requires SelectorEventLoopPolicy
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(
    title="TraderCopilot Backend",
    version="0.8.2-force",
    description="API principal para generación de señales y registro de logs. (Forced Deployment)"
)

@app.get("/health")
def health_check():
    return {"status": "ok", "db": "connected"}

# === CORS Configuration ===
# En desarrollo: localhost
# En producción (Railway): permitir todos los orígenes o configurar específicamente
# CORS Configuration - Permissive for MVP
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4173",
    "https://tradercopilot-mvpfinal.vercel.app",
    "*" 
]
print(f"[CORS] Allowed Origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== DB Init ====
from database import engine, Base
from models_db import Signal as SignalDB, SignalEvaluation, User, StrategyConfig  # Import models to register them

@app.on_event("startup")
async def startup():
    # Diagnóstico de DB
    db_url = os.getenv("DATABASE_URL", "")
    if "sqlite" in db_url or not db_url:
        print("⚠️  [WARNING] Using SQLite (Ephemeral). Data WILL BE LOST on redeploy.")
        print("👉  To fix: Connect a PostgreSQL service in Railway and set DATABASE_URL.")
    else:
        print("✅  [INFO] Using PostgreSQL (Persistent).")
        
    print(f"[DB] Connection URL: {db_url.split('@')[-1] if '@' in db_url else 'sqlite://...'}")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Registrar estrategias built-in
    print("\n📦 Registering strategies...")
    from strategies.registry import get_registry
    from strategies.example_rsi_macd import RSIMACDDivergenceStrategy
    from strategies.ma_cross import MACrossStrategy
    from strategies.donchian import DonchianStrategy
    from strategies.bb_mean_reversion import BBMeanReversionStrategy
    
    registry = get_registry()
    registry.register(RSIMACDDivergenceStrategy)
    registry.register(MACrossStrategy)
    registry.register(DonchianStrategy)
    registry.register(BBMeanReversionStrategy)
    print("✅ Strategies registered\n")


# ==== Routers ====
from routers.strategies import router as strategies_router
from routers.logs import router as logs_router
from routers.notifications import router as notifications_router
from routers.advisor import router as advisor_router
from routers.backtest import router as backtest_router
from routers.auth import router as auth_router # [NEW] Auth Support

app.include_router(strategies_router)
app.include_router(logs_router)
app.include_router(notifications_router)
app.include_router(advisor_router)
app.include_router(backtest_router)
app.include_router(auth_router) # [NEW] Register Auth Router


# ==== 4. Configuración global ====
LOGS_DIR = os.path.join(current_dir, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

CSV_HEADERS = [
    "timestamp", "token", "timeframe", "direction", "entry", "tp", "sl",
    "confidence", "rationale", "source"
]


# ==== 5. Funciones auxiliares (logs genéricos) ====

def save_strict_log(mode: str, data: Dict[str, Any]) -> None:
    """
    Guarda una señal en logs/{MODE}/{token}.csv Y en la base de datos.

    - mode se almacena en mayúsculas (LITE, PRO, ADVISOR).
    - token se normaliza a minúsculas para el nombre del fichero: eth.csv, btc.csv, etc.

    Nota: el modo EVALUATED tiene su propio formato y fichero
    {token}.evaluated.csv gestionado por evaluated_logger.py, no por esta función.
    """
    # 1. Guardar en CSV (legacy/backup)
    mode_dir = os.path.join(LOGS_DIR, mode.upper())
    os.makedirs(mode_dir, exist_ok=True)

    token = data.get("token", "unknown")
    token_file = token.lower()
    filepath = os.path.join(mode_dir, f"{token_file}.csv")

    file_exists = os.path.isfile(filepath)
    with open(filepath, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({k: data.get(k, "") for k in CSV_HEADERS})

    # 2. Guardar en base de datos
    try:
        from sqlalchemy import select
        from models_db import Signal
        from database import SessionLocal
        
        # Parse timestamp
        ts_str = data.get("timestamp", datetime.utcnow().isoformat() + "Z")
        try:
            timestamp = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        except:
            timestamp = datetime.utcnow()
        
        # Create signal record
        signal = Signal(
            timestamp=timestamp,
            token=data.get("token", "").upper(),
            timeframe=data.get("timeframe", ""),
            direction=data.get("direction", ""),
            entry=float(data.get("entry", 0)),
            tp=float(data.get("tp", 0)),
            sl=float(data.get("sl", 0)),
            confidence=float(data.get("confidence", 0)),
            rationale=data.get("rationale", ""),
            source=data.get("source", ""),
            mode=mode.upper(),
            raw_response=data.get("raw_response", None)
        )
        
        # Save to database
        db = SessionLocal()
        try:
            db.add(signal)
            db.commit()
            print(f"[DB] ✅ Señal guardada en DB: {mode} - {signal.token} - {ts_str}")
        except Exception as db_err:
            print(f"[DB] ❌ Error CRÍTICO al guardar en DB: {db_err}")
            db.rollback()
        finally:
            db.close()
    except Exception as e:
        print(f"[DB] ⚠️  Warning: Failed to save signal to database: {e}")
        import traceback
        traceback.print_exc()
        # Continue even if DB save fails (CSV is saved)


def read_logs_by_token_and_mode(mode: str, token: str) -> List[dict]:
    """
    Lee los logs de un token y modo específico.

    - Para LITE, PRO, ADVISOR → backend/logs/{MODE}/{token}.csv
    - Para EVALUATED          → backend/logs/EVALUATED/{token}.evaluated.csv
    """
    mode_up = mode.upper()
    token_low = token.lower()

    if mode_up == "EVALUATED":
        filename = f"{token_low}.evaluated.csv"
    else:
        filename = f"{token_low}.csv"

    filepath = os.path.join(LOGS_DIR, mode_up, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"No logs found for {mode}/{token}")

    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


# ==== 6. Capa Quant + LITE core ====

def _build_lite_from_market(token: str, timeframe: str, market: Dict[str, Any]) -> Tuple[LiteSignal, Dict[str, Any]]:
    """
    Aplica la lógica LITE v2 sobre los datos de mercado y devuelve:

    - LiteSignal (modelo oficial)
    - dict con indicadores (para enriquecer la respuesta)
    """

    # Extract & normalize
    try:
        price = float(market["price"])
        rsi = float(market["rsi"])
        trend = str(market.get("trend", "NEUTRAL")).upper()
        ema21 = float(market["ema21"])
        macd = float(market["macd"])
        macd_hist = float(market["macd_hist"])
        atr = float(market.get("atr", price * 0.01))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=502, detail=f"Invalid market data: {exc!r}")

    if price <= 0:
        raise HTTPException(status_code=502, detail="Market data inválido: price <= 0")

    # == 2. Inicialización ==
    direction: Optional[str] = None
    rationale = "Contexto sin setup claro."
    confidence = 0.5
    tp = price
    sl = price

    # == 3. Lógica de decisión (Lite v2 adaptada) ==

    # A) Reversión (Contratendencia)
    if rsi < 30:
        direction = "long"
        rationale = f"Setup LONG (scalp) por sobreventa extrema (RSI {rsi:.1f}). Posible rebote."
        confidence = 0.7
        sl = price * 0.98
        tp = price * 1.03

    elif rsi > 75:
        direction = "short"
        rationale = f"Setup SHORT (scalp) por sobrecompra extrema (RSI {rsi:.1f}). Posible corrección."
        confidence = 0.7
        sl = price * 1.02
        tp = price * 0.97

    # B) Trend Following (a favor de tendencia) en rango de RSI medio
    elif 35 < rsi < 65:
        # Setup bajista
        if price < ema21 and macd < 0 and macd_hist < 0:
            direction = "short"
            rationale = (
                "Setup SHORT (trend): precio < EMA21 con MACD bajista. "
                "Tendencia bajista consolidada."
            )
            confidence = 0.8
            sl = price * 1.025
            tp = price * 0.95

        # Setup alcista
        elif price > ema21 and macd > 0 and macd_hist > 0:
            direction = "long"
            rationale = (
                "Setup LONG (trend): precio > EMA21 con MACD alcista. "
                "Tendencia alcista consolidada."
            )
            confidence = 0.8
            sl = price * 0.975
            tp = price * 1.05

    # C) Fallback si no hay setup claro (pero siempre devolvemos long|short)
    if direction is None:
        if trend == "BULLISH":
            direction = "long"
            rationale = (
                f"Sin setup claro, pero tendencia global alcista (trend={trend}, RSI {rsi:.1f}). "
                "Señal exploratoria de menor confianza."
            )
        else:
            direction = "short"
            rationale = (
                f"Sin setup claro, pero tendencia global bajista (trend={trend}, RSI {rsi:.1f}). "
                "Señal exploratoria de menor confianza."
            )
        confidence = 0.45
        if direction == "long":
            sl = price * 0.985
            tp = price * 1.02
        else:
            sl = price * 1.015
            tp = price * 0.98

    # Limitar rationale a 240 caracteres por contrato
    if len(rationale) > 240:
        rationale = rationale[:237] + "..."

    # Timestamp UTC (sin tzinfo pero con sufijo Z en logs)
    now_dt = datetime.utcnow()

    lite = LiteSignal(
        timestamp=now_dt,
        token=token.upper(),      # ETH/BTC/SOL/XAU
        timeframe=timeframe,
        direction=direction,      # type: ignore[arg-type]
        entry=round(price, 2),
        tp=round(tp, 2),
        sl=round(sl, 2),
        confidence=round(confidence, 2),
        rationale=rationale,
        source="lite-rule@v2",    # versión de la regla LITE
    )

    indicators = {
        "rsi": rsi,
        "trend": trend,
        "macd": round(macd, 2),
        "ema21": round(ema21, 2),
        "atr": atr,
    }

    return lite, indicators


# ==== 7. Capa RAG básica (vía rag_context) ====


def _load_brain_context(token: str) -> Dict[str, str]:
    """
    Wrapper sobre build_token_context(token) para mantener compatibilidad
    con el resto del código PRO.

    Devuelve al menos las claves:
    - insights
    - news
    - onchain
    - sentiment
    - snapshot
    - raw_context
    """
    token_ctx = build_token_context(token)
    return {
        "insights": token_ctx.get("insights", "") or "",
        "news": token_ctx.get("news", "") or "",
        "onchain": token_ctx.get("onchain", "") or "",
        "sentiment": token_ctx.get("sentiment", "") or "",
        "snapshot": token_ctx.get("snapshot", "") or "",
        "raw_context": token_ctx.get("raw_context", "") or "",
    }


def _inject_rag_into_lite_rationale(
    token: str,
    timeframe: str,
    lite: LiteSignal,
    market: Dict[str, Any],
) -> str:
    """
    Ajusta la rationale de LITE combinando:
    - Texto base de la regla (lite-rule@v2).
    - Comentario simple sobre el entorno 24h.
    - Una frase corta de contexto RAG (sentiment/news) sin recortes agresivos.

    Importante: NO recorta por longitud más allá de lo que la UI soporte.
    """
    base = (lite.rationale or "").strip()
    extra_parts: List[str] = []

    # 1) Ajuste por cambio 24h
    change_24h = market.get("price_change_24h")
    if isinstance(change_24h, (int, float)):
        ch = round(change_24h, 2)
        if ch <= -5 and lite.direction == "long":
            extra_parts.append("24h en fuerte caída; usar tamaño de posición conservador.")
        elif ch >= 5 and lite.direction == "short":
            extra_parts.append("24h muy alcistas; evitar shorts agresivos.")
        elif abs(ch) >= 4:
            extra_parts.append("Entorno 24h volátil; gestionar bien el riesgo.")

    # 2) Frase de contexto desde RAG
    try:
        brain = _load_brain_context(token)
        raw_sentiment = (brain.get("sentiment") or "").strip()
        raw_news = (brain.get("news") or "").strip()

        raw = raw_sentiment or raw_news

        tagline = None
        if raw:
            for line in raw.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                tagline = line.lstrip("# ").strip()
                break

        if tagline:
            # Si acaba en ":" (porque en el .md sigue una lista), lo dejamos tal cual.
            extra_parts.append(f"Ctx: {tagline}")
    except Exception:
        # No queremos que un fallo de RAG rompa la señal LITE
        pass

    combined = base
    if extra_parts:
        if not combined.endswith("."):
            combined += "."
        combined += " " + " ".join(extra_parts)

    return combined

def _build_pro_markdown(
    req: ProReq,
    lite: LiteSignal,
    indicators: Dict[str, Any],
    brain: Dict[str, str],
) -> str:
    """
    Construye un prompt y delega en Gemini Flash para el análisis PRO.
    """
    # 1. Extract context
    token_up = lite.token
    tf = lite.timeframe
    user_msg = (req.user_message or "").strip()

    rsi = indicators.get("rsi", "N/D")
    trend = indicators.get("trend", "NEUTRAL")
    ema21 = indicators.get("ema21", "N/D")
    
    # Format numbers
    rsi_str = f"{rsi:.1f}" if isinstance(rsi, (int, float)) else str(rsi)
    ema21_str = f"{ema21:.2f}" if isinstance(ema21, (int, float)) else str(ema21)

    insights = brain.get("insights", "Sin información").strip()
    news = brain.get("news", "Sin noticias recientes").strip()
    onchain = brain.get("onchain", "Sin datos onchain relevantes").strip()
    sentiment_txt = brain.get("sentiment", "Neutral").strip()
    snapshot = brain.get("snapshot", "").strip()

    # 2. Build Prompt
    from gemini_client import generate_pro

    prompt = f"""
Has recibido una solicitud de análisis PRO para {token_up} en timeframe {tf}.

DATOS TÉCNICOS (LITE):
- Dirección: {lite.direction.upper()}
- Entrada Sugerida: {lite.entry}
- TP Sugerido: {lite.tp}
- SL Sugerido: {lite.sl}
- RSI: {rsi_str}
- EMA21: {ema21_str}
- Tendencia: {trend}

CONTEXTO DE MERCADO (RAG):
- Insight Clave: {insights}
- Noticias: {news}
- OnChain: {onchain}
- Sentimiento: {sentiment_txt}
- Snapshot Precio: {snapshot}

MENSAJE DEL USUARIO:
{user_msg if user_msg else "Ninguno"}

TAREA:
Genera un informe profesional institucional.
Debes rellenar EXACTAMENTE las secciones requeridas.
Sé conciso pero "insightful". No uses relleno. Queremos que el usuario sienta que habla con un Senior Quant.
Integra los datos técnicos con el contexto fundamental/onchain si tiene sentido.
Si el sentimiento o noticias contradicen la señal técnica, menciónalo como riesgo.

FORMATO DE SALIDA (Estricto):
#ANALYSIS_START
#CTXT#
(Resumen ejecutivo de la situación macro/técnica)
#TA#
(Análisis técnico detallado: estructura, liquidez, indicadores)
#PLAN#
(Plan de ejecución, gestión de la posición)
#INSIGHT#
(Un dato clave fundamental, onchain o psicológico que apoye la tesis)
#PARAMS#
Entry: {lite.entry}
TP: {lite.tp}
SL: {lite.sl}
#ANALYSIS_END
"""

    # 3. Call AI
    return generate_pro(prompt)



# ==== 8. Rutas base ====

@app.get("/")
def health_check():
    return {"status": "ok", "version": "v0.8.1"}


# ==== Market Data API ====
from market_data_api import get_ohlcv_data, get_market_summary

@app.get("/market/summary")
def market_summary_endpoint():
    """
    Returns price and 24h change for the default watchlist.
    """
    try:
        watchlist = ["BTC", "ETH", "SOL", "XRP", "BNB", "DOGE", "ADA", "AVAX", "DOT", "LINK", "LTC", "MATIC", "UNI", "ATOM", "NEAR"]
        data = get_market_summary(watchlist)
        return {"current_prices": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_market_ohlcv(token: str, timeframe: str = "30m", limit: int = 100):
    """
    Obtiene datos OHLCV (candlestick) para un token específico.
    
    Args:
        token: Símbolo del token (btc, eth, sol)
        timeframe: Intervalo de tiempo (1m, 5m, 15m, 30m, 1h, 4h, 1d)
        limit: Número de velas a retornar (máx 1000)
    
    Returns:
        Lista de datos OHLCV
    """
    try:
        data = get_ohlcv_data(token, timeframe, limit)
        return {"status": "ok", "data": data, "symbol": token.upper(), "timeframe": timeframe}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market data: {str(e)}")

# ==== Logs CSV por modo/token ===============================================

@app.get("/logs/{mode}/{token}")
async def get_logs(mode: str, token: str):
    """
    Devuelve logs en JSON a partir de la DB (con fallback a CSV).

    - LITE/PRO/ADVISOR
    - EVALUATED
    """
    mode_upper = mode.upper()
    token_lower = token.lower()
    
    print(f"[LOGS] Request received: mode={mode_upper}, token={token_lower}")

    allowed_modes = {"LITE", "PRO", "ADVISOR", "EVALUATED"}
    if mode_upper not in allowed_modes:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {mode}")

    # Lista maestra de logs
    all_logs = []

    # 1. Intentar leer de DB (PostgreSQL/SQLite)
    try:
        from database import AsyncSessionLocal
        from models_db import Signal
        from sqlalchemy import select, desc
        
        async with AsyncSessionLocal() as session:
            query = select(Signal).where(Signal.mode == mode_upper)
            
            if token_lower != "all":
                query = query.where(Signal.token == token.upper())
            
            # Traemos hasta 100 de la DB
            query = query.order_by(desc(Signal.timestamp)).limit(100)
            
            result = await session.execute(query)
            signals = result.scalars().all()
            
            if signals:
                db_logs = [
                    {
                        "timestamp": s.timestamp.isoformat() + "Z" if s.timestamp.tzinfo is None else s.timestamp.isoformat(),
                        "token": s.token,
                        "timeframe": s.timeframe,
                        "direction": s.direction,
                        "entry": s.entry,
                        "tp": s.tp,
                        "sl": s.sl,
                        "confidence": s.confidence,
                        "rationale": s.rationale,
                        "source": s.source,
                        "result": "OPEN" 
                    }
                    for s in signals
                ]
                all_logs.extend(db_logs)
                print(f"[LOGS] Loaded {len(db_logs)} logs from DB")

    except Exception as e:
        print(f"[LOGS] Error reading from DB: {e}. Falling back to CSV.")
        # 2. Fallback: Leer de CSV solo si DB falla completamente
        mode_dir = os.path.join(LOGS_DIR, mode_upper)
        if os.path.exists(mode_dir):
            csv_logs = []
            # Si token es 'all', leemos TODOS los CSVs
            if token_lower == "all":
                try:
                    for filename in os.listdir(mode_dir):
                        if filename.endswith(".csv"):
                            filepath = os.path.join(mode_dir, filename)
                            with open(filepath, newline="", encoding="utf-8") as f:
                                reader = csv.DictReader(f)
                                for row in reader:
                                    if "token" not in row:
                                        row["token"] = filename.replace(".csv", "").replace(".evaluated", "").upper()
                                    csv_logs.append(row)
                except Exception as e:
                    print(f"[LOGS] Error reading CSVs for ALL: {e}")
            else:
                # Token específico
                filename = f"{token_lower}.evaluated.csv" if mode_upper == "EVALUATED" else f"{token_lower}.csv"
                csv_path = os.path.join(mode_dir, filename)
                if os.path.exists(csv_path):
                    try:
                        with open(csv_path, newline="", encoding="utf-8") as f:
                            reader = csv.DictReader(f)
                            for row in reader:
                                csv_logs.append(row)
                    except Exception as e:
                        print(f"[LOGS] Error reading CSV {filename}: {e}")

            if csv_logs:
                print(f"[LOGS] Loaded {len(csv_logs)} logs from CSV")
                all_logs.extend(csv_logs)

    # 3. Ordenar todo por timestamp descendente y limitar
    # Normalizamos timestamps para poder ordenar
    def parse_ts(log):
        ts = log.get("timestamp", "")
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except:
            return datetime.min

    all_logs.sort(key=parse_ts, reverse=True)
    
    # Devolver solo los 100 más recientes
    final_logs = all_logs[:100]

    return {"count": len(final_logs), "logs": final_logs}

# ==== 9. Endpoint Evaluacion ====

@app.post("/analyze/evaluate")
def trigger_evaluation():
    """
    Ejecuta el proceso de evaluación de señales bajo demanda.
    Revisa todas las señales LITE pendientes y verifica si tocaron TP/SL.
    """
    try:
        from evaluated_logger import evaluate_all_tokens
        tokens_count, new_evals = evaluate_all_tokens()
        return {
            "status": "ok",
            "tokens_processed": tokens_count,
            "new_evaluations": new_evals,
            "message": f"Evaluated {new_evals} new signals across {tokens_count} tokens."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


# ==== 9. Endpoint LITE ====

@app.post("/analyze/lite")
def analyze_lite(req: LiteReq):
    """
    Genera una señal LITE para un token/timeframe, usando la lógica LITE v2 adaptada
    a contratos oficiales, enriquecida con:

    - Contexto RAG básico desde brain/{token}/
    - Snapshot cuantitativo de mercado (precio + variación 24h si está disponible)
    - Rotación ligera de snippets para evitar sensación de texto repetido

    Ahora usa el schema Signal unificado del Signal Hub.

    - direction ∈ {"long","short"}
    - token en mayúsculas en la respuesta y en el CSV
    - timestamp en logs con sufijo Z
    """
    token = req.token.lower()
    tf = req.timeframe

    # 1) Capa Quant
    df, market = get_market_data(token, tf, limit=300)
    if not market:
        raise HTTPException(status_code=502, detail="Error fetching market data")

    # 2) Construcción de señal LITE (modelo Pydantic + validación)
    lite_signal, indicators = _build_lite_from_market(token, tf, market)

    # 3) Capa RAG básica (enriquecimiento de contexto para Lite)
    brain_ctx = _load_brain_context(token)

    sentiment_txt = brain_ctx.get("sentiment", "").strip()
    insights_txt = brain_ctx.get("insights", "").strip()
    news_txt = brain_ctx.get("news", "").strip()
    onchain_txt = brain_ctx.get("onchain", "").strip()

    # 3.1) Snapshot simple de mercado usando la misma capa Quant
    snapshot = ""
    try:
        price_now = float(market.get("price"))
        ch24 = market.get("change_24h")
        if ch24 is not None:
            snapshot = f"{lite_signal.token} = {price_now:.2f} USD · 24h: {float(ch24):.2f}%"
        else:
            snapshot = f"{lite_signal.token} = {price_now:.2f} USD"
    except Exception:
        snapshot = ""

    # 3.2) Selección ligera / rotación de snippets para evitar sensación de "copypaste"
    context_snippets: List[str] = []
    if snapshot:
        context_snippets.append(f"Snapshot mercado: {snapshot}.")
    if sentiment_txt:
        context_snippets.append(sentiment_txt.splitlines()[0])
    if insights_txt:
        context_snippets.append(insights_txt.splitlines()[0])
    if news_txt:
        context_snippets.append(news_txt.splitlines()[0])

    if context_snippets:
        import random
        extra_context = random.choice(context_snippets).strip()
        lite_signal.rationale = f"{lite_signal.rationale} | Ctx: {extra_context}"
        # Reaplicar límite duro de 240 caracteres
        if len(lite_signal.rationale) > 240:
            lite_signal.rationale = lite_signal.rationale[:237] + "..."

    # 3.3) Adjuntar metadatos RAG a los indicadores (para UI / debugging)
    indicators["rag"] = {
        "snapshot": snapshot,
        "has_sentiment": bool(sentiment_txt),
        "has_insights": bool(insights_txt),
        "has_news": bool(news_txt),
        "has_onchain": bool(onchain_txt),
        "sources_used": [
            key for key, value in {
                "insights": insights_txt,
                "news": news_txt,
                "onchain": onchain_txt,
                "sentiment": sentiment_txt,
            }.items() if value
        ],
    }

    # 4) Crear instancia de Signal unificado
    unified_signal = Signal(
        timestamp=lite_signal.timestamp,
        strategy_id="lite_v2",  # ID de la estrategia
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
        extra={
            "indicators": indicators  # Metadatos adicionales (incluyendo RAG)
        }
    )

    # 5) Guardar usando el logger unificado
    log_signal(unified_signal)

    # 6) Respuesta (base LITE + indicadores extra para UI)
    response = lite_signal.model_dump()
    response["indicators"] = indicators
    return response


# ==== 10. Endpoint PRO v1 (sin LLM, con RAG local) ====

@app.post("/analyze/pro")
def analyze_pro(req: ProReq):
    """
    Genera un análisis PRO en formato Markdown estructurado (#ANALYSIS_START..END),
    combinando:

    - Señal LITE sugerida (sesgo + niveles)
    - Contexto RAG desde brain/{token}/ vía rag_context.build_token_context
    - Mensaje opcional del usuario (user_message)

    Ahora usa el schema Signal unificado del Signal Hub.

    Por ahora NO llama a ningún LLM externo: el análisis es determinista.
    Más adelante se sustituirá la construcción interna por una llamada a DeepSeek/GPT
    manteniendo el mismo contrato de salida.
    """
    token = req.token.lower()
    tf = req.timeframe

    # 1) Capa Quant
    df, market = get_market_data(token, tf, limit=200)
    if not market:
        raise HTTPException(status_code=502, detail="Error fetching market data")

    # 2) Señal LITE interna como "ancla" táctica
    lite_signal, indicators = _build_lite_from_market(token, tf, market)

    # 3) Contexto RAG (wrapper sobre rag_context)
    brain_ctx = _load_brain_context(token)

    # 4) Markdown PRO
    markdown = _build_pro_markdown(req, lite_signal, indicators, brain_ctx)

    # 5) Crear instancia de Signal unificado para PRO
    unified_signal = Signal(
        timestamp=datetime.utcnow(),
        strategy_id="pro_v1_local",
        mode="PRO",
        token=lite_signal.token,
        timeframe=lite_signal.timeframe,
        direction=lite_signal.direction,
        entry=lite_signal.entry,
        tp=lite_signal.tp,
        sl=lite_signal.sl,
        confidence=lite_signal.confidence,
        rationale="PRO analysis generated (local v1, sin LLM)",
        source="PRO_V1_LOCAL",
        extra={
            "analysis_markdown": markdown,
            "rag_sources_used": list(brain_ctx.keys()),
            "user_message": req.user_message,
        }
    )

    # 6) Guardar usando el logger unificado
    log_signal(unified_signal)

    # 7) Respuesta: mantenemos JSON para que el frontend tenga margen
    return {
        "analysis": markdown,
        "meta": {
            "token": lite_signal.token,
            "timeframe": lite_signal.timeframe,
            "direction_bias": lite_signal.direction,
            "entry_hint": lite_signal.entry,
            "tp_hint": lite_signal.tp,
            "sl_hint": lite_signal.sl,
            "lite_confidence": lite_signal.confidence,
            "rag_used": True,
        },
    }


# ==== 11. Endpoint ADVISOR (Local v1) ====

@app.post("/analyze/advisor")
def analyze_advisor(req: AdvisorReq):
    """
    Analiza una posición abierta y sugiere alternativas.
    Versión local determinista (sin LLM).
    
    Ahora usa el schema Signal unificado del Signal Hub.
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
    
    # Guardar usando el logger unificado
    log_signal(unified_signal)
    
    return response


# ==== 11.1 Endpoint ADVISOR CHAT ====

class ChatMessage(BaseModel):
    role: str
    content: str

class AdvisorChatReq(BaseModel):
    history: List[ChatMessage]
    context: Dict[str, Any]

@app.post("/analyze/advisor/chat")
def analyze_advisor_chat(req: AdvisorChatReq):
    """
    Endpoint para chat interactivo con el Advisor (DeepSeek).
    """
    from gemini_client import generate_chat
    
    # Convertir modelos Pydantic a dicts para la función
    messages = [{"role": m.role, "content": m.content} for m in req.history]
    
    # Añadir contexto técnico al último mensaje si es relevante
    # (Opcional: inyectarlo como system prompt adicional o en el último user msg)
    if req.context:
        ctx_str = (
            f"\n[Context: Token={req.context.get('token')}, "
            f"Direction={req.context.get('direction')}, "
            f"Entry={req.context.get('entry')}]"
        )
        # Añadir al final del último mensaje de usuario para que el modelo lo tenga fresco
        if messages and messages[-1]["role"] == "user":
            messages[-1]["content"] += ctx_str

    response_text = generate_chat(messages)
    
    return {
        "role": "assistant",
        "content": response_text,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }



# ==== 12. Endpoint Notify (Telegram) ====

class TelegramMsg(BaseModel):
    text: str

@app.post("/notify/telegram")
def notify_telegram(msg: TelegramMsg):
    """
    Envía una notificación a Telegram (simulado por ahora).
    """
    print(f"[TELEGRAM] Sending message: {msg.text}")
    return {"status": "ok", "sent": True}

# ==== 9. Stats & Metrics para Dashboard ====


def _parse_iso_ts(value: Optional[str]):
    """
    Intenta parsear timestamps en varios formatos.
    Devuelve datetime con tz UTC o None si no se puede.
    """
    if not value:
        return None

    v = value.strip()
    if not v:
        return None

    # ISO con Z
    try:
        if v.endswith("Z"):
            v = v.replace("Z", "+00:00")
        dt = datetime.fromisoformat(v)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        pass

    # Formatos alternativos
    for fmt in ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"):
        try:
            dt = datetime.strptime(v, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except Exception:
            continue

    return None


def compute_stats_summary() -> Dict[str, Any]:
    """
    Calcula métricas agregadas desde la base de datos.
    Fallback a CSV si la DB falla.
    """
    try:
        from typing import Dict, Any
        from sqlalchemy import func
        from models_db import Signal, SignalEvaluation
        from database import SessionLocal
        
        db = SessionLocal()
        try:
            day_ago = datetime.utcnow() - timedelta(hours=24)
            
            # Signals evaluated in last 24h
            eval_24h_count = db.query(func.count(SignalEvaluation.id)).filter(
                SignalEvaluation.evaluated_at >= day_ago
            ).scalar() or 0
            
            # Total evaluations
            total_eval = db.query(func.count(SignalEvaluation.id)).scalar() or 0
            
            # Win/Loss counts in last 24h
            tp_24h = db.query(func.count(SignalEvaluation.id)).filter(
                SignalEvaluation.evaluated_at >= day_ago,
                SignalEvaluation.result == 'WIN'
            ).scalar() or 0
            
            sl_24h = db.query(func.count(SignalEvaluation.id)).filter(
                SignalEvaluation.evaluated_at >= day_ago,
                SignalEvaluation.result == 'LOSS'
            ).scalar() or 0
            
            # LITE signals in last 24h
            lite_24h = db.query(func.count(Signal.id)).filter(
                Signal.timestamp >= day_ago,
                Signal.mode == 'LITE'
            ).scalar() or 0
            
            # Calculate win rate
            decided = tp_24h + sl_24h
            win_rate_24h = tp_24h / decided if decided > 0 else None
            
            # Open signals (LITE signals not yet evaluated)
            open_signals_est = max(lite_24h - eval_24h_count, 0)
            
            # [NEW] Calculate PnL (7d)
            week_ago = datetime.utcnow() - timedelta(days=7)
            pnl_7d_total = db.query(func.sum(SignalEvaluation.pnl_r)).filter(
                SignalEvaluation.evaluated_at >= week_ago
            ).scalar() or 0.0

            # [NEW] Active Agents Count (Requires StrategyConfig check)
            # Assuming marketplace_config.py loads into StrategyConfig or we just count enabled strategies via API
            # For now, we return 0 here and let frontend fetch /strategies to count enabled ones.
            # actually better to let frontend count active agents from /strategies endpoint.
            
            return {
                "win_rate_24h": win_rate_24h,
                "signals_evaluated_24h": eval_24h_count,
                "signals_total_evaluated": total_eval,
                "signals_lite_24h": lite_24h,
                "open_signals": open_signals_est,
                "pnl_7d": round(pnl_7d_total, 2)
            }
        finally:
            db.close()
            
    except Exception as e:
        print(f"Database query failed, falling back to CSV: {e}")
        # Fallback to CSV-based computation
        return compute_stats_summary_from_csv()


def compute_stats_summary_from_csv() -> Dict[str, Any]:
    """
    Fallback: Calcula métricas desde archivos CSV (legacy).
    """
    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(hours=24)

    # --- Evaluated: backend/logs/EVALUATED/{token}.evaluated.csv ---
    evaluated_dir = os.path.join(LOGS_DIR, "EVALUATED")
    total_eval = 0
    eval_24h = 0
    tp_24h = 0
    sl_24h = 0

    if os.path.isdir(evaluated_dir):
        for name in os.listdir(evaluated_dir):
            lower = name.lower()
            if not (lower.endswith(".csv") or lower.endswith(".evaluated.csv")):
                continue

            path = os.path.join(evaluated_dir, name)
            try:
                with open(path, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        total_eval += 1
                        ts = _parse_iso_ts(
                            row.get("evaluated_at") or row.get("signal_ts")
                        )
                        if ts and ts >= day_ago:
                            eval_24h += 1
                            result = (row.get("result") or "").strip()
                            if result == "hit-tp":
                                tp_24h += 1
                            elif result == "hit-sl":
                                sl_24h += 1
            except Exception:
                # No queremos que un CSV roto tumbe todo el endpoint
                continue

    # --- LITE: backend/logs/LITE/{token}.csv ---
    lite_dir = os.path.join(LOGS_DIR, "LITE")
    lite_24h = 0

    if os.path.isdir(lite_dir):
        for name in os.listdir(lite_dir):
            if not name.lower().endswith(".csv"):
                continue

            path = os.path.join(lite_dir, name)
            try:
                with open(path, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        ts = _parse_iso_ts(row.get("timestamp"))
                        if ts and ts >= day_ago:
                            lite_24h += 1
            except Exception:
                continue

    decided = tp_24h + sl_24h
    win_rate_24h = tp_24h / decided if decided > 0 else None

    # Señales LITE en las últimas 24h que aún no tienen evaluación
    open_signals_est = max(lite_24h - eval_24h, 0)

    return {
        "win_rate_24h": win_rate_24h,  # 0.0–1.0 o null
        "signals_evaluated_24h": eval_24h,
        "signals_total_evaluated": total_eval,
        "signals_lite_24h": lite_24h,
        "open_signals": open_signals_est,
    }


@app.get("/stats/summary")
def stats_summary():
    """
    Métricas agregadas simples para el dashboard de TraderCopilot.
    """
    try:
        return compute_stats_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==== 11. Fallback global ====

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Manejo genérico de errores inesperados."""
    if isinstance(exc, HTTPException):
        # Dejamos que FastAPI maneje HTTPException como siempre
        raise exc

    return {
        "error": str(exc),
        "message": "Unexpected server error."
    }










# ==== 13. Endpoint Strategy Management (Toggle) ====

@app.patch("/strategies/marketplace/{id}/toggle")
def toggle_strategy_active(id: str):
    """
    Toggles the is_active state of a strategy persona.
    Supports both Custom (user_strategies.json) and System (system_overrides.json) personas.
    """
    try:
        # Import config helpers locally to avoid circulars if any
        from marketplace_config import (
            load_user_strategies, save_user_strategies,
            load_system_overrides, save_system_overrides,
            SYSTEM_PERSONAS, refresh_personas
        )

        target_id = id
        
        # 1. Check if it's a User Strategy
        user_strategies = load_user_strategies()
        found_in_user = False
        
        for p in user_strategies:
            if p["id"] == target_id:
                # Toggle
                current = p.get("is_active", True)
                p["is_active"] = not current
                found_in_user = True
                save_user_strategies(user_strategies)
                break
        
        if found_in_user:
            refresh_personas()
            return {"status": "ok", "message": f"Strategy {target_id} toggled."}

        # 2. Check if it's a System Strategy
        is_system = any(p["id"] == target_id for p in SYSTEM_PERSONAS)
        
        if is_system:
            overrides = load_system_overrides()
            # If not in overrides, assume active (default for system is True)
            # Find default first to be sure
            default_state = True
            for sp in SYSTEM_PERSONAS:
                if sp["id"] == target_id:
                    default_state = sp.get("is_active", True)
                    break
            
            # Determine current state
            current_override = overrides.get(target_id, {}).get("is_active")
            current_state = current_override if current_override is not None else default_state
            
            # Toggle
            new_state = not current_state
            
            # Save override
            if target_id not in overrides:
                overrides[target_id] = {}
            overrides[target_id]["is_active"] = new_state
            
            save_system_overrides(overrides)
            refresh_personas()
            return {"status": "ok", "message": f"System Strategy {target_id} toggled to {new_state}."}

        raise HTTPException(status_code=404, detail="Strategy not found")
        
    except Exception as e:
        print(f"Error toggling strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==== 10. System Tools ====

@app.post("/system/reset")
async def factory_reset(request: Request):
    """
    FACTORY RESET PROTECCION CIVIL
    Borra TODAS las señales y datos de la base de datos.
    Se usa para demos limpias o reiniciar el entorno.
    """
    try:
        from database import AsyncSessionLocal
        from sqlalchemy import text
        
        async with AsyncSessionLocal() as session:
            # 1. Truncate Dependent Tables First (Foreign Key Constraints)
            await session.execute(text("DELETE FROM signal_evaluations"))
            
            # 2. Truncate Signals Table
            await session.execute(text("DELETE FROM signals"))
            
            await session.commit()
            
        print("[SYSTEM] ⚠️ FACTORY RESET EXECUTED. DB CLEARED.")
        return {"status": "ok", "message": "Database cleared successfully. System ready for new deployment."}
            
    except Exception as e:
        print(f"[SYSTEM] Reset Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
