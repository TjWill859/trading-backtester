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