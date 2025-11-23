# models/arima_model.py

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import warnings

warnings.filterwarnings("ignore")

def add_arima_predictions(df: pd.DataFrame, order=(5, 1, 0)) -> pd.DataFrame:
    df = df.copy()

    if len(df) < 50:
        raise ValueError("Dataframe muy pequeño para ARIMA")

    df["arima_pred"] = None

    for i in range(50, len(df)):
        try:
            series = df["close"].iloc[:i]
            model = ARIMA(series, order=order)
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=1)
            df.at[df.index[i], "arima_pred"] = forecast.iloc[0]
        except Exception as e:
            print(f"[ARIMA] Error en la iteración {i}: {e}")
            continue

    return df
