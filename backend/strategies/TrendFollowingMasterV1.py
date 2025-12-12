from jesse.strategies import Strategy, cached
import jesse.indicators as ta
from jesse import utils

class TrendFollowingMasterV1(Strategy):
    def hyperparameters(self):
        return [
            {'name': 'ema_fast', 'type': int, 'min': 10, 'max': 50, 'default': 20},
            {'name': 'ema_slow', 'type': int, 'min': 50, 'max': 200, 'default': 100},
            {'name': 'adx_period', 'type': int, 'min': 10, 'max': 30, 'default': 14},
            {'name': 'adx_threshold', 'type': int, 'min': 15, 'max': 40, 'default': 25},
            {'name': 'atr_period', 'type': int, 'min': 10, 'max': 30, 'default': 14},
            {'name': 'risk_pct', 'type': float, 'min': 0.5, 'max': 5.0, 'default': 2.0},
        ]

    @property
    @cached
    def ema_fast(self):
        return ta.ema(self.candles, self.hp['ema_fast'])

    @property
    @cached
    def ema_slow(self):
        return ta.ema(self.candles, self.hp['ema_slow'])

    @property
    @cached
    def adx(self):
        return ta.adx(self.candles, period=self.hp['adx_period'])

    @property
    @cached
    def atr(self):
        return ta.atr(self.candles, period=self.hp['atr_period'])

    def should_long(self) -> bool:
        return self.ema_fast > self.ema_slow and self.adx > self.hp['adx_threshold']

    def should_short(self) -> bool:
        return self.ema_fast < self.ema_slow and self.adx > self.hp['adx_threshold']

    def go_long(self):
        entry = self.price
        stop_loss = entry - (2 * self.atr)
        qty = utils.risk_to_size(self.capital, self.hp['risk_pct'], entry, stop_loss, fee_rate=self.fee_rate)
        self.buy = qty, entry

    def go_short(self):
        entry = self.price
        stop_loss = entry + (2 * self.atr)
        qty = utils.risk_to_size(self.capital, self.hp['risk_pct'], entry, stop_loss, fee_rate=self.fee_rate)
        self.sell = qty, entry

    def on_open_position(self, order):
        entry = order.price
        qty = order.qty
        atr = self.atr
        
        if self.is_long:
            self.stop_loss = qty, entry - (2 * atr)
            self.take_profit = qty, entry + (4 * atr)
        else:
            self.stop_loss = qty, entry + (2 * atr)
            self.take_profit = qty, entry - (4 * atr)

    def update_position(self):
        # Dynamic Trailing Stop: Tighten SL as price moves in favor
        atr = self.atr
        if self.is_long:
            new_sl = self.price - (2 * atr)
            # Only move SL up
            if new_sl > self.stop_loss[1]:
                self.stop_loss = self.position.qty, new_sl
        else:
            new_sl = self.price + (2 * atr)
            # Only move SL down
            if new_sl < self.stop_loss[1]:
                self.stop_loss = self.position.qty, new_sl

    def should_cancel_entry(self) -> bool:
        return True
