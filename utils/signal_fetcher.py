import requests
import logging
import os
import time
from utils.ta_engine import calc_rsi, calc_macd, calc_ema_slope, calc_vol_spike

logger = logging.getLogger(__name__)

# =====================================================
# === OANDA CONNECTION SETUP ===
# =====================================================
OANDA_BASE_URL = os.getenv("OANDA_BASE_URL", "https://api-fxpractice.oanda.com/v3")
OANDA_API_KEY = os.getenv("OANDA_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {OANDA_API_KEY}",
    "Content-Type": "application/json"
}

# =====================================================
# === FETCH LIVE SIGNAL ===
# =====================================================
def fetch_live_signal(pair: str, timeframe="M5", count=100):
    """
    Fetch live candle data from OANDA and compute RSI, MACD, EMA slope,
    and a synthetic volatility-spike factor.
    Returns a signal dictionary ready for scoring.
    """
    granularity = timeframe  # compatibility alias

    try:
        # ✅ OANDA format uses underscores instead of slashes
        formatted_pair = pair.replace("/", "_")

        url = f"{OANDA_BASE_URL}/instruments/{formatted_pair}/candles"
        params = {"count": count, "granularity": granularity, "price": "M"}

        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        candles = data.get("candles", [])
        if not candles:
            logger.warning(f"⚠️ No candles returned for {pair}")
            return None

        closes = [float(c["mid"]["c"]) for c in candles if "mid" in c]
        highs  = [float(c["mid"]["h"]) for c in candles if "mid" in c]
        lows   = [float(c["mid"]["l"]) for c in candles if "mid" in c]

        if len(closes) < 30:
            logger.warning(f"⚠️ Not enough candle data for {pair}")
            return None

        # =====================================================
        # === TRUE INDICATOR CALCULATIONS ===
        # =====================================================
        rsi = calc_rsi(closes)
        macd = calc_macd(closes)
        ema_slope = calc_ema_slope(closes)
        volume_spike = calc_vol_spike(highs, lows)  # volatility-based boost

        # =====================================================
        # === TREND DETECTION & SIGNAL PACK ===
        # =====================================================
        trend = "sideways"
        if abs(ema_slope) > 0.002:  # ~0.2% slope threshold
            trend = "strong"

        signal = {
            "pair": pair,
            "rsi": rsi,
            "macd": macd,
            "ema_slope": ema_slope,
            "volume_spike": volume_spike,
            "trend": trend,
            "price": closes[-1],
        }

        logger.info(
            f"✅ Retrieved {len(closes)} candles for {formatted_pair} "
            f"| RSI={rsi:.2f}, MACD={macd:.5f}, EMA_Slope={ema_slope:.5f}, "
            f"VolSpike={volume_spike:.2f}"
        )
        return signal

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Signal fetch failed for {pair}: {e}")
        time.sleep(3)
        return None
