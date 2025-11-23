# models/trend_slope.py

import numpy as np
import pandas as pd

def _rolling_slope(series: pd.Series, window: int) -> pd.Series:
    """
    Pendiente de regresión lineal (OLS) sobre log(precio) en ventana fija.
    Normalizada por la media del eje X para estabilidad.
    """
    y = np.log(series.replace(0, np.nan))
    x = np.arange(len(series), dtype=float)

    # coeficiente 'slope' con polyfit en ventana móvil
    def slope_fn(i):
        j = i - window + 1
        if j < 0:
            return np.nan
        yy = y.iloc[j:i+1]
        xx = x[j:i+1]
        if yy.isna().any():
            return np.nan
        # polinomio grado 1 (a*x + b): a = slope
        a, b = np.polyfit(xx, yy, 1)
        return a

    return pd.Series([slope_fn(i) for i in range(len(series))], index=series.index)

def add_trend_regime(df: pd.DataFrame, windows=(14, 28)) -> pd.DataFrame:
    out = df.copy()
    w1, w2 = windows
    out[f"slope_{w1}"] = _rolling_slope(out["close"], w1)
    out[f"slope_{w2}"] = _rolling_slope(out["close"], w2)

    # Clasificación de régimen
    up = (out[f"slope_{w1}"] > 0) & (out[f"slope_{w2}"] > 0)
    dn = (out[f"slope_{w1}"] < 0) & (out[f"slope_{w2}"] < 0)

    out["trend_regime"] = "RANGE"
    out.loc[up, "trend_regime"] = "UP"
    out.loc[dn, "trend_regime"] = "DOWN"
    return out
