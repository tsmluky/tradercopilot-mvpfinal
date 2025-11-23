# Trading Rules Module

This module contains the pure logic extracted from `trading_lab` for use in the `TraderCopilot` backend.

## Structure

- **`indicators.py`**: Stateless indicator functions (EMA, ATR, Bollinger, etc.).
- **`side_generators.py`**: Functions that take a DataFrame and return a Series of "LONG"/"SHORT" signals based on specific strategies (MA Cross, Donchian, BBMR).
- **`signal_builder.py`**: Logic to convert a raw "side" signal into a trade setup (Entry, TP, SL) using ATR-based rules.

## Usage in Backend

1. **Import**:
   ```python
   from trading_rules.indicators import ensure_features
   from trading_rules.side_generators import side_ma_cross
   from trading_rules.signal_builder import compute_entry_tp_sl
   ```

2. **Workflow**:
   - Fetch OHLCV data as a Pandas DataFrame.
   - Run `ensure_features(df)` to add ATR, EMA50, EMA200.
   - Call the appropriate side generator (e.g., `side_ma_cross`).
   - Call `compute_entry_tp_sl` with the result.
   - If `side != "NO_TRADE"`, generate a `Signal` object.
