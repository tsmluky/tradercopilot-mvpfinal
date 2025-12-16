
# backend/market_data_api.py
"""
Módulo para obtener datos de mercado en tiempo real.
Refactorizado para usar CCXT (Binance) para consistencia con Trading Lab.
"""
import ccxt
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from core.cache import cache  # Importar Cache

def get_ohlcv_data(
    symbol: str,
    timeframe: str = "30m",
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Obtiene datos OHLCV con Caching + Fallback.
    TTL: 60s para reducir latencia.
    """
    # 1. Intentar Cache
    cache_key = f"ohlcv:{symbol.upper()}:{timeframe}:{limit}"
    cached_data = cache.get(cache_key)
    if cached_data:
        # print(f"[MARKET] ⚡ Cache Hit for {cache_key}")
        return cached_data

    # ... execution continues ...

    base_symbol = symbol.upper().replace("USDT", "").replace("-", "")
    ccxt_symbol = f"{base_symbol}/USDT"
    
    # 1. Fallback Order
    exchanges_config = [
        {'id': 'binance', 'class': ccxt.binance, 'timeout': 5000}, # 5s timeout
        {'id': 'kucoin', 'class': ccxt.kucoin, 'timeout': 5000},   # 5s timeout
        {'id': 'bybit', 'class': ccxt.bybit, 'timeout': 5000},     # 5s timeout
    ]

    for cfg in exchanges_config:
        ex_id = cfg['id']
        try:
            print(f"[MARKET DATA] Attempting fetch {ccxt_symbol} from {ex_id}...")
            exchange = cfg['class']({'enableRateLimit': True, 'timeout': cfg['timeout']})
            
            # Simple fetch without pagination loop to minimize hang risk
            # For 200-300 candles, a single call is usually enough.
            # Only use loop if limit > 1000 (which we reduced in main.py)
            
            data = exchange.fetch_ohlcv(ccxt_symbol, timeframe, limit=limit)
            
            if data and len(data) > 0:
                print(f"[MARKET DATA] Success: {len(data)} candles from {ex_id}.")
                
                # Format
                ohlcv = []
                for candle in data:
                    ts = candle[0]
                    dt = datetime.fromtimestamp(ts / 1000)
                    ohlcv.append({
                        'timestamp': ts,
                        'time': dt.strftime('%Y-%m-%d %H:%M'),
                        'open': float(candle[1]),
                        'high': float(candle[2]),
                        'low': float(candle[3]),
                        'close': float(candle[4]),
                        'volume': float(candle[5]),
                    })
                
                # Cache Valid Data: 20s TTL (Balance between load and freshness)
                cache.set(cache_key, ohlcv, ttl=20)
                return ohlcv
                return ohlcv
        except Exception as e:
            print(f"[MARKET DATA] ⚠️ Failed fetch from {ex_id}: {e}")
            continue # Try next exchange

    # 2. Last Resort: Mock Data
    print(f"[MARKET DATA] 🚨 All exchanges failed. Returning MOCK data to prevent crash.")
    mock_data = generate_mock_ohlcv(base_symbol, limit)
    return mock_data # Don't cache mock data, or cache briefly? No cache for mock.


# ... (generate_mock_ohlcv stays same) ...


def get_market_summary(symbols: List[str]) -> List[Dict[str, Any]]:
    """
    Obtiene precio y cambio 24h para múltiples símbolos.
    """
    # 1. Cache Check
    s_key = "-".join(sorted(symbols))
    cache_key = f"market:summary:{hash(s_key)}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        exchange = ccxt.binance()
        # Normalizar a BTC/USDT, ETH/USDT...
        pairs = [f"{s.upper().replace('USDT','')}/USDT" for s in symbols]
        
        # Intentar fetch_tickers (Batch)
        try:
            tickers = exchange.fetch_tickers(pairs)
        except:
            # Fallback slow loop
            tickers = {}
            for p in pairs:
                try:
                    tickers[p] = exchange.fetch_ticker(p)
                except:
                    pass

        summary = []
        for p in pairs:
            t = tickers.get(p)
            if t:
                # Calculate change if not provided
                change = t.get('percentage')
                if change is None and t.get('open'):
                    change = ((t['last'] - t['open']) / t['open']) * 100
                
                summary.append({
                    "symbol": p.replace("/USDT", ""),
                    "price": t['last'],
                    "change_24h": change or 0.0
                })
        
        # 2. Set Cache: 5s TTL for Summary (Price sensitivity)
        if summary:
            cache.set(cache_key, summary, ttl=5)
            
        return summary
    except Exception as e:
        print(f"[MARKET DATA] Error getting summary: {e}")
        return []

def get_current_price(symbol: str) -> Optional[float]:
    """
    Obtiene el precio actual de un símbolo.
    """
    try:
        data = get_ohlcv_data(symbol, limit=1)
        if data:
            return data[-1]['close']
    except:
        pass
    return None

