import logging
from brokers import oanda, kraken, alpaca, tos

logger = logging.getLogger(__name__)

def get_broker(name: str):
    name = name.lower()

    brokers = {
        "oanda": oanda,
        "kraken": kraken,
        "alpaca": alpaca,
        "tos": tos,
    }

    broker = brokers.get(name)
    if not broker:
        raise ValueError(f"Unsupported broker: {name}")

    required_methods = ["fetch_candles", "get_price", "place_order", "ping", "get_balance"]
    for method in required_methods:
        if not hasattr(broker, method):
            logger.warning(f"⚠️ Missing '{method}' in {name} broker")

    return broker
