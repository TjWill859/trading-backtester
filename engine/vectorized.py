import pandas as pd


def run_backtest(close, signal, initial_capital=100_000, cost_bps=0.0):
    
    daily_return = close.pct_change().fillna(0)

    position = signal.shift(1).fillna(0)

    turnover = position.diff().abs().fillna(0)

    cost = turnover * cost_bps / 10_000

    strategy_return = position * daily_return - cost
    equity = initial_capital * (1 + strategy_return).cumprod()

    return pd.DataFrame({
        "position": position,
        "turnover": turnover,
        "strategy_return": strategy_return,
        "equity": equity,
    })


def trades_per_year(result):
    years = len(result) / 252
    return result["turnover"].sum() / years