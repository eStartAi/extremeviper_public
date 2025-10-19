# ==============================================================
# 🐍 ExtremeViper Parallel LIVE Engine (v0.3-SAFE)
# --------------------------------------------------------------
# Description:
# Runs Kraken + OANDA simultaneously in live mode
# with Telegram alerts, kill-switch, and auto PnL shutdown.
# ==============================================================

import os
import time
import logging
from dotenv import load_dotenv

from broker import get_broker
from utils.pnl_logger import log_trade_result, check_pnl_limits
from utils.validate_env import validate_env
from utils.signal_fetcher import fetch_live_signal
from utils.score_engine import score_signal
from utils.risk_manager import calculate_lot_size
from utils.adaptive_throttle import get_adaptive_threshold
from utils.trade_control_logger import is_in_cooldown, is_duplicate, update_trade_log
from utils.telegram_service import (
    start_telegram_listener,
    is_killed,
    send_telegram_message,
)

# === ENV & Logging Setup ===
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
ENABLED_BROKERS = os.getenv("ENABLED_BROKERS", "kraken,oanda").split(",")

PAIRMAP = {
    "kraken": os.getenv("KRAKEN_PAIRS", "BTC/USD,ETH/USD").split(","),
    "oanda": os.getenv("OANDA_PAIRS", "EUR/USD,GBP/USD").split(","),
}


def process_pair(broker_name, broker, pair):
    """Handles signal scoring and trade execution for a single pair."""
    try:
        logger.info(f"📡 Fetching live signal for {pair} via {broker_name.upper()}...")
        signal = fetch_live_signal(pair, broker_name)
        if not signal:
            logger.warning(f"⚠️ No signal data for {pair}")
            return

        scored = score_signal(signal)
        score = float(scored.get("score", 0)) if isinstance(scored, dict) else float(scored)
        threshold = get_adaptive_threshold(signal)
        lot_size = calculate_lot_size(score, broker_name)

        logger.info(
            f"🧠 {broker_name.upper()} {pair} → score={score:.2f} | "
            f"threshold={threshold:.2f} | lot={lot_size:.5f}"
        )

        if score < threshold:
            logger.info(f"🚫 Ignored weak signal ({score:.2f} < {threshold:.2f}) for {pair}")
            return

        if is_in_cooldown(pair, broker_name) or is_duplicate(pair, broker_name):
            logger.info(f"⏳ Skipping {pair} - cooldown/duplicate active.")
            return

        # === Execution Phase ===
        if DRY_RUN:
            logger.info(
                f"🤖 [DRY-RUN] Would place {signal.get('side')} order for {pair} "
                f"({broker_name}) size={lot_size:.5f}"
            )
        else:
            result = broker.place_order(
                pair=pair,
                side=signal.get("side"),
                price=signal.get("price"),
                sl=signal.get("stop_loss"),
                tp=signal.get("take_profit"),
                lot_size=lot_size,
            )
            logger.info(f"✅ LIVE ORDER [{broker_name.upper()}]: {result}")
            update_trade_log(pair, broker_name)
            send_telegram_message(
                f"✅ LIVE ORDER [{broker_name.upper()}]: {pair} | {signal.get('side').upper()} | "
                f"Size={lot_size:.5f}"
            )

            # PnL tracking
            profit_usd = float(result.get("profit_usd", 0.0))
            log_trade_result(pair, broker_name, profit_usd)
            check_pnl_limits(profit_usd)

    except Exception as e:
        logger.error(f"💥 Error processing {pair} ({broker_name}): {e}")
        send_telegram_message(f"⚠️ Error on {pair} ({broker_name}): {e}")


def main():
    logger.info("🚀 Starting ExtremeViper Parallel LIVE Mode...")

    if not validate_env():
        logger.error("❌ Missing required environment variables. Exiting.")
        return

    start_telegram_listener()
    send_telegram_message("🟢 ExtremeViper Parallel LIVE Mode started.")

    while True:
        # Global kill check
        if is_killed():
            logger.warning("🛑 Kill flag active — skipping all trades.")
            time.sleep(10)
            continue

        for broker_name in ENABLED_BROKERS:
            broker_name = broker_name.strip().lower()
            broker = get_broker(broker_name)
            pairs = PAIRMAP.get(broker_name, [])

            for pair in pairs:
                process_pair(broker_name, broker, pair)

        time.sleep(30)  # main loop delay


if __name__ == "__main__":
    main()
