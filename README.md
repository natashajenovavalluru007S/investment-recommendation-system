# Investment Recommendation System

A finance analytics app that analyses 28 Nifty 50 stocks, scores their risk and return, and gives a Buy / Hold / Sell recommendation for each. Built as the capstone project for the SkillOrbit *Investment Banking with Finance* programme.

**Live dashboard:** https://investment-recommendation-system-bnw27gg3puetznkcc3st2u.streamlit.app

> For education only. Not financial advice.

## What it does

- Collects 5 years of daily price data for 28 Nifty 50 stocks across 8 sectors, plus the Nifty 50 index as a benchmark
- Cleans the data and calculates return, volatility, maximum drawdown, beta and Sharpe ratio
- Combines these into a 0-100 risk score and a Buy / Hold / Sell recommendation
- Shows everything in an interactive Streamlit dashboard with five pages:
  Overview, Stock Explorer, Compare Stocks, Portfolio Builder and Risk vs Return

## Screenshots

| Overview | Stock Explorer |
|---|---|
| ![Overview](screenshots/1_overview.png) | ![Stock Explorer](screenshots/2_stock_explorer.png) |

| Compare Stocks | Portfolio Builder |
|---|---|
| ![Compare](screenshots/3_compare.png) | ![Portfolio](screenshots/4_portfolio.png) |

![Risk vs Return](screenshots/5_risk_return.png)

## Data

- **Source:** Yahoo Finance, downloaded with the `yfinance` library (`collect_data.py`)
- **Period:** 18 Oct 2021 to 16 Oct 2026, 1,233 trading days shared by all series
- **Cleaning:** 57 placeholder rows (zero volume, flat price, on market holidays) were removed, and every series was aligned to the same trading dates
- Prices are adjusted for splits and dividends

## Method

**Risk score (0 = safest, 100 = riskiest).** Each measure is scaled across the 28 stocks, then combined:

| Measure | Weight |
|---|---|
| Volatility (annualised) | 40% |
| Maximum drawdown | 40% |
| Beta vs Nifty 50 | 20% |

Low: below 33. Medium: 33 to 66. High: above 66. The score is relative to this group of stocks, not an absolute measure.

**Total score and recommendation.**

| Component | Weight |
|---|---|
| Historical performance (Sharpe ratio) | 35% |
| Safety (100 minus risk score) | 25% |
| Current trend | 25% |
| 6-month momentum | 15% |

- **Trend:** Uptrend if price > 50-day average > 200-day average, Downtrend if the reverse, otherwise Sideways
- **Recommendation:** Buy if total score is 60 or more, Sell if below 35, otherwise Hold
- **Sharpe ratio** assumes a 7% annual risk-free rate (roughly an Indian government bond yield)

The weights and thresholds are judgement calls, chosen to be simple and easy to explain.

## Results (as of 16 Oct 2026)

7 Buy, 12 Hold, 9 Sell. Buy-rated: ICICI Bank, Bharti Airtel, Sun Pharma, Bajaj Auto, Kotak Bank, Cipla, Nestle India.

## Limitations

- **Survivorship bias:** the 28 stocks are today's Nifty 50 members, so companies that left the index are not included
- **In-sample results:** recommendations and the demo portfolio use the same history they are judged on, so they are a demonstration, not a forecast
- **Index comparison:** stock prices include dividends, while the Nifty 50 index line does not, which flatters the stocks slightly
- **Short window:** five years covers one market cycle, and results will change with a different period
- Fundamentals (earnings, valuation) are not used, only price history

## Project structure

```
├── app.py                  Streamlit dashboard
├── collect_data.py         Downloads raw data from Yahoo Finance
├── requirements.txt
├── data/
│   ├── raw/                One CSV per stock, plus the index
│   └── processed/          Cleaned prices, returns, metrics, recommendations
├── notebooks/
│   ├── 01_data_overview.ipynb
│   ├── 02_cleaning.ipynb
│   ├── 03_risk_return.ipynb
│   ├── 04_trends_portfolio.ipynb
│   └── 05_recommendations.ipynb
└── screenshots/
```

## Run it locally
https://investment-recommendation-system-bnw27gg3puetznkcc3st2u.streamlit.app/
```
pip install -r requirements.txt
streamlit run app.py
```

To refresh the data, run `python collect_data.py`, then re-run the notebooks in order.

## Tech stack

Python, pandas, NumPy, Plotly, Matplotlib, Streamlit, yfinance
