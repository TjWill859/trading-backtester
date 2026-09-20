import pandas as pd

def load_ticker(ticker, data_dir="data/raw"):
    df = pd.read_csv(f"{data_dir}/{ticker}.csv", index_col=0, parse_dates=True)
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df = df.dropna()
    return df

def load_universe(tickers, data_dir="data/raw"):
    return {ticker: load_ticker(ticker, data_dir) for ticker in tickers}