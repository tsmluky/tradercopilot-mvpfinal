from typing import List
from datetime import datetime
from core.schemas import Signal
from strategies.base import Strategy, StrategyConfigInRuntime
from core.trading_rules.indicators import ensure_features
from core.trading_rules.side_generators import side_donchian
from core.trading_rules.signal_builder import compute_entry_tp_sl

class DonchianBreakoutStrategy(Strategy):
    """
    Estrategia Donchian Breakout.
    Portado de trading_lab: engine.py -> donchian_series
    """
    id = "DONCHIAN_BREAKOUT_V1"
    name = "Donchian Breakout"
    version = "1.0"
    default_timeframe = "4h"
    
    default_params = {
        "n": 20,
        "atr_pct_min": 0.005, # 0.5% volatilidad mínima
        "tp_atr": 1.8,
        "sl_atr": 1.0
    }

    def run(self, config: StrategyConfigInRuntime, market_data_service) -> List[Signal]:
        signals = []
        params = config.params or self.default_params
        
        for token in config.tokens:
            # Necesitamos al menos N velas + buffer para indicadores
            limit = params.get("n", 20) + 100
            
            df = market_data_service.get_ohlcv(
                token=token, 
                timeframe=self.default_timeframe, 
                limit=limit
            )
            
            if df.empty:
                continue

            df = ensure_features(df)

            side_series = side_donchian(
                df, 
                n=params.get("n", 20), 
                atr_pct_min=params.get("atr_pct_min", 0.005)
            )

            sig_dict = compute_entry_tp_sl(
                df, 
                side_series, 
                tp_atr=params.get("tp_atr", 1.8), 
                sl_atr=params.get("sl_atr", 1.0)
            )

            if sig_dict["side"] != "NO_TRADE":
                new_signal = Signal(
                    strategy_id=self.id,
                    token=token,
                    timeframe=self.default_timeframe,
                    direction=sig_dict["side"],
                    entry_price=sig_dict["entry_price"],
                    tp_price=sig_dict["tp_price"],
                    sl_price=sig_dict["sl_price"],
                    confidence=100.0,
                    rationale=f"Donchian Breakout ({params['n']} periods)",
                    source="quant_lab",
                    created_at=datetime.utcnow()
                )
                signals.append(new_signal)

        return signals
