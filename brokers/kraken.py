# brokers/kraken.py

import os
import logging
from utils.pairmap import PAIRMAP_KRAKEN

logger = logging.getLogger(__name__)

KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY")
KRAKEN_API_SECRET = os.getenv("KRAKEN_API_SECRET")
KRAKEN_BASE_URL = os.getenv("KRAKEN_BASE_URL", "https://api.kraken.com")

def place_order(pair, side, price, sl=None, tp=None, lot_size=0.01):
    """
    Simulated Kraken market order with mapped pair and score-based lot size.
    Works in DRY_RUN mode for ExtremeViper.
    """

    # ✅ Map human-readable pair (BTC/USD) → Kraken format (XBTUSD)
    kr_pair = PAIRMAP_KRAKEN.get(pair, pair.replace("/", ""))

    payload = {
        "pair": kr_pair,
        "type": side.lower(),
        "ordertype": "market",
        "volume": str(lot_size),  # Kraken requires string
    }

    # TODO: Add SL/TP via conditional close logic when live mode is enabled
    try:
        logger.info(
            f"✅ Kraken Order Simulated: {side.upper()} {lot_size} lot {pair} "
            f"(Mapped → {kr_pair}) | Price={price}"
        )
        return {"status": "success", "payload": payload}

    except Exception as e:
        logger.error(f"❌ Kraken order failed: {e}")
        return {"status": "error", "reason": str(e)}



