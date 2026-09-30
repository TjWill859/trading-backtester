# engine/event_driven.py
from dataclasses import dataclass
import pandas as pd
import math


@dataclass
class Order:
    date: pd.Timestamp
    ticker: str
    quantity: float


@dataclass
class Fill:
    date: pd.Timestamp
    ticker: str
    quantity: float
    price: float
    cost: float


class Portfolio:

    def __init__(self, initial_capital=100_000):
        self.cash = initial_capital
        self.positions = {}    # e.g. {"AAPL": 123.4} = shares held
        self.fills = []        # every trade ever made
        self.records = []      # one row per day, for the equity curve

    def equity(self, prices):
        holdings = sum(shares * prices[t] for t, shares in self.positions.items())
        return self.cash + holdings

    def make_order(self, date, ticker, target, price, fee_rate=0.0, fractional=True):
        """Position sizing: what must I trade to hold `target` (0 to 1) of my money in ticker?"""
        equity = self.equity({ticker: price})
        current = self.positions.get(ticker, 0.0)
        desired = target * equity / (price * (1 + fee_rate))
        if not fractional:
            desired = math.floor(desired)               # whole shares only

        change = desired - current
        if change > 0:                                  # buying: never spend more than we have
            affordable = self.cash / (price * (1 + fee_rate))
            if not fractional:
                affordable = math.floor(affordable)
            change = min(change, affordable)

        if abs(change) < 1e-9:
            return None
        return Order(date, ticker, change)

    def apply_fill(self, fill):
        """Update cash and shares after a trade."""
        self.cash -= fill.quantity * fill.price + fill.cost
        self.positions[fill.ticker] = self.positions.get(fill.ticker, 0.0) + fill.quantity
        self.fills.append(fill)

    def record(self, date, prices):
        self.records.append({"date": date, "equity": self.equity(prices), "cash": self.cash})


class Broker:

    def __init__(self, cost_bps=0.0):
        self.fee_rate = cost_bps / 10_000     # 5 bps -> 0.0005

    def execute(self, order, price):
        cost = abs(order.quantity) * price * self.fee_rate
        return Fill(order.date, order.ticker, order.quantity, price, cost)



class EventDrivenBacktester:
    """Walks through history one day at a time. The conveyor belt."""

    def __init__(self, close, ticker, strategy, initial_capital=100_000, cost_bps=0.0, fractional=True):
        self.close = close              # pd.Series of prices for ONE ticker
        self.ticker = ticker
        self.strategy = strategy        # use a FRESH strategy object per run
        self.initial_capital = initial_capital
        self.cost_bps = cost_bps
        self.fractional = fractional
        self.portfolio = None           # filled in by run(), so you can inspect fills after

    def run(self):
        self.portfolio = Portfolio(self.initial_capital)
        broker = Broker(self.cost_bps)
        target = 0                      # what we're currently holding (0 = cash, 1 = invested)
        carried = []                    # position we carried INTO each day

        for i, (date, price) in enumerate(self.close.items()):
            carried.append(target)      # 1. remember what we held coming into today

            history = self.close.iloc[:i + 1]          # 2. strategy sees the past only
            new_target = self.strategy.on_bar(history)

            if new_target != target:                   # 3. only trade when the decision CHANGES
                order = self.portfolio.make_order(date, self.ticker, new_target,
                                                  price, broker.fee_rate, self.fractional)
                if order is not None:
                    self.portfolio.apply_fill(broker.execute(order, price))
                target = new_target

            self.portfolio.record(date, {self.ticker: price})   # 4. end-of-day snapshot

        # Package results in the same shape as run_backtest, so metrics/plots just work
        df = pd.DataFrame(self.portfolio.records).set_index("date")
        result = pd.DataFrame({"position": pd.Series(carried, index=df.index),
                               "equity": df["equity"]})
        result["turnover"] = result["position"].diff().abs().fillna(0)
        result["strategy_return"] = result["equity"].pct_change().fillna(0)
        return result[["position", "turnover", "strategy_return", "equity"]]