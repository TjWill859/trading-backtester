import pandas as pd

def run_backtest(close: pd.Series, signal: pd.Series, initial_capital: float = 100_000) -> pd.DataFrame:
    """
    Turns a signal into an equity curve.
    signal[t] is computed using data up to the close of day t.
    """
    daily_return = close.pct_change()          
    position = signal.shift(1) # trade tomorrow on today's signal
    strategy_return = position * daily_return  
    equity = initial_capital * (1 + strategy_return.fillna(0)).cumprod()

    return pd.DataFrame({
        "position": position,
        "strategy_return": strategy_return,
        "equity": equity,
    })