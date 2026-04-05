import logging
from brokers import kraken, oanda
from utils.score_engine import score_signal
from utils.broker_selector import get_smart_broker  # ✅ correct import
from utils.pairmap import ENABLED_PAIRS
from brokers.kraken import normalize_timeframe  # ✅ Use this to safely convert

logger = logging.getLogger(__name__)


def fetch_signal(pair: str, broker: str, timeframe="M5", count=100):
    try:
        candles = None

        # ✅ Use broker-specific candle fetching logic
        if broker.lower() == "kraken":
            candles = kraken.fetch_candles(pair, timeframe, count)
        elif broker.lower() == "oanda":
            candles = oanda.fetch_candles(pair, timeframe, count)
        else:
            logger.warning(f"⚠️ Unsupported broker: {broker}")
            return None

        if not candles or len(candles) < count:
            logger.warning(f"⚠️ Insufficient or missing candles for {pair}")
            return None

        signal = _generate_signal_from_candles(candles)
        broker = get_smart_broker(pair)

        score = score_signal(signal)

        return {
            "pair": pair,
            "broker": broker,
            "signal": signal,
            "score": score
        }

    except Exception as e:
        logger.error(f"❌ Signal fetch failed for {pair}: {e}")
        return None


def _generate_signal_from_candles(candles):
    """
    Extract signal indicators from recent candle data.
    Assumes candles are sorted oldest → newest.
    """
    try:
        closes = [c["close"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        volumes = [c["volume"] for c in candles]

        # Most recent candle
        latest = candles[-1]
        previous = candles[-2]

        signal = {
            "price": latest["close"],
            "side": "buy" if latest["close"] > previous["close"] else "sell",
            "rsi": _calculate_rsi(closes),
            "macd": _calculate_macd(closes),
            "ema_slope": _calculate_ema_slope(closes),
            "vol_spike": _calculate_vol_spike(volumes),
            "sl": min(lows[-5:]),
            "tp": max(highs[-5:]),
        }

        return signal

    except Exception as e:
        logger.error(f"❌ Failed to generate signal from candles: {e}")
        return {}


# === Stub indicator logic ===
def _calculate_rsi(closes): return 50
def _calculate_macd(closes): return 0
def _calculate_ema_slope(closes): return 0
def _calculate_vol_spike(volumes): return 1
