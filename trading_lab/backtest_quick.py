import ccxt
import pandas as pd
import pandas_ta as ta
from datetime import datetime

# --- CONFIGURACIÓN GLOBAL ---
SYMBOL = 'ETH/USDT'
TIMEFRAME = '1h'      # Bajamos a 1H para buscar más frecuencia
LIMIT = 2000          # ~ 83 días de datos en 1H
EMA_PERIOD = 200
RISK_REWARD = 2.0

def fetch_data(symbol, timeframe, limit):
    print(f"📥 Descargando {limit} velas de {symbol} ({timeframe})...")
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def run_strategy(df, scenario_name, donchian_len, use_atr_filter):
    # Copia del DF para no ensuciar
    d = df.copy()
    
    # Indicadores
    donchian = ta.donchian(d['high'], d['low'], lower_length=donchian_len, upper_length=donchian_len)
    d['dc_upper'] = donchian[f'DCU_{donchian_len}_{donchian_len}'].shift(1)
    d['dc_lower'] = donchian[f'DCL_{donchian_len}_{donchian_len}'].shift(1)
    d['dc_mid']   = donchian[f'DCM_{donchian_len}_{donchian_len}'].shift(1)
    
    d['atr'] = ta.atr(d['high'], d['low'], d['close'], length=14)
    d['atr_ma'] = d['atr'].rolling(window=20).mean()
    d['ema_trend'] = ta.ema(d['close'], length=EMA_PERIOD)
    
    trades = []
    in_position = False
    pos = {}
    
    for i in range(EMA_PERIOD, len(d)):
        row = d.iloc[i]
        if pd.isna(row['dc_upper']) or pd.isna(row['ema_trend']): continue
        
        # --- SALIDA ---
        if in_position:
            res = None
            pnl = 0
            if pos['type'] == 'LONG':
                if row['low'] <= pos['sl']:
                    res = 'LOSS'; pnl = -1.0
                elif row['high'] >= pos['tp']:
                    res = 'WIN'; pnl = RISK_REWARD
            elif pos['type'] == 'SHORT':
                if row['high'] >= pos['sl']:
                    res = 'LOSS'; pnl = -1.0
                elif row['low'] <= pos['tp']:
                    res = 'WIN'; pnl = RISK_REWARD
            
            if res:
                trades.append({'res': res, 'pnl': pnl})
                in_position = False
            continue

        # --- ENTRADA ---
        # Filtros
        vol_ok = True
        if use_atr_filter:
            vol_ok = row['atr'] > row['atr_ma']
            
        # Logica
        if row['close'] > row['dc_upper'] and vol_ok and row['close'] > row['ema_trend']:
            sl = row['dc_mid']
            risk = row['close'] - sl
            if risk <= 0: continue
            in_position = True
            pos = {'type': 'LONG', 'sl': sl, 'tp': row['close'] + (risk * RISK_REWARD)}
            
        elif row['close'] < row['dc_lower'] and vol_ok and row['close'] < row['ema_trend']:
            sl = row['dc_mid']
            risk = sl - row['close']
            if risk <= 0: continue
            in_position = True
            pos = {'type': 'SHORT', 'sl': sl, 'tp': row['close'] - (risk * RISK_REWARD)}

    # --- METRICAS ---
    total = len(trades)
    if total == 0: return (scenario_name, 0, 0, 0)
    
    wins = len([t for t in trades if t['res'] == 'WIN'])
    win_rate = (wins / total) * 100
    net_r = sum(t['pnl'] for t in trades)
    
    return (scenario_name, total, win_rate, net_r)

def main():
    df = fetch_data(SYMBOL, TIMEFRAME, LIMIT)
    
    print(f"\n🔎 COMPARATIVA DE ESCENARIOS ({SYMBOL} 1H - Últimos ~80 días)")
    print(f"{'ESCENARIO':<25} | {'TRADES':<8} | {'WIN RATE':<10} | {'NETO (R)':<10}")
    print("-" * 65)
    
    scenarios = [
        ("Base (20, Filtros ON)", 20, True),
        ("Rápido (10, Filtros ON)", 10, True),
        ("Sin Filtro ATR (20, OFF)", 20, False),
        ("Rápido + Sin ATR (10, OFF)", 10, False)
    ]
    
    for name, period, atr_filter in scenarios:
        res = run_strategy(df, name, period, atr_filter)
        print(f"{res[0]:<25} | {res[1]:<8} | {res[2]:<9.1f}% | {res[3]:<9.2f} R")
    print("-" * 65)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
