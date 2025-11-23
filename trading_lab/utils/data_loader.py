# utils/data_loader.py
import os
import pandas as pd

def load_dataset(symbol: str, timeframe: str, datasets_dir: str = "datasets") -> pd.DataFrame:
    """
    Carga un dataset CSV desde datasets/ en un DataFrame con índice datetime ascendente.
    Espera columnas: timestamp|date, open, high, low, close, volume
    """
    file_name = f"{symbol.upper().replace('/', '')}_{timeframe}.csv"
    path = os.path.join(datasets_dir, file_name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset no encontrado: {path}")
    df = pd.read_csv(path)
    df.columns = [c.lower() for c in df.columns]
    if "timestamp" in df.columns:
        try:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        except Exception:
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", errors="coerce")
        df.set_index("timestamp", inplace=True)
    elif "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df.set_index("date", inplace=True)
    else:
        raise ValueError("No se encontró columna de fecha.")
    df = df.sort_index()
    return df
