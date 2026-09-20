import yfinance as yf
import pandas as pd
import os

TICKERS = ["AAPL", "MSFT", "JPM", "XOM", "SPY"]
START = "2018-01-01"
END = "2024-12-31"
DATA_DIR = "data/raw"

def fetch_and_save(tickers, start, end, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for ticker in tickers:
        print(f"Fetching {ticker}...")
        df = yf.download(ticker, start=start, end=end, auto_adjust=True)

        # yfinance sometimes returns multi-level columns (ticker + field) even
        # for a single ticker — flatten to just the field names (Open, Close, etc.)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.to_csv(f"{out_dir}/{ticker}.csv")
        print(f"  -> saved {len(df)} rows")

if __name__ == "__main__":
    fetch_and_save(TICKERS, START, END, DATA_DIR)