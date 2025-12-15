
# backend/market_data_api.py
"""
Módulo para obtener datos de mercado en tiempo real.
Refactorizado para usar CCXT (Binance) para consistencia con Trading Lab.
"""
import ccxt
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

def get_ohlcv_data(
    symbol: str,
    timeframe: str = "30m",
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Obtiene datos OHLCV con Fallback Chain: Binance -> KuCoin -> Bybit -> Mock.
    Garantiza retorno de datos para evitar timeouts en frontend.
    """
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
                return ohlcv
        except Exception as e:
            print(f"[MARKET DATA] ⚠️ Failed fetch from {ex_id}: {e}")
            continue # Try next exchange

    # 2. Last Resort: Mock Data
    print(f"[MARKET DATA] 🚨 All exchanges failed. Returning MOCK data to prevent crash.")
    return generate_mock_ohlcv(base_symbol, limit)

def generate_mock_ohlcv(symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Genera datos OHLCV simulados para desarrollo/fallback.
    """
    import random
    
    print(f"[MARKET DATA] 🎲 Generating MOCK data for {symbol}...")
    
    base_prices = {
        'btc': 95000,
        'eth': 3600,
        'sol': 200,
    }
    
    base_price = base_prices.get(symbol.lower(), 1000)
    current_price = base_price
    
    ohlcv = []
    now = datetime.now()
    
    for i in range(limit):
        change_pct = random.uniform(-0.01, 0.01)
        open_price = current_price
        high_price = open_price * (1 + abs(change_pct) * random.uniform(0.5, 1.5))
        low_price = open_price * (1 - abs(change_pct) * random.uniform(0.5, 1.5))
        close_price = open_price * (1 + change_pct)
        
        current_price = close_price
        
        timestamp = now - timedelta(minutes=(limit - i) * 60)
        
        ohlcv.append({
            'timestamp': int(timestamp.timestamp() * 1000),
            'time': timestamp.strftime('%H:%M'),
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': random.randint(1000, 10000),
        })
    
    return ohlcv


def get_market_summary(symbols: List[str]) -> List[Dict[str, Any]]:
    """
    Obtiene precio y cambio 24h para múltiples símbolos.
    """
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

