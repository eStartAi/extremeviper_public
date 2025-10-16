# brokers/oanda.py

import os
import requests
import logging

logger = logging.getLogger(__name__)

OANDA_API_KEY = os.getenv("OANDA_API_KEY")
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
OANDA_BASE_URL = os.getenv("OANDA_BASE_URL", "https://api-fxpractice.oanda.com")

HEADERS = {
    "Authorization": f"Bearer {OANDA_API_KEY}",
    "Content-Type": "application/json"
}

def place_order(pair, side, price, sl, tp, lot_size=1.0):
    units = int(lot_size * 1000)
    if side.lower() == "sell":
        units *= -1

    order_data = {
        "order": {
            "instrument": pair.replace("/", "_"),
            "units": str(units),
            "type": "MARKET",
            "positionFill": "DEFAULT",
            "stopLossOnFill": {"price": str(sl)},
            "takeProfitOnFill": {"price": str(tp)}
        }
    }

    endpoint = f"{OANDA_BASE_URL}/v3/accounts/{OANDA_ACCOUNT_ID}/orders"

    try:
        response = requests.post(endpoint, headers=HEADERS, json=order_data)
        response.raise_for_status()
        logger.info(f"✅ OANDA Order Placed: {side.upper()} {lot_size} lot {pair}")
        return response.json()
    except Exception as e:
        logger.error(f"❌ OANDA order failed: {e}")
        return None
