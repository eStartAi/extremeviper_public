# =====================================================
# utils/broker_selector.py
# v1.3 — Smart rotation + latency-aware broker routing
# =====================================================
import os
import time
import logging
import requests
from statistics import mean
from utils.trade_control_logger import get_last_success_time

logger = logging.getLogger(__name__)

# Memory stores
_broker_health = {}
_last_failure = {}
FAILURE_TIMEOUT = 180  # seconds before retry
BROKER_ROTATION_ORDER = ["kraken", "oanda", "alpaca", "tos"]

# Optional broker ping endpoints (lightweight public URLs)
BROKER_PING_URLS = {
    "kraken": "https://api.kraken.com/0/public/Time",
    "oanda": "https://api-fxpractice.oanda.com/v3/accounts",
    "alpaca": "https://data.alpaca.markets/v2/stocks/AAPL/bars?limit=1",
    "tos": "https://api.schwabapi.com/v1/marketdata/quotes?symbols=AAPL"
}


def _is_broker_healthy(broker: str) -> bool:
    """Return True if broker not in failure cooldown."""
    last_fail = _last_failure.get(broker, 0)
    return (time.time() - last_fail) > FAILURE_TIMEOUT


def _record_failure(broker: str):
    _last_failure[broker] = time.time()
    logger.warning(f"❌ {broker.upper()} marked temporarily unhealthy.")


def _record_success(broker: str):
    _broker_health[broker] = time.time()
    logger.debug(f"✅ {broker.upper()} marked healthy.")


def _ping_broker(broker: str) -> float:
    """
    Measure latency to broker API.
    Returns response time in ms or large number if failed.
    """
    url = BROKER_PING_URLS.get(broker)
    if not url:
        return 9999

    start = time.time()
    try:
        res = requests.get(url, timeout=2)
        if res.status_code == 200:
            latency = (time.time() - start) * 1000
            return round(latency, 2)
    except Exception:
        pass
    return 9999


def get_smart_broker(pair: str) -> str:
    """
    Dynamically choose best broker based on:
      • Recent success timestamps
      • Health / failure cooldown
      • Latency (ping time)
      • Enabled brokers list
    """
    enabled = os.getenv("ENABLED_BROKERS", "kraken,oanda,alpaca,tos").split(",")
    enabled = [b.strip().lower() for b in enabled if b.strip()]

    # Step 1 — Filter by health
    healthy = [b for b in enabled if _is_broker_healthy(b)]
    if not healthy:
        fallback = enabled[0] if enabled else "kraken"
        logger.warning(f"⚠️ No healthy brokers, falling back to {fallback.upper()}")
        return fallback

    # Step 2 — Measure latency
    latencies = {b: _ping_broker(b) for b in healthy}
    best_latency = min(latencies.values())
    fast_brokers = [b for b, l in latencies.items() if l == best_latency]

    # Step 3 — Rank by recent success if tie
    if len(fast_brokers) > 1:
        ranked = sorted(
            fast_brokers,
            key=lambda b: get_last_success_time(pair, b),
            reverse=True
        )
        broker = ranked[0]
    else:
        broker = fast_brokers[0]

    logger.info(
        f"🧭 SmartRouter → {broker.upper()} "
        f"(latency={latencies[broker]}ms, healthy={len(healthy)}/{len(enabled)})"
    )
    return broker


def report_broker_result(broker: str, success: bool):
    """Called after each order/fetch to update broker health memory."""
    if success:
        _record_success(broker)
    else:
        _record_failure(broker)
