# backend/market_data_api.py
"""
Módulo para obtener datos de mercado en tiempo real desde APIs públicas.
"""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


def get_ohlcv_data(
    symbol: str,
    timeframe: str = "30m",
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Obtiene datos OHLCV (Open, High, Low, Close, Volume) desde Binance API pública.
    
    Args:
        symbol: Par de trading (ej: 'BTCUSDT', 'ETHUSDT', 'SOLUSDT')
        timeframe: Intervalo de tiempo ('1m', '5m', '15m', '30m', '1h', '4h', '1d')
        limit: Número de velas a obtener (máx 1000)
    
    Returns:
        Lista de diccionarios con datos OHLCV
    """
    # Mapeo de símbolos
    symbol_map = {
        'btc': 'BTCUSDT',
        'eth': 'ETHUSDT',
        'sol': 'SOLUSDT',
    }
    
    binance_symbol = symbol_map.get(symbol.lower(), f"{symbol.upper()}USDT")
    
    # Mapeo de timeframes
    interval_map = {
        '1m': '1m',
        '5m': '5m',
        '15m': '15m',
        '30m': '30m',
        '1h': '1h',
        '4h': '4h',
        '1d': '1d',
    }
    
    interval = interval_map.get(timeframe, '30m')
    
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {
            'symbol': binance_symbol,
            'interval': interval,
            'limit': min(limit, 1000)
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Formatear datos
        ohlcv = []
        for candle in data:
            ohlcv.append({
                'timestamp': candle[0],  # Open time
                'time': datetime.fromtimestamp(candle[0] / 1000).strftime('%H:%M'),
                'open': float(candle[1]),
                'high': float(candle[2]),
                'low': float(candle[3]),
                'close': float(candle[4]),
                'volume': float(candle[5]),
            })
        
        return ohlcv
        
    except Exception as e:
        print(f"Error fetching OHLCV data: {e}")
        # Fallback a datos mock si falla la API
        return generate_mock_ohlcv(symbol, limit)


def generate_mock_ohlcv(symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Genera datos OHLCV simulados para desarrollo/fallback.
    """
    import random
    
    # Precio base según símbolo
    base_prices = {
        'btc': 65000,
        'eth': 3600,
        'sol': 200,
    }
    
    base_price = base_prices.get(symbol.lower(), 1000)
    current_price = base_price
    
    ohlcv = []
    now = datetime.now()
    
    for i in range(limit):
        # Generar variación aleatoria
        change_pct = random.uniform(-0.01, 0.01)  # ±1%
        open_price = current_price
        high_price = open_price * (1 + abs(change_pct) * random.uniform(0.5, 1.5))
        low_price = open_price * (1 - abs(change_pct) * random.uniform(0.5, 1.5))
        close_price = open_price * (1 + change_pct)
        
        current_price = close_price
        
        timestamp = now - timedelta(minutes=(limit - i) * 30)
        
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
            return data[0]['close']
    except:
        pass
    return None
