import pandas as pd

def momentum_signal(close: pd.Series, lookback: int = 126) -> pd.Series:
    past_return = close.pct_change(lookback)
    signal = (past_return > 0).astype(int)
    return signal