# engine.py

import os
import sys
import time
from datetime import datetime
import pandas as pd

# ---- CONFIG RÁPIDA ---------------------------------------------------------
DATA_PATH = "data/ETHUSDT_60.csv"  # Ruta dataset
RESULTS_PATH = "results/summary.csv"
TRADES_PATH = "last_trades.csv"
SCORED_SIGNALS_PATH = "results/scored_signals.csv"

FAST_MODE = True
FAST_TAIL_N = 5000
USE_ARIMA = False
# ---------------------------------------------------------------------------

from utils.signal_logger import save_signal


def log(msg: str):
    ts = datetime.utcnow().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def ensure_dirs():
    for p in [RESULTS_PATH, TRADES_PATH, SCORED_SIGNALS_PATH]:
        d = os.path.dirname(p)
        if d:
            os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), "logs"), exist_ok=True)


def load_data(path: str) -> pd.DataFrame:
    log(f"Cargando dataset desde: {path}")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No existe el archivo: {path}")

    t0 = time.time()
    df = pd.read_csv(path)
    log(f"Leído CSV en {time.time() - t0:.2f}s (shape={df.shape})")

    df.columns = [c.lower() for c in df.columns]

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", errors="coerce")
        if df["timestamp"].isna().all():
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df.set_index("timestamp", inplace=True)
    elif "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df.set_index("date", inplace=True)
    else:
        raise ValueError("No se encontró columna de fecha ('timestamp' o 'date').")

    df = df.sort_index()
    if FAST_MODE:
        df = df.tail(FAST_TAIL_N).copy()
        log(f"FAST_MODE activo → usando tail({FAST_TAIL_N}) (shape={df.shape})")
    return df


def try_add_arima(df: pd.DataFrame) -> pd.DataFrame:
    try:
        from models.arima_model import add_arima_predictions
    except Exception as e:
        log(f"[ARIMA] No se pudo importar: {e}. Omitido.")
        return df

    try:
        t0 = time.time()
        df = add_arima_predictions(df)
        log(f"[ARIMA] Predicciones añadidas en {time.time() - t0:.2f}s.")
        return df
    except Exception as e:
        log(f"[ARIMA] Error al calcular: {e}. Omitido.")
        return df


def evaluate_strategy(df, strategy, symbol="ETHUSDT", timeframe="1h") -> dict:
    log(f"Evaluando estrategia: {strategy.name}")
    t0 = time.time()
    trades = strategy.generate_signals(df)
    dt = time.time() - t0
    log(f"{strategy.name} generó {len(trades)} trades en {dt:.2f}s")

    # DEBUG: mostrar trades obtenidos
    print("\n[DEBUG] Primeras filas de trades generados:")
    print(trades.head())

    # Guardar trades para visualización
    trades.to_csv(TRADES_PATH, index=False)
    log(f"Trades guardados en {TRADES_PATH}")

    # Guardar cada trade como señal en logs/
    if trades.empty:
        log("[⚠️] No se generaron trades → no hay nada que guardar en logs.")
    else:
        for idx, trade in trades.iterrows():
            print(f"\n[DEBUG] Guardando trade #{idx}:")
            print(trade.to_dict())

            # Validaciones extra antes de guardar
            required_cols = ["entry_time", "entry_price", "side", "tp_level", "sl_level", "bars_timeout", "confidence"]
            for col in required_cols:
                if col not in trade:
                    raise ValueError(f"Falta la columna '{col}' en trades → no se puede guardar señal.")

            # Aquí no hay try/except: queremos que reviente si falla
            save_signal(
                symbol=symbol,
                timeframe=timeframe,
                strategy=strategy.name,
                entry_time=pd.to_datetime(trade["entry_time"]),
                entry_price=float(trade["entry_price"]),
                side=str(trade.get("side", "LONG")),
                tp=float(trade.get("tp_level", 0)),
                sl=float(trade.get("sl_level", 0)),
                bars_timeout=int(trade.get("bars_timeout", 0)),
                confidence=float(trade.get("confidence", 0))
            )

    # Stats de resultados
    wins = trades[trades.get("result", "") == "win"]
    winrate = len(wins) / len(trades) * 100 if len(trades) > 0 else 0.0
    avg_return = trades["return_pct"].mean() if "return_pct" in trades.columns else 0.0
    max_dd = trades["return_pct"].min() if "return_pct" in trades.columns else 0.0

    return {
        "strategy": strategy.name,
        "trades": int(len(trades)),
        "winrate": round(winrate, 2),
        "avg_return_pct": round(float(avg_return), 2),
        "max_drawdown_pct": round(float(max_dd), 2),
        "date_tested": datetime.utcnow().isoformat()
    }


def save_results_row(row: dict, path: str):
    df = pd.DataFrame([row])
    if os.path.exists(path):
        df.to_csv(path, mode="a", header=False, index=False)
    else:
        df.to_csv(path, index=False)
    log(f"Resumen guardado en {path}")


def save_scored(df_scored: pd.DataFrame, path: str, last_n: int = 300):
    cols = [
        "close", "rsi", "macd", "macd_signal", "volume", "volume_ma20", "ema50", "ema200",
        "bb_percent", "atr_pct", "trend_regime", "score_long", "score_short", "confidence",
        "signal_side", "strategy", "sl_atr_mult", "tp_atr_mult"
    ]
    keep = [c for c in cols if c in df_scored.columns]
    df_scored.tail(last_n)[keep].to_csv(path, index=True)
    log(f"Scored (tail {last_n}) guardado en {path}")


def main():
    ensure_dirs()

    # 1) Cargar datos
    df = load_data(DATA_PATH)

    df.tail(5).to_csv("results/debug_loaded_tail.csv")
    log("Tail del dataset guardado en results/debug_loaded_tail.csv")

    # 2) Features
    from features import add_features
    log("Calculando features…")
    df = add_features(df)
    log(f"Features calculados (cols={len(df.columns)})")

    df.tail(5).to_csv("results/debug_features_tail.csv")
    log("Tail con features guardado en results/debug_features_tail.csv")

    # 3) ARIMA (opcional)
    if USE_ARIMA:
        df = try_add_arima(df)
    else:
        log("[ARIMA] Desactivado (USE_ARIMA=False).")

    # 4) Scoring + estrategia
    from models.scoring import Scorer
    from strategies.ensemble_score import EnsembleScoreStrategy

    log("Calculando score/confianza…")
    scorer = Scorer()
    df_scored = scorer.score(df)

    log("Aplicando EnsembleScoreStrategy…")
    es = EnsembleScoreStrategy()
    df_scored = es.apply(df_scored)

    save_scored(df_scored, SCORED_SIGNALS_PATH)

    # 5) Evaluación + guardado en logs
    from strategies.rsi_macd_volume import RSIMACDVolumeStrategy
    strategy = RSIMACDVolumeStrategy()
    results = evaluate_strategy(df, strategy, symbol="ETHUSDT", timeframe="1h")
    save_results_row(results, RESULTS_PATH)
    log(f"▶️ Estrategia evaluada: {results}")

    log("✅ Pipeline finalizado.")


if __name__ == "__main__":
    main()
