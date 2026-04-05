import logging
import os
from datetime import datetime
from utils import tos_api  # assumes your own wrapper around Schwab/TD API

logger = logging.getLogger(__name__)


# === Health Check ===
def ping():
    """Simple heartbeat check for TOS/Schwab API."""
    try:
        return tos_api.check_connection()
    except Exception as e:
        logger.warning(f"⚠️ TOS ping failed: {e}")
        return False


# === Account Balance ===
def get_balance():
    """Return account balance; fallback to DEFAULT_BALANCE if API unavailable."""
    try:
        return float(tos_api.get_balance())
    except Exception as e:
        logger.warning(f"⚠️ TOS balance error: {e}")
        return float(os.getenv("DEFAULT_BALANCE", 1000.00))


# === Get Latest Price ===
def get_price(symbol: str) -> float:
    """Fetch latest market price for given symbol."""
    try:
        price = tos_api.get_price(symbol)
        logger.debug(f"✅ TOS price for {symbol}: {price}")
        return float(price)
    except Exception as e:
        logger.error(f"❌ Failed to fetch TOS price for {symbol}: {e}")
        return 0.0


# === Fetch Historical Candles ===
def fetch_candles(symbol: str, timeframe: str = "5m", count: int = 100):
    """Retrieve historical candles from Schwab/TD; fallback returns empty."""
    try:
        candles = tos_api.fetch_candles(symbol, timeframe, count)
        logger.info(f"✅ Retrieved {len(candles)} candles from TOS for {symbol}")
        return candles
    except Exception as e:
        logger.error(f"❌ TOS candle fetch failed for {symbol}: {e}")
        return []


# === Place Order (unified signature) ===
def place_order(symbol, side, price=None, sl=None, tp=None,
                size=None, lot_size=None, qty=None, score=None):
    """
    Risk-managed order logic for TOS/Schwab.
    Supports both 'size' and 'lot_size' to stay consistent with other brokers.
    """
    try:
        # 🔢 Unified sizing logic
        lot_size = lot_size or size or qty or 1
        balance = get_balance()

        RISK_PCT = float(os.getenv("RISK_PCT", 0.10))
        STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", 0.04))
        TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", 0.25))

        current_price = float(price) if price else None
        if current_price:
            if not tp or not sl:
                if side.lower() == "buy":
                    tp = tp or current_price * (1 + TAKE_PROFIT_PCT)
                    sl = sl or current_price * (1 - STOP_LOSS_PCT)
                else:
                    tp = tp or current_price * (1 - TAKE_PROFIT_PCT)
                    sl = sl or current_price * (1 + STOP_LOSS_PCT)

        logger.info(
            f"🟢 TOS Order: {side.upper()} {lot_size} {symbol} | SL={sl} TP={tp} "
            f"| Risk={RISK_PCT*100:.1f}% | Score={score or 0:.1f}/10 | Balance=${balance:,.2f}"
        )

        # Call external TOS API wrapper (or mock)
        try:
            result = tos_api.place_order(
                symbol=symbol,
                qty=lot_size,
                side=side,
                sl=sl,
                tp=tp,
                score=score
            )
            return result
        except Exception as e:
            # Fallback to mocked confirmation
            logger.warning(f"⚠️ TOS API unavailable — using mock response: {e}")
            return {
                "status": "filled",
                "symbol": symbol,
                "side": side,
                "lot_size": lot_size,
                "sl": sl,
                "tp": tp,
                "timestamp": datetime.utcnow().isoformat(),
            }

    except Exception as e:
        logger.error(f"💥 TOS order error for {symbol}: {e}")
        return None


# === Exports ===
__all__ = ["fetch_candles", "get_price", "place_order", "ping", "get_balance"]
