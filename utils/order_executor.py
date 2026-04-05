import logging
from datetime import datetime
from brokers import kraken, oanda  # Add alpaca, tos if needed
from utils.risk_manager import calculate_lot_size

logger = logging.getLogger(__name__)


def execute_trade(pair, broker, signal: dict, score: float, dry_run=True):
    side = signal.get("side")
    price = signal.get("price")
    sl = signal.get("sl")
    tp = signal.get("tp")

    lot_size = calculate_lot_size(score=score, price=price)

    if dry_run:
        logger.info(f"🟡 [DRY RUN] {broker.upper()} → {side.upper()} {pair} | Size={lot_size:.4f} @ {price} | SL={sl} | TP={tp}")
        return {
            "status": "dry_run",
            "pair": pair,
            "side": side,
            "price": price,
            "sl": sl,
            "tp": tp,
            "lot_size": lot_size,
            "broker": broker,
            "timestamp": datetime.utcnow().isoformat()
        }

    try:
        if broker.lower() == "kraken":
            response = kraken.place_order(pair, side, price, sl, tp, lot_size)
        elif broker.lower() == "oanda":
            response = oanda.place_order(pair, side, price, sl, tp, lot_size)
        else:
            logger.error(f"❌ Unsupported broker: {broker}")
            return None

        logger.info(f"✅ Order Executed via {broker.upper()}: {side.upper()} {pair} | Size={lot_size:.4f}")
        return response

    except Exception as e:
        logger.error(f"❌ Trade execution failed: {e}")
        return None

