
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
    Obtiene datos OHLCV (Open, High, Low, Close, Volume) usando CCXT (Binance).
    
    Args:
        symbol: Par de trading (ej: 'BTC', 'ETH', 'SOL') -> Se convierte a 'BTC/USDT'
        timeframe: Intervalo ('1m', '5m', '15m', '30m', '1h', '4h', '1d')
        limit: Número de velas a obtener
    
    Returns:
        Lista de diccionarios con datos OHLCV
    """
    # 1. Normalización de Símbolo y Timeframe
    # CCXT usa formato 'BTC/USDT'
    base_symbol = symbol.upper().replace("USDT", "").replace("-", "")
    ccxt_symbol = f"{base_symbol}/USDT"
    
    # 2. Instanciar Exchange (Binance)
    exchange = ccxt.binance({'enableRateLimit': True})
    
    print(f"[MARKET DATA] Fetching {limit} candles for {ccxt_symbol} {timeframe} via CCXT...")

    try:
        # 3. Fetch Data with Pagination
        all_candles = []
        
        # Calculate 'since' (Start Time)
        # We need 'limit' candles ending NOW.
        m_factors = {'m': 1, 'h': 60, 'd': 1440}
        unit = timeframe[-1]
        val = int(timeframe[:-1])
        minutes = val * m_factors.get(unit, 1)
        duration_ms = minutes * 60 * 1000
        
        total_duration_ms = duration_ms * limit
        since = int(datetime.now().timestamp() * 1000) - total_duration_ms
        
        # Max limit per call for Binance is typically 1000
        BATCH_SIZE = 1000
        
        while len(all_candles) < limit:
            remaining = limit - len(all_candles)
            fetch_limit = min(remaining, BATCH_SIZE)
            
            try:
                data = exchange.fetch_ohlcv(ccxt_symbol, timeframe, since=since, limit=fetch_limit)
            except Exception as e:
                print(f"[MARKET DATA] Warning: Batch fetch failed: {e}")
                time.sleep(1)
                continue
            
            if not data:
                break
                
            all_candles.extend(data)
            
            # Update since for next batch
            last_ts = data[-1][0]
            since = last_ts + 1
            
            # Respect rate limits
            time.sleep(0.1) 
            
            if len(data) < fetch_limit:
                break
        
        # Trim to limit if we got too many
        if len(all_candles) > limit:
            all_candles = all_candles[-limit:]
                 
        # 4. Formatear
        ohlcv = []
        for candle in all_candles:
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
            
        print(f"[MARKET DATA] Success: {len(ohlcv)} candles loaded.")
        return ohlcv
        
    except Exception as e:
        print(f"[MARKET DATA] 🚨 CCXT Error fetching {ccxt_symbol}: {e}")
        print(f"[MARKET DATA] ⚠️ Attempting fallback to Mock Data (Random Walk)... Result quality will degrade.")
        return generate_mock_ohlcv(symbol, limit)

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
