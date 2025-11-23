# strategies/ensemble_score.py

import pandas as pd

class EnsembleScoreStrategy:
    """
    Estrategia por score/confianza:
    - No genera trades históricos por sí sola (eso lo hace tu estrategia clásica).
    - Añade TP/SL dinámicos como referencia en función de ATR% y confianza.
    - Marca si hay señal (LONG/SHORT vs NO_TRADE).
    """
    def __init__(self, name: str = "EnsembleScore"):
        self.name = name

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        atr = out["atr_pct"].fillna(0.02)
        conf = out["confidence"].fillna(0.0)

        # SL/TP dinámicos en múltiplos de ATR, mapeo simple
        out["sl_atr_mult"] = ((100.0 - conf) / 100.0) * 1.8 + 1.2   # 1.2x..3.0x
        out["tp_atr_mult"] = (conf / 100.0) * 3.0 + 1.5             # 1.5x..4.5x

        out["entry_signal"] = (out["signal_side"] != "NO_TRADE").astype(int)
        out["strategy"] = self.name
        return out
