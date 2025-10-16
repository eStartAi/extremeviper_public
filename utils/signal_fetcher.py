# utils/signal_fetcher.py

import logging
import time
from broker import get_broker
from utils.ta_engine import calc_rsi, calc_macd, calc_ema_slope, calc_vol_spike

logger = logging.getLogger(__name__)

def fetch_live_signal(pair: str, broker_name: str, count=100, timeframe="M5"):
    """
    Unified signal fetcher that routes by broker.
    Calls broker.fetch_candles(pair) and computes indicators.
    """
    try:
        broker = get_broker(broker_name)
        candles = broker.fetch_candles(pair, timeframe=timeframe, count=count)
        if not candles or len(candles) < 30:
            logger.warning(f"⚠️ Insufficient or missing candles for {pair}")
            return None

        closes = [c["close"] for c in candles]
        highs  = [c["high"] for c in candles]
        lows   = [c["low"] for c in candles]

        # === Core Indicator Calculations ===
        rsi = calc_rsi(closes)
        macd = calc_macd(closes)
        ema_slope = calc_ema_slope(closes)
        vol_spike = calc_vol_spike(highs, lows)  # ✅ FIXED: no comma → float

        trend = "sideways"
        if abs(ema_slope) > 0.002:
            trend = "strong"

        signal = {
            "pair": pair,
            "broker": broker_name,
            "rsi": rsi,
            "macd": macd,
            "ema_slope": ema_slope,
            "volume_spike": vol_spike,
            "trend": trend,
            "price": closes[-1],
            "side": "buy" if ema_slope > 0 else "sell",
            "stop_loss": closes[-1] * (1 - 0.04),
            "take_profit": closes[-1] * (1 + 0.25),
        }

        # === Safely format log output ===
        logger.info(
            f"✅ Retrieved {len(closes)} candles for {pair} via {broker_name.upper()} | "
            f"RSI={rsi:.2f}, "
            f"MACD={macd if isinstance(macd, float) else '??'}, "
            f"EMA_Slope={ema_slope:.5f}, "
            f"VolSpike={vol_spike:.2f}"
        )
        return signal

    except Exception as e:
        logger.error(f"❌ Signal fetch failed for {pair}: {e}")
        time.sleep(2)
        return None

