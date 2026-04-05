import os
import time
import requests
import logging

from oandapyV20 import API
from oandapyV20.endpoints.orders import OrderCreate
from utils.pairmap import PAIRMAP_OANDA

logger = logging.getLogger(__name__)

OANDA_API_KEY = os.getenv("OANDA_API_KEY")
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
OANDA_BASE_URL = os.getenv("OANDA_BASE_URL", "https://api-fxpractice.oanda.com/v3")

oanda_api = API(access_token=OANDA_API_KEY)

HEADERS = {
    "Authorization": f"Bearer {OANDA_API_KEY}",
    "Content-Type": "application/json"
}


def normalize_oanda_pair(pair):
    """Convert EUR/USD → EUR_USD using pairmap"""
    return PAIRMAP_OANDA.get(pair.upper(), pair.replace("/", "_"))


def fetch_candles(pair, timeframe="5m", count=100):
    """
    Fetch OHLC candle data from OANDA.
    Timeframes: S5, S10, M1, M5, M15, M30, H1, H4, D, W, M
    """
    symbol = normalize_oanda_pair(pair)
    granularity = timeframe.upper()
    if granularity.endswith("M"):
        granularity = "M" + granularity[:-1]

    url = f"{OANDA_BASE_URL}/instruments/{symbol}/candles"
    params = {
        "count": count,
        "granularity": granularity,
        "price": "M"  # Midpoint price
    }

    try:
        res = requests.get(url, headers=HEADERS, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()["candles"]
        candles = [
            {
                "timestamp": int(time.mktime(time.strptime(c["time"][:19], "%Y-%m-%dT%H:%M:%S"))),
                "open": float(c["mid"]["o"]),
                "high": float(c["mid"]["h"]),
                "low": float(c["mid"]["l"]),
                "close": float(c["mid"]["c"]),
                "volume": float(c["volume"]),
            }
            for c in data if c["complete"]
        ]
        logger.info(f"✅ Normalized {len(candles)} candles for {pair} via OANDA ({symbol}, {granularity})")
        return candles
    except Exception as e:
        logger.error(f"❌ OANDA candle fetch failed for {pair} → {e}")
        return []


def get_price(pair):
    """Get latest bid/ask price and return midpoint"""
    symbol = normalize_oanda_pair(pair)
    url = f"{OANDA_BASE_URL}/accounts/{OANDA_ACCOUNT_ID}/pricing"
    params = {"instruments": symbol}

    try:
        res = requests.get(url, headers=HEADERS, params=params, timeout=10)
        res.raise_for_status()
        prices = res.json()["prices"][0]
        bid = float(prices["bids"][0]["price"])
        ask = float(prices["asks"][0]["price"])
        mid = (bid + ask) / 2
        logger.debug(f"OANDA {symbol} → {mid}")
        return {"price": mid}
    except Exception as e:
        logger.error(f"❌ OANDA price fetch failed for {pair} → {e}")
        return None


def place_order(pair, side, price=None, sl=None, tp=None, size=None, lot_size=None):
    """
    Simulated OANDA order (for DRY_RUN). Accepts both 'size' and 'lot_size'.
    """
    lot_size = lot_size or size or 0.01
    try:
        logger.info(f"✅ OANDA Order Placed: {side.upper()} {lot_size} lot {pair} (mocked)")
        return {
            "status": "filled",
            "pair": pair,
            "side": side,
            "price": price,
            "sl": sl,
            "tp": tp,
            "lot": lot_size,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        }
    except Exception as e:
        logger.error(f"❌ OANDA order failed: {e}")
        return None


def check_connection():
    try:
        _ = fetch_candles("EUR/USD", count=1)
        return True
    except Exception as e:
        logger.warning(f"OANDA connection check failed: {e}")
        return False


# Exported for use in execute_trade()
__all__ = ["fetch_candles", "get_price", "place_order", "oanda_api", "OrderCreate"]


def ping():
    """
    Simple OANDA API heartbeat check.
    Returns True if the pricing endpoint responds.
    """
    try:
        url = f"{OANDA_BASE_URL}/accounts/{OANDA_ACCOUNT_ID}/instruments"
        res = requests.get(url, headers=HEADERS, timeout=5)
        return res.status_code == 200
    except Exception as e:
        logger.warning(f"⚠️ OANDA ping failed: {e}")
        return False


def get_balance():
    """
    Return simulated OANDA account balance (DRY_RUN mode).
    Replace with a real API call when live trading is enabled.
    """
    try:
        return float(os.getenv("DEFAULT_BALANCE", 1000.00))
    except Exception as e:
        logger.warning(f"⚠️ OANDA get_balance failed: {e}")
        return 1000.00
