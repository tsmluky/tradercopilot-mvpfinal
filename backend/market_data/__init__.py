from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple

from .models import PriceSnapshot, OHLCVSlice, Timeframe
from .providers.ccxt_provider import fetch_price_snapshot, fetch_ohlcv_slice

# Cachés simples en memoria
_price_cache: Dict[str, Tuple[PriceSnapshot, datetime]] = {}
_ohlcv_cache: Dict[Tuple[str, str, Timeframe], Tuple[OHLCVSlice, datetime]] = {}

# TTL por defecto (puedes parametrizar desde .env más adelante si quieres)
PRICE_TTL = timedelta(seconds=30)
OHLCV_TTL = timedelta(seconds=60)


def get_price_snapshot(token: str) -> PriceSnapshot:
    """
    Devuelve un snapshot de precio actual para el token dado, con caché ligera.
    """
    now = datetime.now(timezone.utc)
    key = token.lower()

    if key in _price_cache:
        snap, ts = _price_cache[key]
        if now - ts < PRICE_TTL:
            return snap

    snap = fetch_price_snapshot(token)
    _price_cache[key] = (snap, now)
    return snap


def get_ohlcv(token: str, timeframe: Timeframe, limit: int = 200) -> OHLCVSlice:
    """
    Devuelve un slice de OHLCV (candlesticks) para el token y timeframe dados.
    """
    now = datetime.now(timezone.utc)
    key = (token.lower(), "default", timeframe)

    if key in _ohlcv_cache:
        slice_, ts = _ohlcv_cache[key]
        if now - ts < OHLCV_TTL:
            return slice_

    slice_ = fetch_ohlcv_slice(token, timeframe, limit=limit)
    _ohlcv_cache[key] = (slice_, now)
    return slice_


def snapshot(token: str) -> dict:
    """
    Función de compatibilidad para código antiguo:
    devuelve un diccionario simple con los datos de mercado.

    Esto es lo que está usando main.py:
        from .market_data import snapshot
        mkt = snapshot(req.token)
        pro.build_prompt(..., market=mkt, ...)
    """
    snap = get_price_snapshot(token)

    return {
        "token": snap.token,
        "symbol": snap.symbol,
        "exchange": snap.exchange,
        "price": snap.price,
        "change_24h": snap.change_24h,
        "volume_24h": snap.volume_24h,
        "ts": snap.ts.isoformat(),
    }
