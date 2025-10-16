import os
import requests
from utils.pairmap import PAIRMAP_OANDA

OANDA_API_KEY = os.getenv("OANDA_API_KEY")
OANDA_BASE_URL = os.getenv("OANDA_BASE_URL", "https://api-fxpractice.oanda.com/v3")

def fetch_candles(pair: str, timeframe="M5", count=100):
    symbol = PAIRMAP_OANDA.get(pair, pair.replace("/", "_"))
    url = f"{OANDA_BASE_URL}/instruments/{symbol}/candles"
    headers = {
        "Authorization": f"Bearer {OANDA_API_KEY}"
    }
    params = {
        "granularity": timeframe,
        "count": count,
        "price": "M"
    }

    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    data = r.json().get("candles", [])

    return [
        {
            "time": c["time"],
            "open": float(c["mid"]["o"]),
            "high": float(c["mid"]["h"]),
            "low": float(c["mid"]["l"]),
            "close": float(c["mid"]["c"]),
        }
        for c in data if c.get("complete")
    ]
