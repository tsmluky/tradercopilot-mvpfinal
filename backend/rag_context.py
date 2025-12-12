from __future__ import annotations

import random
from pathlib import Path
from typing import Dict, Optional

import requests

BASE_DIR = Path(__file__).resolve().parent
BRAIN_DIR = BASE_DIR / "brain"

COINGECKO_IDS: Dict[str, str] = {
    "ETH": "ethereum",
    "BTC": "bitcoin",
    "SOL": "solana",
}


def _load_snippet(token: str, name: str) -> str:
    """
    Carga un archivo de brain/{token}/{name}.* y devuelve
    UN snippet aleatorio separado por '---'.

    Si no existe o está vacío, devuelve cadena vacía.
    """
    token = token.lower()
    # insights = .md, el resto los hemos dejado como .txt
    if name == "insights":
        path = BRAIN_DIR / token / "insights.md"
    else:
        path = BRAIN_DIR / token / f"{name}.txt"

    if not path.exists():
        return ""

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return ""

    # Separar por '---' para tener variación
    parts = [p.strip() for p in text.split("\n---\n") if p.strip()]
    if not parts:
        return text

    return random.choice(parts)


def _get_realtime_snapshot(token: str) -> Optional[str]:
    """
    Obtiene un snapshot simple de precio y cambio 24h desde CoinGecko.
    No debe romper el flujo si falla: devuelve None en caso de error.
    """
    token_upper = token.upper()
    cg_id = COINGECKO_IDS.get(token_upper)
    if not cg_id:
        return None

    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": cg_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
            },
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
        info = data.get(cg_id)
        if not info:
            return None

        price = info.get("usd")
        change = info.get("usd_24h_change")

        if price is None or change is None:
            return None

        return f"{token_upper} = {price:.2f} USD · 24h: {change:+.2f}%"
    except Exception:
        # No queremos tirar la señal porque CoinGecko falle un día
        return None


def build_token_context(token: str) -> Dict[str, str]:
    """
    Devuelve un diccionario con contexto listo para inyectar en el
    prompt PRO/LITE. No impone formato final, solo agrupa piezas.
    """
    token_upper = token.upper()

    insights = _load_snippet(token_upper, "insights")
    news = _load_snippet(token_upper, "news")
    onchain = _load_snippet(token_upper, "onchain")
    sentiment = _load_snippet(token_upper, "sentiment")
    snapshot = _get_realtime_snapshot(token_upper)

    context_blocks = []

    if insights:
        context_blocks.append(f"## Insights sobre {token_upper}\n{insights}")

    if news:
        context_blocks.append(f"## Noticias y narrativa reciente ({token_upper})\n{news}")

    if onchain:
        context_blocks.append(f"## Contexto estructural / on-chain ({token_upper})\n{onchain}")

    if sentiment:
        context_blocks.append(f"## Sentimiento de mercado ({token_upper})\n{sentiment}")

    if snapshot:
        context_blocks.append(f"## Snapshot en tiempo real\n{snapshot}")

    full_context = "\n\n".join(context_blocks).strip()

    return {
        "token": token_upper,
        "raw_context": full_context,
        "snapshot": snapshot or "",
        "insights": insights,
        "news": news,
        "onchain": onchain,
        "sentiment": sentiment,
    }
