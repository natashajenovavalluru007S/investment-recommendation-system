"""
Module 1: Financial Data Collection
Downloads 5 years of daily OHLCV data for selected Nifty 50 stocks
plus the Nifty 50 index (benchmark) from Yahoo Finance.

Usage:
    pip install yfinance pandas
    python collect_data.py
"""
import os
import time
from datetime import date, timedelta

import pandas as pd
import yfinance as yf

OUT_DIR = "data/raw"
YEARS = 5

# sector -> tickers (NSE, .NS suffix)
STOCKS = {
    "IT": ["TCS", "INFY", "WIPRO", "HCLTECH"],
    "Banking": ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK"],
    "FMCG": ["HINDUNILVR", "ITC", "NESTLEIND"],
    "Pharma": ["SUNPHARMA", "DRREDDY", "CIPLA"],
    "Auto": ["MARUTI", "M&M", "BAJAJ-AUTO"],
    "Energy": ["RELIANCE", "ONGC", "NTPC", "POWERGRID"],
    "Metals": ["TATASTEEL", "HINDALCO"],
    "Infra/Others": ["LT", "ASIANPAINT", "ULTRACEMCO", "BHARTIARTL"],
}
BENCHMARK = "^NSEI"  # Nifty 50 index


def download_one(ticker: str, start: str, end: str, retries: int = 3):
    for attempt in range(1, retries + 1):
        try:
            df = yf.download(ticker, start=start, end=end, interval="1d",
                             auto_adjust=True, progress=False)
            if df is not None and not df.empty:
                # flatten MultiIndex columns if present
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df = df.reset_index()
                return df
        except Exception as e:
            print(f"  attempt {attempt} failed for {ticker}: {e}")
        time.sleep(2 * attempt)
    return None


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    end = date.today()
    start = end - timedelta(days=365 * YEARS)
    s, e = start.isoformat(), end.isoformat()

    meta_rows, failed = [], []

    jobs = [(BENCHMARK, "Index", "NIFTY50")]
    for sector, tickers in STOCKS.items():
        for t in tickers:
            jobs.append((f"{t}.NS", sector, t))

    for yf_ticker, sector, name in jobs:
        print(f"Downloading {yf_ticker} ...")
        df = download_one(yf_ticker, s, e)
        if df is None:
            failed.append(yf_ticker)
            continue
        safe = name.replace("&", "and").replace("-", "_")
        df.to_csv(f"{OUT_DIR}/{safe}.csv", index=False)
        meta_rows.append({
            "symbol": safe, "yf_ticker": yf_ticker, "sector": sector,
            "rows": len(df), "first_date": df["Date"].min(),
            "last_date": df["Date"].max(),
        })

    pd.DataFrame(meta_rows).to_csv(f"{OUT_DIR}/_metadata.csv", index=False)
    print(f"\nDone. {len(meta_rows)} downloaded, {len(failed)} failed.")
    if failed:
        print("Failed:", failed)


if __name__ == "__main__":
    main()
