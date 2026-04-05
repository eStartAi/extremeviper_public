import os
import requests
import logging
from datetime import datetime, timedelta
from utils.pairmap import PAIRMAP_KRAKEN

logger = logging.getLogger(__name__)

KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY")
KRAKEN_API_SECRET = os.getenv("KRAKEN_API_SECRET")
KRAKEN_BASE_URL = os.getenv("KRAKEN_BASE_URL", "https://api.kraken.com")


def normalize_timeframe(tf):
    """Convert 'M5', 'H1', 'D1' style strings to integer minutes."""
    if isinstance(tf, int):
        return tf
    if isinstance(tf, str):
        tf = tf.upper().strip()
        if tf.startswith("M") and tf[1:].isdigit():
            return int(tf[1:])
        elif tf.startswith("H") and tf[1:].isdigit():
            return int(tf[1:]) * 60
        elif tf.startswith("D") and tf[1:].isdigit():
            return int(tf[1:]) * 1440
    raise ValueError(f"❌ normalize_timeframe() failed: unsupported format → {tf} ({type(tf)})")


def fetch_candles(pair, timeframe="M5", count=100):
    """Retrieve historical OHLC candles for a pair from Kraken."""
    try:
        kraken_pair = PAIRMAP_KRAKEN.get(pair)
        if not kraken_pair:
            logger.error(f"❌ Kraken pair mapping not found for {pair}")
            return None

        interval = normalize_timeframe(timeframe)
        total_minutes = int(interval) * int(count)
        since = int((datetime.utcnow() - timedelta(minutes=total_minutes)).timestamp())

        url = f"{KRAKEN_BASE_URL}/0/public/OHLC"
        params = {"pair": kraken_pair, "interval": interval, "since": since}

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if not data or data.get("error"):
            logger.error(f"❌ Kraken fetch error: {data.get('error')}")
            return None

        result = list(data.get("result", {}).values())[0]
        candles = [
            {
                "timestamp": int(float(c[0])),
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
                "volume": float(c[6]),
            }
            for c in result[-count:]
        ]

        logger.info(f"✅ Normalized {len(candles)} candles for {pair} via Kraken ({kraken_pair}, {timeframe})")
        return candles

    except Exception as e:
        logger.error(f"❌ Kraken fetch failed for {pair}: {e}")
        return None


def get_price(pair: str) -> float:
    """Fetch the latest mid-price for a given pair via Kraken public API."""
    try:
        kraken_pair = PAIRMAP_KRAKEN.get(pair, pair.replace("/", ""))
        url = f"{KRAKEN_BASE_URL}/0/public/Ticker?pair={kraken_pair}"
        resp = requests.get(url, timeout=5)
        data = resp.json()

        result = list(data.get("result", {}).values())
        if not result:
            raise ValueError(f"No price data returned for {pair}")

        ask = float(result[0]["a"][0])
        bid = float(result[0]["b"][0])
        price = (ask + bid) / 2
        logger.debug(f"✅ Kraken price fetched for {pair}: {price}")
        return price
    except Exception as e:
        logger.error(f"❌ Failed to fetch price for {pair}: {e}")
        return 0.0


def place_order(pair, side, price=None, sl=None, tp=None, size=None, lot_size=None):
    """
    Mocked market order placement (supports both 'size' and 'lot_size').
    """
    lot_size = lot_size or size or 0.01
    try:
        logger.info(f"✅ Kraken Order Placed: {side.upper()} {lot_size} lot {pair} (mocked)")
        return {
            "status": "filled",
            "pair": pair,
            "side": side,
            "price": price,
            "sl": sl,
            "tp": tp,
            "lot_size": lot_size,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"❌ Kraken order failed: {e}")
        return None


def ping():
    """Simple health check to confirm Kraken API responsiveness."""
    try:
        r = requests.get(f"{KRAKEN_BASE_URL}/0/public/Time", timeout=5)
        return r.status_code == 200
    except Exception as e:
        logger.warning(f"Kraken ping failed: {e}")
        return False


def get_balance():
    """Dummy balance for Kraken (for DRY_RUN mode)."""
    return 1000.00
