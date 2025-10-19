import os
import requests
import logging
import json

logger = logging.getLogger(__name__)

# === Instrument precision map ===
INSTRUMENT_PRECISION = {
    "JPY": 3, "USD": 5, "GBP": 5, "EUR": 5, "AUD": 5,
    "NZD": 5, "CAD": 5, "CHF": 5, "XAU": 2, "XAG": 3,
    "BTC": 2, "ETH": 2
}

def get_precision(pair: str):
    """Return precision based on quote currency (last 3 chars)."""
    quote = pair.split("/")[-1]
    return INSTRUMENT_PRECISION.get(quote, 5)

def round_price(pair, value):
    if value is None:
        return None
    precision = get_precision(pair)
    return round(float(value), precision)

# === Utility: fetch OANDA balance ===
def get_account_balance():
    """Fetch current OANDA account balance to calculate dynamic lot size."""
    try:
        OANDA_API_KEY = os.getenv("OANDA_API_KEY")
        OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
        OANDA_BASE_URL = os.getenv("OANDA_BASE_URL", "https://api-fxtrade.oanda.com/v3")
        headers = {"Authorization": f"Bearer {OANDA_API_KEY}"}
        url = f"{OANDA_BASE_URL}/accounts/{OANDA_ACCOUNT_ID}/summary"
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return float(data["account"]["balance"])
    except Exception as e:
        logger.warning(f"⚠️ Could not fetch OANDA balance: {e}")
        return None

def place_order(pair, side, price=None, sl=None, tp=None, lot_size=None, score=None):
    """
    Place a market order on OANDA with auto SL/TP and dynamic position sizing.
    lot_size is optional — will be calculated from RISK_PCT, balance, and score.
    """

    # === Environment ===
    OANDA_API_KEY = os.getenv("OANDA_API_KEY")
    OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
    OANDA_BASE_URL = os.getenv("OANDA_BASE_URL", "https://api-fxtrade.oanda.com/v3")

    # Risk settings
    RISK_PCT = float(os.getenv("RISK_PCT", 0.10))          # total risk per trade
    STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", 0.04))
    TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", 0.25))
    BASE_UNITS = int(os.getenv("BASE_UNITS", 1000))         # fallback minimum

    if not OANDA_API_KEY or not OANDA_ACCOUNT_ID:
        logger.error("❌ Missing OANDA credentials in environment.")
        return None

    # === Determine balance and lot size dynamically ===
    balance = get_account_balance() or 1000  # fallback for DRYRUN
    precision = get_precision(pair)
    current_price = float(price) if price else None

    # Calculate dynamic lot size based on risk and confidence score (0–10)
    if not lot_size:
        # fraction of account balance at risk
        risk_capital = balance * RISK_PCT
        # expected loss per unit at SL
        if current_price:
            sl_distance = current_price * STOP_LOSS_PCT
            loss_per_unit = sl_distance or 1
        else:
            loss_per_unit = 1
        # Adjust by confidence score
        confidence_multiplier = (score or 5) / 10
        lot_size = max(int((risk_capital / loss_per_unit) * confidence_multiplier), BASE_UNITS)

    instrument = pair.replace("/", "_")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OANDA_API_KEY}"
    }

    # === Auto-calc SL/TP if missing ===
    if current_price:
        if not tp or not sl:
            if side.lower() == "buy":
                tp = tp or current_price * (1 + TAKE_PROFIT_PCT)
                sl = sl or current_price * (1 - STOP_LOSS_PCT)
            else:
                tp = tp or current_price * (1 - TAKE_PROFIT_PCT)
                sl = sl or current_price * (1 + STOP_LOSS_PCT)

    tp = round_price(pair, tp)
    sl = round_price(pair, sl)

    data = {
        "order": {
            "units": str(lot_size if side.lower() == "buy" else -lot_size),
            "instrument": instrument,
            "timeInForce": "FOK",
            "type": "MARKET",
            "positionFill": "DEFAULT"
        }
    }

    if tp:
        data["order"]["takeProfitOnFill"] = {"price": str(tp), "timeInForce": "GTC"}
    if sl:
        data["order"]["stopLossOnFill"] = {"price": str(sl), "timeInForce": "GTC"}

    # === Send to OANDA ===
    try:
        url = f"{OANDA_BASE_URL}/accounts/{OANDA_ACCOUNT_ID}/orders"
        response = requests.post(url, headers=headers, json=data)

        if not response.ok:
            logger.error(f"💥 OANDA API Error [{response.status_code}]: {response.text}")
            return None

        result = response.json()
        logger.info(
            f"✅ OANDA Order Placed: {side.upper()} {lot_size} {pair} | "
            f"SL={sl} TP={tp} | Risk {RISK_PCT*100:.1f}% | "
            f"Conf={score or 0:.1f}/10 | Bal=${balance:,.2f}"
        )
        logger.debug(json.dumps(result, indent=2))
        return result

    except Exception as e:
        logger.error(f"💥 Unexpected OANDA order error for {pair}: {e}")
        return None
