# strategies/ma_cross.py
import pandas as pd
from dataclasses import dataclass

@dataclass
class MACrossStrategy:
    fast_period: int = 10
    slow_period: int = 50
    tp_atr_mult: float = 1.5
    sl_atr_mult: float = 1.0
    bars_timeout: int = 10
    name: str = "MA Cross"

    def __post_init__(self):
        self.name = f"MA_Cross_{self.fast_period}x{self.slow_period}_tp{self.tp_atr_mult}_sl{self.sl_atr_mult}"

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        d = df.copy()
        d["ema_fast"] = d["close"].ewm(span=self.fast_period, adjust=False).mean()
        d["ema_slow"] = d["close"].ewm(span=self.slow_period, adjust=False).mean()

        d["cross"] = 0
        d.loc[(d["ema_fast"] > d["ema_slow"]) & (d["ema_fast"].shift(1) <= d["ema_slow"].shift(1)), "cross"] = 1  # golden
        d.loc[(d["ema_fast"] < d["ema_slow"]) & (d["ema_fast"].shift(1) >= d["ema_slow"].shift(1)), "cross"] = -1  # death

        signals = []
        for ts, row in d.iterrows():
            if row["cross"] == 1:
                entry_price = float(row["close"])
                atr = float(row.get("atr", 0.0))
                tp = entry_price + self.tp_atr_mult * atr
                sl = entry_price - self.sl_atr_mult * atr
                signals.append({
                    "entry_time": ts,
                    "side": "LONG",
                    "entry_price": entry_price,
                    "tp_level": tp,
                    "sl_level": sl,
                    "bars_timeout": self.bars_timeout,
                    "confidence": 100.0 if row.get("trend_regime", 0) == 1 else 70.0
                })
            elif row["cross"] == -1:
                entry_price = float(row["close"])
                atr = float(row.get("atr", 0.0))
                tp = entry_price - self.tp_atr_mult * atr
                sl = entry_price + self.sl_atr_mult * atr
                signals.append({
                    "entry_time": ts,
                    "side": "SHORT",
                    "entry_price": entry_price,
                    "tp_level": tp,
                    "sl_level": sl,
                    "bars_timeout": self.bars_timeout,
                    "confidence": 100.0 if row.get("trend_regime", 0) == -1 else 70.0
                })

        return pd.DataFrame(signals)
