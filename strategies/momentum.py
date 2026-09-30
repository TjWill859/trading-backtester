import pandas as pd

def momentum_signal(close: pd.Series, lookback: int = 126) -> pd.Series:
    past_return = close.pct_change(lookback)
    signal = (past_return > 0).astype(int)
    return signal

class MomentumStrategy:
    """Streaming version: sees only history up to today."""

    def __init__(self, lookback=126):
        self.lookback = lookback

    def on_bar(self, history):
        # Need lookback+1 prices to compute a lookback-day return
        if len(history) <= self.lookback:
            return 0
        past_return = history.iloc[-1] / history.iloc[-1 - self.lookback] - 1
        return int(past_return > 0)