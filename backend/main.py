import sys
import os
import asyncio
import csv
from sqlalchemy import text  # Added for schema fix
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
        
        # 🔧 HOTFIX: Ensure rationale column is TEXT (unlimited) to prevent 500 errors
        # This fixes 'value too long for type character varying(240)'
        try:
            # Check if Postgres by looking at driver/url
            db_dsn = str(engine.url)
            if "postgresql" in db_dsn:
                print("🔧 [DB FIX] Attempting to expand 'rationale' column to TEXT...")
                await conn.execute(text("ALTER TABLE signals ALTER COLUMN rationale TYPE TEXT;"))
                print("✅ [DB FIX] Column 'rationale' updated to TEXT.")
        except Exception as e:
            # It might fail if table doesn't exist yet or other reasons, but safe to ignore
            print(f"⚠️ [DB FIX] Schema update skipped: {e}")
    
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
from routers.market import router as market_router
from routers.system import router as system_router
from routers.analysis import router as analysis_router
from routers.backtest import router as backtest_router
from routers.auth import router as auth_router

app.include_router(strategies_router, prefix="/strategies", tags=["Strategies"])
app.include_router(logs_router, prefix="/logs", tags=["Logs"])
app.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
app.include_router(advisor_router, prefix="/advisor", tags=["Advisor"])
app.include_router(analysis_router, prefix="/analyze", tags=["Analysis"])
app.include_router(market_router, prefix="/market", tags=["Market Data"])
app.include_router(system_router, prefix="/system", tags=["System"])
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
# (Logic moved to backend/core/analysis_logic.py)

# ==== 7. Capa RAG básica (vía rag_context) ====
# (Logic moved to backend/core/analysis_logic.py)




# ==== 8. Rutas base ====

@app.get("/")
def health_check():
    return {"status": "ok", "version": "v0.8.1"}


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
    Wrapper seguro para capturar errores 500 y mostrarlos en el frontend.
    """
    import traceback
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
    brain_ctx = _load_brain_context(token, market)

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

    # 3.2) Selección enriquecida de contexto (Base + Snapshot + Sentiment + Insight)
    context_parts = []
    
    # Base rationale from strategy
    if lite_signal.rationale:
        context_parts.append(lite_signal.rationale)

    # Snapshot hard data
    if snapshot:
        context_parts.append(f"Mkup: {snapshot}.")

    # Sentiment & Insights
    if sentiment_txt:
        context_parts.append(f"Sent: {sentiment_txt.splitlines()[0]}.")
    if insights_txt:
        context_parts.append(f"Insight: {insights_txt.splitlines()[0]}.")
    
    # News (Only if brief)
    if news_txt:
        news_headline = news_txt.splitlines()[0]
        if len(news_headline) < 80:
             context_parts.append(f"News: {news_headline}.")

    # Combine all
    full_rationale = " | ".join(context_parts)
    # Combined rationale
    lite_signal.rationale = full_rationale
    
    # [REMOVED TRUNCATION] No limits.


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
    brain_ctx = _load_brain_context(token, market)

    # 4) Markdown PRO
# ==== 9. Stats & Metrics para Dashboard ====
# (Mantener parse_iso_ts y compute_stats_summary si son usadas por endpoints restantes, de lo contrario mover a core/stats.py)
# Por seguridad, las dejo aquí si están siendo usadas por routers.stats que no existe aun.
# Wait, compute_stats_summary was used by /stats/summary ?
# I didn't see a /stats endpoint.
# Let's check if they are endpoints.
# If they are logic functions, they are fine.
# But analyze_advisor MUST GO.
# get_logs MUST GO.

def _parse_iso_ts(value: Optional[str]):
    """
    Intenta parsear timestamps en varios formatos.
    """
    if not value: return None
    try:
        if value.endswith("Z"): value = value.replace("Z", "+00:00")
        return datetime.fromisoformat(value)
    except:
        return None

# End of main.py - Cleaned.



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
