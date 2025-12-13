import ccxt
import pandas as pd
import pandas_ta as ta
import time

# --- CONFIGURACIÓN ---
TOKENS = ['BTC/USDT', 'ETH/USDT']
TIMEFRAMES = ['1h', '4h']
LIMIT = 1500 # Muestra representativa

def fetch_data(symbol, timeframe):
    try:
        print(f"📥 Bajando {symbol} {timeframe}...")
        exchange = ccxt.binance()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=LIMIT)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Error bajando {symbol}: {e}")
        return pd.DataFrame()

# --- ESTRATEGIA 1: DONCHIAN (TREND) ---
def strat_donchian(df):
    d = df.copy()
    # Indicadores
    donchian = ta.donchian(d['high'], d['low'], lower_length=20, upper_length=20)
    # Shift para evitar repainting
    upper = donchian['DCU_20_20'].shift(1)
    lower = donchian['DCL_20_20'].shift(1)
    mid   = donchian['DCM_20_20'].shift(1)
    ema   = ta.ema(d['close'], length=200)
    
    trades = []
    in_pos = False
    pos = {}
    
    for i in range(200, len(d)):
        row = d.iloc[i]
        if pd.isna(upper.iloc[i]): continue
        
        # Salida
        if in_pos:
            pnl = 0
            if pos['type'] == 'LONG':
                if row['low'] <= pos['sl']: pnl = -1.0 # Loss
                elif row['high'] >= pos['tp']: pnl = 2.0 # Win (2R)
            elif pos['type'] == 'SHORT':
                if row['high'] >= pos['sl']: pnl = -1.0
                elif row['low'] <= pos['tp']: pnl = 2.0
            
            if pnl != 0:
                trades.append(pnl)
                in_pos = False
            continue
            
        # Entrada Trend
        # Long: Rompe arriba + Precio sobre EMA200
        if row['close'] > upper.iloc[i] and row['close'] > ema.iloc[i]:
            sl = mid.iloc[i]
            risk = row['close'] - sl
            if risk > 0:
                in_pos = True
                pos = {'type': 'LONG', 'sl': sl, 'tp': row['close'] + (risk * 2)}
        
        # Short: Rompe abajo + Precio bajo EMA200
        elif row['close'] < lower.iloc[i] and row['close'] < ema.iloc[i]:
            sl = mid.iloc[i]
            risk = sl - row['close']
            if risk > 0:
                in_pos = True
                pos = {'type': 'SHORT', 'sl': sl, 'tp': row['close'] - (risk * 2)}
                
    return trades

# --- ESTRATEGIA 2: BOLLINGER (MEAN REVERSION) ---
def strat_bollinger(df):
    d = df.copy()
    # Bollinger Bands (20, 2.0)
    bb = ta.bbands(d['close'], length=20, std=2.0)
    if bb is None: return []
    
    # Shift para seguridad
    upper = bb['BBU_20_2.0'].shift(1)
    lower = bb['BBL_20_2.0'].shift(1)
    mid   = bb['BBM_20_2.0'].shift(1) # SMA 20
    
    trades = []
    in_pos = False
    pos = {}
    
    # RSI para filtro (comprar solo si sobrevendido)
    rsi = ta.rsi(d['close'], length=14).shift(1)

    for i in range(50, len(d)):
        row = d.iloc[i]
        if pd.isna(upper.iloc[i]): continue
        
        # Salida (Al tocar la media movil - Regresión a la media)
        if in_pos:
            pnl = 0
            # Salimos al tocar la media (SMA20) o Stop Loss fijo
            curr_mid = mid.iloc[i]
            
            if pos['type'] == 'LONG':
                if row['low'] <= pos['sl']: pnl = -1.0
                elif row['high'] >= curr_mid: pnl = 1.5 # Salida técnica estimada
            elif pos['type'] == 'SHORT':
                if row['high'] >= pos['sl']: pnl = -1.0
                elif row['low'] <= curr_mid: pnl = 1.5

            if pnl != 0:
                trades.append(pnl)
                in_pos = False
            continue

        # Entrada Reversión
        # Long: Precio cae bajo banda inferior + RSI bajo (Rebote)
        if row['close'] < lower.iloc[i] and rsi.iloc[i] < 35:
            dist = mid.iloc[i] - row['close']
            sl = row['close'] - (dist * 0.5) # SL debajo
            in_pos = True
            pos = {'type': 'LONG', 'sl': sl}

        # Short: Precio sube sobre banda superior + RSI alto (Rechazo)
        elif row['close'] > upper.iloc[i] and rsi.iloc[i] > 65:
            dist = row['close'] - mid.iloc[i]
            sl = row['close'] + (dist * 0.5)
            in_pos = True
            pos = {'type': 'SHORT', 'sl': sl}
            
    return trades

def run_tournament():
    print("\n🏆 INICIANDO TORNEO DE ESTRATEGIAS")
    print("="*60)
    print(f"{'ASSET':<10} | {'TF':<4} | {'STRATEGY':<15} | {'TRADES':<6} | {'WIN%':<6} | {'NET R':<6}")
    print("-" * 60)
    
    for token in TOKENS:
        for tf in TIMEFRAMES:
            df = fetch_data(token, tf)
            if df.empty: continue
            
            # Test Donchian
            res_d = strat_donchian(df)
            net_d = sum(res_d)
            wr_d = (len([x for x in res_d if x > 0]) / len(res_d) * 100) if res_d else 0
            
            print(f"{token:<10} | {tf:<4} | {'Donchian (Trend)':<15} | {len(res_d):<6} | {wr_d:<5.1f}% | {net_d:<6.1f}")
            
            # Test Bollinger
            res_b = strat_bollinger(df)
            net_b = sum(res_b)
            wr_b = (len([x for x in res_b if x > 0]) / len(res_b) * 100) if res_b else 0
            
            print(f"{token:<10} | {tf:<4} | {'Bollinger (Rev)':<15} | {len(res_b):<6} | {wr_b:<5.1f}% | {net_b:<6.1f}")
            print("-" * 60)

if __name__ == "__main__":
    run_tournament()
