import os
import requests
from utils.pairmap import PAIRMAP_KRAKEN

KRAKEN_BASE_URL = os.getenv("KRAKEN_BASE_URL", "https://api.kraken.com")

def fetch_candles(pair: str, timeframe="5", count=100):
    # Kraken intervals: 1, 5, 15, 30, 60, etc.
    symbol = PAIRMAP_KRAKEN.get(pair, pair.replace("/", ""))
    url = f"{KRAKEN_BASE_URL}/0/public/OHLC"
    params = {
        "pair": symbol,
        "interval": int(timeframe.replace("M", "")),  # M5 → 5
        "since": 0
    }

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    result = r.json().get("result", {})
    candles_raw = list(result.values())[0]

    return [
        {
            "time": c[0],
            "open": float(c[1]),
            "high": float(c[2]),
            "low": float(c[3]),
            "close": float(c[4]),
        }
        for c in candles_raw[-count:]
    ]

