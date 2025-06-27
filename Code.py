import requests
import pandas as pd
import time

# ------------------------
# CONFIGURATION
# ------------------------

# Date range
start_date = "2025-01-18 00:00:00"
end_date = "2025-01-25 00:00:00"

# Expiry dates for options (DDMMYY format)
expiries = ['190125', '200125', '210125', '220125', '230125']

# Strike range
strike_start = 105000
strike_end = 108000
strike_step = 200

# Option types
option_types = ['C', 'P']  # Call and Put

# Futures symbols
futures_symbols = ['BTCUSDT', 'BTCUSD_PERP']

# Candle resolution
resolution = '5m'

# TIMESTAMP CONVERSION

start_time = int(time.mktime(time.strptime(start_date, "%Y-%m-%d %H:%M:%S")))
end_time = int(time.mktime(time.strptime(end_date, "%Y-%m-%d %H:%M:%S")))

# CANDLE FETCH FUNCTION

def get_candle(symbol, use_india_api=False):
    base_url = 'https://api.india.delta.exchange/v2/history/candles' if use_india_api else 'https://api.delta.exchange/v2/history/candles'
    headers = {'Accept': 'application/json'}
    params = {
        'resolution': resolution,
        'symbol': symbol,
        'start': start_time,
        'end': end_time
    }
    r = requests.get(base_url, params=params, headers=headers)
    if r.status_code == 200:
        data = r.json().get('result', [])
        if not data:
            print(f"No data for {symbol}")
            return None
        df = pd.DataFrame(data)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
    else:
        print(f"Error {r.status_code} for {symbol}")
        return None

# ------------------------
# FETCH OPTIONS
# ------------------------

for expiry in expiries:
    for strike in range(strike_start, strike_end + 1, strike_step):
        for option_type in option_types:
            symbol = f'{option_type}-BTC-{strike}-{expiry}'
            print(f"Fetching {symbol}")
            df = get_candle(symbol, use_india_api=True)
            if df is not None:
                filename = f'{symbol}.csv'
                df.to_csv(filename, index=False)
                print(f"Saved {filename}")

# ------------------------
# FETCH FUTURES
# ------------------------

for symbol in futures_symbols:
    print(f"Fetching futures: {symbol}")
    df = get_candle(symbol, use_india_api=False)
    if df is not None:
        filename = f'{symbol}_{resolution}.csv'
        df.to_csv(filename, index=False)
        print(f"Saved {filename}")
