import numpy as np
import pandas as pd


def mean_reversion_signal(close: pd.Series, window: int = 20,
                          threshold: float = 0.05) -> pd.Series:
    
    ma = close.rolling(window).mean()          

    entry = close < ma * (1 - threshold)       
    exit_ = close >= ma                        

    state = pd.Series(np.nan, index=close.index)
    state[entry] = 1                          
    state[exit_] = 0                          


    return state.ffill().fillna(0)             


class MeanReversionStrategy:

    def __init__(self, window=20, threshold=0.05):
        self.window = window
        self.threshold = threshold
        self.holding = 0          # the memory

    def on_bar(self, history):
        if len(history) < self.window:
            return self.holding   # not enough data for a moving average yet
        price = history.iloc[-1]
        ma = history.iloc[-self.window:].mean()

        if price < ma * (1 - self.threshold):
            self.holding = 1      # dropped far below average: buy
        elif price >= ma:
            self.holding = 0      # reverted to average: sell
        return self.holding       # in between: keep doing what we were doing