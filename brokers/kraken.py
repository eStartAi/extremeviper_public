import os
import requests
import logging
import json

logger = logging.getLogger(__name__)

# === Instrument precision map (Kraken symbols) ===
INSTRUMENT_PRECISION = {
    "USD": 2, "EUR": 2, "GBP": 2, "JPY": 0,
    "BTC": 2, "ETH": 2, "ADA": 4, "SOL": 2, "XRP": 4, "DOT": 3
}

def get_precision(pair: str):
    """Return decimal precision based on quote currency."""
    quote = pair.split("/")[-1]
    return INSTRUMENT_PRECISION.get(quote, 2)

def round_price(pair, value):
    if value is None:
        return None
    precision = get_precision(pair)
    return round(float(value), precision)

# === Utility: mock balance retrieval ===
def get_account_balance():
    """
    Fetch account balance from Kraken (placeholder for real API call).
    Replace this with signed Kraken balance endpoint if using live trading.
    """
    try:
        # Simulate or later replace with: requests.get(kraken_api_endpoint)
        fake_balance = float(os.getenv("DEFAULT_BALANCE", 1000))
        return fake_balance
    except Exception as e:
        logger.warning(f"⚠️ Could not fetch Kraken balance: {e}")
        return 1000

def place_order(pair, side, price=None, sl=None, tp=None, lot_size=None, score=None):
    """
    Simulated Kraken market order with dynamic risk sizing & auto SL/TP.
    Replace requests.post with Kraken authenticated API when ready.
    """

    # === Env ===
    RISK_PCT = float(os.getenv("RISK_PCT", 0.10))
    STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", 0.04))
    TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", 0.25))
    BASE_UNITS = float(os.getenv("BASE_UNITS", 0.01))

    balance = get_account_balance()
    current_price = float(price) if price else None

    # === Dynamic lot sizing ===
    if not lot_size:
        risk_capital = balance * RISK_PCT
        sl_distance = current_price * STOP_LOSS_PCT if current_price else 1
        loss_per_unit = sl_distance or 1
        confidence_multiplier = (score or 5) / 10
        lot_size = max(round((risk_capital / loss_per_unit) * confidence_multiplier, 5), BASE_UNITS)

    # === Auto SL/TP ===
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

    # === Simulate or send real Kraken order ===
    try:
        # Here we only log for DRYRUN mode
        logger.info(
            f"✅ KRAKEN Order Placed: {side.upper()} {lot_size} {pair} | "
            f"SL={sl} TP={tp} | Risk {RISK_PCT*100:.1f}% | "
            f"Conf={score or 0:.1f}/10 | Bal=${balance:,.2f}"
        )

        # Return mock response to mimic OANDA JSON
        return {
            "status": "success",
            "broker": "kraken",
            "pair": pair,
            "side": side,
            "lot_size": lot_size,
            "sl": sl,
            "tp": tp,
            "balance": balance
        }

    except Exception as e:
        logger.error(f"💥 Kraken order error for {pair}: {e}")
        return None

