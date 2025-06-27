# Chicago Quant Alley – Crypto Trading Simulator and Strategy Optimizer

## Overview

This project is based on building a basic framework to simulate crypto trading strategies using real-world market data. I used Delta Exchange’s public API to fetch live and historical crypto derivatives data, mainly for BTC options and futures. The goal was to get clean data, store it, and use it for analysis and simulation of trading ideas.

I wrote two main Python scripts for this. One is for picking a random week and collecting candles, the other is for downloading a full set of options and futures candle data across multiple strikes and expiries. I also studied theory from the book *Stochastic Finance with Python* (Ch. 1–5) to understand the background behind price modeling, randomness in markets, and simulation techniques.

---

## Practical Work

### Delta Exchange API Usage

I worked with Delta Exchange’s REST API which provides endpoints for market data. I used the following endpoints:
- `/v2/products`: Used to get metadata of all available contracts (futures and options).
- `/v2/history/candles`: Main endpoint to fetch OHLCV data. Limited to 500 candles per call.
- `/v2/options/chains`: Used to get the full list of options contracts for an underlying asset.

The API works without an API key for public data and supports timestamp-based filtering. I used this to break data into time slices and avoid hitting the 500-candle limit.

---

### `sample.py` – Random Week Data Fetcher

This script automates downloading data for a randomly selected week in the last 6 months for any given symbol.

Details:
- Picks a random start and end timestamp for a full week.
- Uses the 5-minute (`5m`) resolution.
- Calls the API to fetch OHLCV candle data for the given week.
- Handles retries if the API fails (up to 3 attempts).
- Converts the timestamps from UNIX to ISO datetime.
- Displays the range and the first few candles in pretty JSON format.
- Saves the output to a CSV file in the format: `BTCUSDT_5m_<start_time>.csv`.

Useful for creating random sample datasets for exploratory data analysis or testing simulations over different time periods.

---

### `Code.py` – Full Week BTC Options and Futures Scraper

This script is designed to collect data in bulk for a specific week (2025-01-18 to 2025-01-25) for:
- Multiple option strikes and expiries
- Both Call and Put types
- Futures symbols like `BTCUSDT` and `BTCUSD_PERP`

What it does:
- Loops over a list of expiry dates like `190125`, `200125`, etc.
- Loops over a range of strike prices from `105000` to `108000` with step size `200`.
- Forms symbols like `C-BTC-106000-220125` and `P-BTC-107000-230125`.
- Calls the Delta API using either the global or India API (both tested).
- Converts raw timestamps into datetime using `pandas`.
- Creates a separate CSV file for each option and each futures symbol, saved using the symbol as the filename.
- Also handles no-data cases and prints a message if data is empty.

This script basically builds a complete snapshot of the BTC derivatives market for one week and is meant to be used for research, modeling, or historical volatility studies.

---

### Data Cleaning and Storage

In both scripts:
- Time columns are converted from epoch seconds to readable datetime strings.
- Output files are saved in `.csv` format with consistent naming.
- Columns include: `time`, `open`, `high`, `low`, `close`, `volume`.
- Data is clean and ready for use in other analysis scripts or modeling notebooks.

---

## Theory from Book – Stochastic Finance with Python (Chapters 1–5)

**Chapter 1 – Introduction**  
Discusses randomness in markets and why stochastic modeling is required. Introduces simulation as a method to explore different outcomes and emphasizes Python's use for finance modeling.

**Chapter 2 – Finance Basics**  
Explains compounding interest, log vs simple returns, and basic instruments like stocks, options, and portfolios. Shows how to calculate returns and understand time value of money.

**Chapter 3 – Probability and Estimation**  
Covers random variables, expectations, standard deviation, and distributions like Normal, Exponential, and Poisson. Also includes parameter estimation methods like frequentist and Bayesian.

**Chapter 4 – Simulation**  
Details Monte Carlo simulation and how to simulate price paths. Talks about inverse transform and rejection sampling methods. Useful for modeling future asset behavior under uncertainty.

**Chapter 5 – Stochastic Processes**  
Introduces Brownian Motion and Random Walks. Defines drift, volatility, and quadratic variation. These are used later to model asset prices using stochastic differential equations (SDEs).

---

## Tools Used

- Python 3
- Libraries: `requests`, `pandas`, `csv`, `datetime`, `json`, `time`, `random`
- API: Delta Exchange REST API (`https://api.delta.exchange`, `https://api.india.delta.exchange`)
- Output: `.csv` files containing historical OHLCV candles for options and futures
- Editor: Visual Studio Code
