# ==============================================================
# 🐍 ExtremeViper DRY-RUN Engine (v0.1.1-SAFE-PnL)
# --------------------------------------------------------------
# Description:
# Multi-broker scanner (OANDA, Kraken) with adaptive throttle,
# confidence scoring, risk-based lot sizing, duplicate/cooldown filters,
# Telegram kill-switch + status command, and PnL auto-shutdown logic.
# ==============================================================

import os
import time
import logging
from dotenv import load_dotenv

from broker import get_broker
from utils.pnl_logger import log_trade_result
from utils.validate_env import validate_env
from utils.signal_fetcher import fetch_live_signal
from utils.score_engine import score_signal
from utils.risk_manager import calculate_lot_size
from utils.adaptive_throttle import get_adaptive_threshold
from utils.trade_control_logger import is_in_cooldown, is_duplicate, update_trade_log
from utils.telegram_service import start_telegram_listener, is_killed, send_telegram_message

# === ENV & Logging Setup ===
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
ENABLED_BROKERS = os.getenv("ENABLED_BROKERS", "oanda,kraken").split(",")

PAIRMAP = {
    "oanda": os.getenv("OANDA_PAIRS", "EUR/USD,GBP/USD").split(","),
    "kraken": os.getenv("KRAKEN_PAIRS", "BTC/USD,ETH/USD").split(","),
}


def main():
    logger.info("🧠 Starting ExtremeViper-DRYRUN safely...")

    # === 1. Validate Environment ===
    if not validate_env():
        logger.error("❌ Missing required environment variables. Exiting.")
        return

    # === 2. Start Telegram Kill-Switch Listener ===
    start_telegram_listener()
    send_telegram_message("🚀 ExtremeViper started safely in DRYRUN mode.")

    # === 3. Main Loop ===
    while True:
        # --- Global Kill-Switch Check ---
        if is_killed():
            logger.warning("🛑 Kill flag active — skipping all trades.")
            time.sleep(10)
            continue

        # --- Broker Scanning ---
        for broker_name in ENABLED_BROKERS:
            broker_name = broker_name.strip().lower()
            pairs = PAIRMAP.get(broker_name, [])
            broker = get_broker(broker_name)

            for pair in pairs:
                try:
                    # --- Fetch Signal ---
                    logger.info(f"📡 Fetching live signal for {pair} via {broker_name.upper()}...")
                    signal = fetch_live_signal(pair, broker_name)
                    if not signal:
                        logger.warning(f"⚠️ No signal data for {pair}")
                        continue

                    # --- Score Signal ---
                    scored = score_signal(signal)
                    if isinstance(scored, dict):
                        score = float(scored.get("score", 0))
                    else:
                        score = float(scored)

                    threshold = get_adaptive_threshold(signal)
                    lot_size = calculate_lot_size(score, broker_name)
                    logger.info(
                        f"🧠 Scored {pair} = {score:.2f}/10 | Threshold = {threshold:.2f} | Lot Size = {lot_size:.5f}"
                    )

                    # --- Decision Filters ---
                    if score < threshold:
                        logger.info(f"🚫 Ignored weak signal ({score:.2f} < {threshold:.2f}) for {pair}")
                        continue

                    if is_in_cooldown(pair, broker_name) or is_duplicate(pair, broker_name):
                        logger.info(f"⏳ Skipping {pair} - cooldown or duplicate active.")
                        continue

                    # --- Execution Phase ---
                    if DRY_RUN:
                        logger.info(
                            f"🤖 [DRY-RUN] Would place order: {pair} | Side: {signal.get('side')} | "
                            f"Size: {lot_size:.5f}"
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
                        logger.info(f"✅ LIVE ORDER: {result}")
                        update_trade_log(pair, broker_name)
                        send_telegram_message(
                            f"✅ LIVE ORDER: {pair} | Side: {signal.get('side')} | Size: {lot_size:.5f}"
                        )

                        # --- Log PnL (placeholder or API result) ---
                        profit_usd = result.get("profit_usd", 0.0)
                        log_trade_result(pair, broker_name, profit_usd)

                except Exception as e:
                    logger.error(f"💥 Error while processing {pair} ({broker_name}): {e}", exc_info=False)

        # --- Loop Delay ---
        time.sleep(30)  # 🕒 Delay between full broker loops


if __name__ == "__main__":
    main()
