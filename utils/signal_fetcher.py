# utils/signal_fetcher.py
# v0.0.14‑fix — unified fetcher with correct OANDA URL handling

import os
import time
import logging
import requests
from dotenv import load_dotenv

from broker import get_broker
from utils.ta_engine import calc_rsi, calc_macd, calc_ema_slope, calc_vol_spike

load_dotenv()
logger = logging.getLogger(__name__)

# === OANDA secrets ===
OANDA_API_KEY = os.getenv("OANDA_API_KEY")
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
OANDA_BASE_URL = os.getenv("OANDA_BASE_URL", "https://api-fxpractice.oanda.com")

# --- sanitize: strip any trailing /v3 or slash ---
OANDA_BASE_URL = OANDA_BASE_URL.rstrip("/")
if OANDA_BASE_URL.endswith("/v3"):
    OANDA_BASE_URL = OANDA_BASE_URL[:-3]
if OANDA_BASE_URL.endswith("/"):
    OANDA_BASE_URL = OANDA_BASE_URL[:-1]


def fetch_live_signal(pair: str, broker_name: str, count=100, timeframe="M5"):
    """
    Unified signal fetcher that routes by broker.
    Calls broker.fetch_candles(pair) and computes indicators.
    """
    try:
        broker = get_broker(broker_name)

        # === OANDA REST fetch ===
        if broker_name.lower() == "oanda":
            symbol = pair.replace("/", "_")
            url = f"{OANDA_BASE_URL}/v3/instruments/{symbol}/candles"
            headers = {
                "Authorization": f"Bearer {OANDA_API_KEY}",
                "Content-Type": "application/json"
            }
            params = {"granularity": timeframe, "count": count, "price": "M"}

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            candles = []
            for item in data.get("candles", []):
                if not item.get("complete"):
                    continue
                mid = item["mid"]
                candles.append({
                    "time": item["time"],
                    "open": float(mid["o"]),
                    "high": float(mid["h"]),
                    "low": float(mid["l"]),
                    "close": float(mid["c"]),
                })

        else:
            # === Kraken, Alpaca, etc. ===
            candles = broker.fetch_candles(pair, timeframe=timeframe, count=count)

        if not candles or len(candles) < 30:
            logger.warning(f"⚠️  Insufficient or missing candles for {pair}")
            return None

        closes = [c["close"] for c in candles]
        highs  = [c["high"]  for c in candles]
        lows   = [c["low"]   for c in candles]

        rsi        = calc_rsi(closes)
        macd       = calc_macd(closes)
        ema_slope  = calc_ema_slope(closes)
        vol_spike  = calc_vol_spike(highs, lows)
        trend      = "strong" if abs(ema_slope) > 0.002 else "sideways"
        price      = closes[-1]

        signal = {
            "pair": pair,
            "broker": broker_name,
            "rsi": rsi,
            "macd": macd,
            "ema_slope": ema_slope,
            "volume_spike": vol_spike,
            "trend": trend,
            "price": price,
            "side": "buy" if ema_slope > 0 else "sell",
            "stop_loss": price * (1 - 0.04),
            "take_profit": price * (1 + 0.25),
        }

        logger.info(
            f"✅ Retrieved {len(closes)} candles for {pair} via {broker_name.upper()} | "
            f"RSI={rsi:.2f}, MACD={macd:.5f}, EMA_Slope={ema_slope:.5f}, VolSpike={vol_spike:.2f}"
        )
        return signal

    except Exception as e:
        logger.error(f"❌ Signal fetch failed for {pair}: {e}")
        time.sleep(2)
        return None
