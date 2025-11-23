# strategies/rsi_macd_volume.py
import pandas as pd
from dataclasses import dataclass

@dataclass
class RSIMACDVolumeStrategy:
    rsi_buy: int = 35
    rsi_sell: int = 65
    vol_mult: float = 1.2
    tp_atr_mult: float = 1.8
    sl_atr_mult: float = 1.0
    bars_timeout: int = 12
    name: str = "RSI_MACD_Volume"

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        d = df.copy()
        d["vol_ok"] = d["volume"] > (self.vol_mult * d["volume_ma20"].fillna(0))
        d["macd_cross_up"] = (d["macd"] > d["macd_signal"]) & (d["macd"].shift(1) <= d["macd_signal"].shift(1))
        d["macd_cross_down"] = (d["macd"] < d["macd_signal"]) & (d["macd"].shift(1) >= d["macd_signal"].shift(1))

        signals = []

        for ts, row in d.iterrows():
            atr = float(row.get("atr", 0.0))
            price = float(row["close"])

            # LONG: RSI bajo->subiendo + cruce MACD alcista + volumen
            if row["rsi"] <= self.rsi_buy and row["macd_cross_up"] and row["vol_ok"]:
                tp = price + self.tp_atr_mult * atr
                sl = price - self.sl_atr_mult * atr
                signals.append({
                    "entry_time": ts, "side": "LONG", "entry_price": price,
                    "tp_level": tp, "sl_level": sl, "bars_timeout": self.bars_timeout,
                    "confidence": 80.0
                })

            # SHORT: RSI alto->bajando + cruce MACD bajista + volumen
            if row["rsi"] >= self.rsi_sell and row["macd_cross_down"] and row["vol_ok"]:
                tp = price - self.tp_atr_mult * atr
                sl = price + self.sl_atr_mult * atr
                signals.append({
                    "entry_time": ts, "side": "SHORT", "entry_price": price,
                    "tp_level": tp, "sl_level": sl, "bars_timeout": self.bars_timeout,
                    "confidence": 80.0
                })

        return pd.DataFrame(signals)
