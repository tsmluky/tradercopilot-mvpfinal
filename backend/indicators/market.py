import ccxt
import pandas as pd
import pandas_ta as ta

# Configuración básica
EXCHANGE_ID = 'binance' 

def get_market_data(symbol: str, timeframe: str = "1h", limit: int = 100):
    """
    Descarga OHLCV y calcula indicadores técnicos base.
    Retorna: (dataframe, dict_resumen_actual)
    """
    # Normalizar símbolo (ej: 'eth' -> 'ETH/USDT')
    pair = f"{symbol.upper()}/USDT"
    
    try:
        exchange = getattr(ccxt, EXCHANGE_ID)()
        
        # Descarga de datos
        ohlcv = exchange.fetch_ohlcv(pair, timeframe, limit=limit)
        if not ohlcv:
            return None, None
            
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Cálculo de Indicadores (Quant Layer)
        df.ta.ema(length=21, append=True)
        df.ta.ema(length=50, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.macd(append=True) 
        df.ta.atr(length=14, append=True)
        
        # Limpieza
        df.dropna(inplace=True)
        
        # Extraer última vela
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Mapeo de datos
        data = {
            "price": last['close'],
            "rsi": round(last['RSI_14'], 2),
            "ema21": last['EMA_21'],
            "ema50": last['EMA_50'],
            "macd": last['MACD_12_26_9'],
            "macd_hist": last['MACDh_12_26_9'],
            "atr": last['ATRr_14'],
            "volume_change_pct": round(((last['volume'] - prev['volume']) / prev['volume']) * 100, 2),
            "trend": "BULLISH" if last['close'] > last['EMA_50'] else "BEARISH"
        }
        
        return df, data

    except Exception as e:
        print(f"[ERROR MARKET] {e}")
        return None, None
