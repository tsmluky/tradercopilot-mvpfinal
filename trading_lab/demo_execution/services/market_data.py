import pandas as pd
import os

class MockMarketDataService:
    def __init__(self, datasets_dir="datasets"):
        self.datasets_dir = datasets_dir

    def get_ohlcv(self, token: str, timeframe: str, limit: int = 500) -> pd.DataFrame:
        # Mapear token "ETH" -> "ETHUSDT" si es necesario
        symbol = token if "USDT" in token else f"{token}USDT"
        filename = f"{symbol}_{timeframe}.csv"
        path = os.path.join(self.datasets_dir, filename)
        
        if not os.path.exists(path):
            print(f"[MockData] ⚠️ No encontrado: {path}")
            return pd.DataFrame()
        
        df = pd.read_csv(path)
        
        # Normalizar columnas
        df.columns = [c.lower() for c in df.columns]
        
        # Parsear fecha (asumiendo timestamp o date)
        time_col = None
        for c in ["timestamp", "date", "time", "datetime"]:
            if c in df.columns:
                time_col = c
                break
        
        if time_col:
            df[time_col] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
            df = df.sort_values(time_col).set_index(time_col)
        
        # Devolver las últimas 'limit' velas
        return df.tail(limit).copy()
