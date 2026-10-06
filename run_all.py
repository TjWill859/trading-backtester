import matplotlib
matplotlib.use("Agg")   # draw charts to files only; don't pop up windows

import pandas as pd

from data.load_data import load_universe
from engine.vectorized import run_backtest, trades_per_year
from engine.event_driven import EventDrivenBacktester
from engine.metrics import performance_summary, annualized_return
from engine.plots import plot_equity_curves, plot_drawdowns
from strategies.momentum import momentum_signal, MomentumStrategy
from strategies.mean_reversion import mean_reversion_signal, MeanReversionStrategy

CAPITAL = 100_000
COST_BPS = 5


class BuyAndHold:
    # Reference strategy for the event-driven engine: always invested.
    def on_bar(self, history):
        return 1


# data
close = load_universe(["AAPL"])["AAPL"]["Close"]
spy_close = load_universe(["SPY"])["SPY"]["Close"]
spy_equity = run_backtest(spy_close, pd.Series(1, index=spy_close.index),
                          CAPITAL, COST_BPS)["equity"]

always = pd.Series(1, index=close.index)   # "hold every day" signal

# name: (vectorized signal, function that builds a FRESH streaming strategy)
CASES = {
    "buy_hold_AAPL": (always,                                  lambda: BuyAndHold()),
    "mom_20":        (momentum_signal(close, 20),              lambda: MomentumStrategy(20)),
    "mom_126":       (momentum_signal(close, 126),             lambda: MomentumStrategy(126)),
    "mr_20_5%":      (mean_reversion_signal(close, 20, 0.05),  lambda: MeanReversionStrategy(20, 0.05)),
}

# 1. charts (vectorized engine)
full_results = {name: run_backtest(close, sig, CAPITAL, COST_BPS)
                for name, (sig, _) in CASES.items()}
equities = {name: res["equity"] for name, res in full_results.items()}

plot_equity_curves(equities, spy_equity,
                   title="AAPL strategies vs SPY (5bp costs)",
                   save_path="results/equity_curve.png")
plot_drawdowns({**equities, "SPY": spy_equity},
               save_path="results/drawdown.png")
print("saved results/equity_curve.png and results/drawdown.png")

# 2. vectorized vs event-driven
rows = {}
for name, (sig, make_strategy) in CASES.items():
    runs = {
        "vectorized":           full_results[name],
        "event (fractional)":   EventDrivenBacktester(close, "AAPL", make_strategy(),
                                                      CAPITAL, COST_BPS).run(),
        "event (whole shares)": EventDrivenBacktester(close, "AAPL", make_strategy(),
                                                      CAPITAL, COST_BPS,
                                                      fractional=False).run(),
    }
    for engine, res in runs.items():
        s = pd.Series(performance_summary(res, spy_equity))
        s["final_equity"] = res["equity"].iloc[-1]
        s["trades_per_year"] = trades_per_year(res)
        rows[(name, engine)] = s

pd.DataFrame(rows).T.to_csv("results/engine_comparison.csv")
print("saved results/engine_comparison.csv")


# 3. regime comparison
def slice_regime(result, start, end, initial_capital=CAPITAL):
    # Cut one window out of a full-period backtest and rebuild a fresh equity curve.
    first = result.index.searchsorted(pd.Timestamp(start))   # row of the window's first day
    r = result.iloc[first - 1:].loc[:end].copy()             # start ONE day early = "day 0"
    r.loc[r.index[0], ["strategy_return", "turnover"]] = 0.0 # day 0: no return, no trade
    r["equity"] = initial_capital * (1 + r["strategy_return"]).cumprod()
    return r


spy_ret = spy_close.pct_change()


def spy_equity_slice(start, end, initial_capital=CAPITAL):
    first = spy_ret.index.searchsorted(pd.Timestamp(start))
    r = spy_ret.iloc[first - 1:].loc[:end].copy()
    r.iloc[0] = 0.0
    return initial_capital * (1 + r).cumprod()


REGIMES = {
    "2022 bear":    ("2022-01-01", "2022-12-31"),
    "2023-24 bull": ("2023-01-01", "2024-12-31"),
}

rows = []
for regime, (start, end) in REGIMES.items():
    bench = spy_equity_slice(start, end)
    for name, res in full_results.items():
        sliced = slice_regime(res, start, end)
        s = pd.Series(performance_summary(sliced, bench))
        s["trades_per_year"] = trades_per_year(sliced)
        s["regime"], s["strategy"] = regime, name
        rows.append(s)
    # SPY itself as a reference row (key fixed: "annualized_return", not "ann_return")
    rows.append(pd.Series({"regime": regime, "strategy": "SPY buy&hold",
                           "annualized_return": annualized_return(bench)}))

regime_table = pd.DataFrame(rows).set_index(["regime", "strategy"])
regime_table.to_csv("results/regime_comparison.csv")
print("saved results/regime_comparison.csv")
