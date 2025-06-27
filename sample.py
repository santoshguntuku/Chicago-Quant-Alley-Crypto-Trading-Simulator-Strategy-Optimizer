import requests
import time
import datetime
import random
import json
import csv

# Format timestamp to readable time -----
def format_time(ts):
    return datetime.datetime.fromtimestamp(ts / 1000 if ts > 1e12 else ts).isoformat()

#Fetch up to 500 candles from Delta API -----
def fetch_candles(symbol, resolution, start_time, end_time):
    url = "https://api.delta.exchange/v2/history/candles"
    params = {
        "symbol": symbol,
        "resolution": resolution,
        "start": start_time,
        "end": end_time,
        "limit": 500
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("result", [])
    else:
        print(f"API Error {response.status_code}: {response.text}")
        return []

#Retry Wrapper
def fetch_candles_with_retry(symbol, resolution, start_time, end_time, retries=3):
    for attempt in range(retries):
        candles = fetch_candles(symbol, resolution, start_time, end_time)
        if candles:
            return candles
        print(f"Retry {attempt+1}/{retries} in 3 seconds...")
        time.sleep(3)
    return []

#Select a random week in the last 6 months
def get_random_week_range():
    now = int(time.time())
    six_months_ago = now - 6 * 30 * 24 * 60 * 60
    random_start = random.randint(six_months_ago, now - 7 * 24 * 60 * 60)
    random_end = random_start + 7 * 24 * 60 * 60
    return random_start, random_end

#Save candles to CSV
def save_to_csv(candles, filename):
    with open(filename, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["time", "open", "high", "low", "close", "volume"])
        for c in candles:
            writer.writerow([
                format_time(c["time"]),
                c["open"],
                c["high"],
                c["low"],
                c["close"],
                c["volume"]
            ])
    print(f"Saved to {filename}")

# Main Program
def main():
    symbol = "BTCUSDT"       # Change to any symbol like "ETHUSDT", "SOLUSDT", etc.
    resolution = "5m"        # Choose from "1m", "5m", "15m", "1h", "4h", "1d"

    start_time, end_time = get_random_week_range()

    print("Random Week Range:")
    print("  Start:", format_time(start_time))
    print("  End  :", format_time(end_time))

    print(f"\n Fetching {resolution} candles for {symbol}")
    candles = fetch_candles_with_retry(symbol, resolution, start_time, end_time)

    if not candles:
        print("No data returned.")
        return

    print(f"\n Total candles fetched: {len(candles)}")

    # Print sample (first 5) candles
    print("\n Sample candles:")
    for c in candles[:5]:
        candle = {
            "time": format_time(c["time"]),
            "open": c["open"],
            "high": c["high"],
            "low": c["low"],
            "close": c["close"],
            "volume": c["volume"]
        }
        print(json.dumps(candle, indent=2))

    
    filename = f"{symbol}_{resolution}_{start_time}.csv"
    save_to_csv(candles, filename)

if __name__ == "__main__":
    main()
