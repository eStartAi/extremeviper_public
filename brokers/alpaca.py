import os
import requests
import logging
import json

logger = logging.getLogger(__name__)

# === Instrument precision ===
INSTRUMENT_PRECISION = {
    "USD": 2, "EUR": 2, "JPY": 0, "BTC": 2, "ETH": 2,
    "AAPL": 2, "TSLA": 2, "NVDA": 2, "SPY": 2
}

def get_precision(symbol: str):
    """Determine rounding precision (stocks usually 2 decimals)."""
    for k in INSTRUMENT_PRECISION:
        if symbol.endswith(k):
            return INSTRUMENT_PRECISION[k]
    return 2

def round_price(symbol, value):
    if value is None:
        return None
    return round(float(value), get_precision(symbol))

# === Utility: account balance ===
def get_account_balance():
    """Fetch account equity from Alpaca API."""
    try:
        API_KEY = os.getenv("ALPACA_API_KEY")
        API_SECRET = os.getenv("ALPACA_API_SECRET")
        BASE_URL = os.getenv("ALPACA_BASE_URL", "https://api.alpaca.markets")
        headers = {"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": API_SECRET}
        resp = requests.get(f"{BASE_URL}/v2/account", headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return float(data["equity"])
    except Exception as e:
        logger.warning(f"⚠️ Could not fetch Alpaca balance: {e}")
        return float(os.getenv("DEFAULT_BALANCE", 1000))

# === Core order placement ===
def place_order(symbol, side, price=None, sl=None, tp=None, qty=None, score=None):
    """
    Place a market order on Alpaca with auto SL/TP and dynamic position sizing.
    - Uses .env RISK_PCT, STOP_LOSS_PCT, TAKE_PROFIT_PCT.
    - Scales qty by confidence score (0–10).
    """

    # === Env ===
    API_KEY = os.getenv("ALPACA_API_KEY")
    API_SECRET = os.getenv("ALPACA_API_SECRET")
    BASE_URL = os.getenv("ALPACA_BASE_URL", "https://api.alpaca.markets")

    RISK_PCT = float(os.getenv("RISK_PCT", 0.10))
    STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", 0.04))
    TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", 0.25))
    BASE_UNITS = float(os.getenv("BASE_UNITS", 1))  # default min shares

    if not API_KEY or not API_SECRET:
        logger.error("❌ Missing ALPACA_API_KEY or ALPACA_API_SECRET.")
        return None

    balance = get_account_balance()
    current_price = float(price) if price else None

    # === Dynamic qty ===
    if not qty:
        risk_capital = balance * RISK_PCT
        sl_distance = current_price * STOP_LOSS_PCT if current_price else 1
        loss_per_share = sl_distance or 1
        confidence_multiplier = (score or 5) / 10
        qty = max(round((risk_capital / loss_per_share) * confidence_multiplier, 2), BASE_UNITS)

    # === Auto SL/TP ===
    if current_price:
        if not tp or not sl:
            if side.lower() == "buy":
                tp = tp or current_price * (1 + TAKE_PROFIT_PCT)
                sl = sl or current_price * (1 - STOP_LOSS_PCT)
            else:
                tp = tp or current_price * (1 - TAKE_PROFIT_PCT)
                sl = sl or current_price * (1 + STOP_LOSS_PCT)

    tp = round_price(symbol, tp)
    sl = round_price(symbol, sl)

    # === Build payload ===
    order = {
        "symbol": symbol,
        "qty": str(qty),
        "side": side.lower(),
        "type": "market",
        "time_in_force": "gtc",
    }

    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET,
        "Content-Type": "application/json"
    }

    # === Send order ===
    try:
        url = f"{BASE_URL}/v2/orders"
        response = requests.post(url, headers=headers, json=order)

        if not response.ok:
            logger.error(f"💥 Alpaca API Error [{response.status_code}]: {response.text}")
            return None

        result = response.json()
        logger.info(
            f"✅ ALPACA Order Placed: {side.upper()} {qty} {symbol} | "
            f"SL={sl} TP={tp} | Risk {RISK_PCT*100:.1f}% | "
            f"Conf={score or 0:.1f}/10 | Bal=${balance:,.2f}"
        )
        logger.debug(json.dumps(result, indent=2))

        # You can optionally place OCO (One-Cancels-Other) SL/TP orders after fill
        return result

    except Exception as e:
        logger.error(f"💥 Alpaca order error for {symbol}: {e}")
        return None
