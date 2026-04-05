# ==============================================================
# brokers/alpaca.py
# v0.2.1 — Safe timeframe parsing + candle fetcher + order mocks
# ==============================================================

import os
import logging
import datetime
import requests
from utils.timeframe import TIMEFRAME, TIMEFRAME_MINUTES

logger = logging.getLogger(__name__)

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://data.alpaca.markets/v2/stocks")
ALPACA_TRADING_URL = os.getenv("ALPACA_TRADING_URL", "https://paper-api.alpaca.markets/v2")

HEADERS = {
    "APCA-API-KEY-ID": ALPACA_API_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY
}


def fetch_candles(symbol: str, timeframe: str = TIMEFRAME, count: int = 100):
    """
    Fetch recent candles from Alpaca API with safe timeframe handling.
    """
    try:
        end_time = datetime.datetime.utcnow()
        interval_minutes = TIMEFRAME_MINUTES
        start_time = end_time - datetime.timedelta(minutes=interval_minutes * count)

        url = f"{ALPACA_BASE_URL}/{symbol}/bars"
        params = {
            "start": start_time.isoformat() + "Z",
            "end": end_time.isoformat() + "Z",
            "timeframe": timeframe,  # e.g. '5Min'
            "limit": count
        }

        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        bars = data.get("bars", [])
        candles = [
            {
                "time": bar["t"],
                "open": float(bar["o"]),
                "high": float(bar["h"]),
                "low": float(bar["l"]),
                "close": float(bar["c"]),
                "volume": float(bar.get("v", 0.0)),
            }
            for bar in bars
        ]

        logger.info(f"✅ Retrieved {len(candles)} candles from ALPACA for {symbol}")
        return candles

    except Exception as e:
        logger.error(f"❌ Alpaca fetch failed for {symbol}: {e}")
        return None


def get_price(symbol: str) -> float:
    """
    Fetch the latest trade price for a symbol.
    """
    try:
        url = f"{ALPACA_BASE_URL}/{symbol}/quotes/latest"
        resp = requests.get(url, headers=HEADERS, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        ask = float(data.get("quote", {}).get("ap", 0))
        bid = float(data.get("quote", {}).get("bp", 0))
        price = (ask + bid) / 2 if ask and bid else 0.0
        logger.debug(f"✅ ALPACA {symbol} price: {price}")
        return price
    except Exception as e:
        logger.error(f"❌ Failed to fetch ALPACA price for {symbol}: {e}")
        return 0.0


def place_order(symbol, side, price=None, sl=None, tp=None, size=None, lot_size=None):
    """
    Mocked Alpaca order placement (supports both 'size' and 'lot_size').
    """
    lot_size = lot_size or size or 1
    try:
        logger.info(f"✅ ALPACA Order Placed: {side.upper()} {lot_size} shares {symbol} (mocked)")
        return {
            "status": "filled",
            "symbol": symbol,
            "side": side,
            "price": price,
            "sl": sl,
            "tp": tp,
            "lot_size": lot_size,
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"❌ ALPACA order failed: {e}")
        return None


def ping():
    """
    Basic health check for Alpaca data endpoint.
    """
    try:
        resp = requests.get(f"{ALPACA_BASE_URL}/AAPL/quotes/latest", headers=HEADERS, timeout=5)
        return resp.status_code == 200
    except Exception as e:
        logger.warning(f"Alpaca ping failed: {e}")
def get_balance():
    """Return simulated Alpaca account balance for DRY_RUN mode."""
    try:
        # Replace with real API call later
        return float(os.getenv("DEFAULT_BALANCE", 1000.00))
    except Exception as e:
        logger.warning(f"⚠️ Alpaca get_balance failed: {e}")
        return 1000.00

        return False
