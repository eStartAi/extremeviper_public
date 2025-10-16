# DRYRUNmain.py
# 🔁 ExtremeViper DRY-RUN Engine
# Version: 0.0.13+
# Description: Multi-broker scanner (OANDA, Kraken) with adaptive throttle, confidence scoring,
# risk-based lot sizing, duplicate/cooldown filters, and DRY_RUN-safe execution.

import os
import time
import logging
from dotenv import load_dotenv

from broker import get_broker
from utils.validate_env import validate_env
from utils.signal_fetcher import fetch_live_signal
from utils.score_engine import score_signal
from utils.risk_manager import calculate_lot_size
from utils.adaptive_throttle import get_adaptive_threshold
from utils.trade_control_logger import is_in_cooldown, is_duplicate, update_trade_log

# === ENV & Logging Setup ===
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
ENABLED_BROKERS = os.getenv("ENABLED_BROKERS", "oanda,kraken").split(",")

PAIRMAP = {
    "oanda": os.getenv("OANDA_PAIRS", "EUR/USD,GBP/USD").split(","),
    "kraken": os.getenv("KRAKEN_PAIRS", "BTC/USD,ETH/USD").split(",")
}

def main():
    logger.info("🧠 Starting ExtremeViper-DRYRUN safely...")

    if not validate_env():
        logger.error("❌ Missing required environment variables. Exiting.")
        return

    while True:
        for broker_name in ENABLED_BROKERS:
            broker_name = broker_name.strip().lower()
            pairs = PAIRMAP.get(broker_name, [])
            broker = get_broker(broker_name)

            for pair in pairs:
                logger.info(f"📡 Fetching live signal for {pair} via {broker_name.upper()}...")
                signal = fetch_live_signal(pair, broker_name)
                if not signal:
                    logger.warning(f"⚠️ No signal data for {pair}")
                    continue

                score = score_signal(signal)
                threshold = get_adaptive_threshold(signal)
                lot_size = calculate_lot_size(score, broker_name)

                logger.info(f"🧠 Scored {pair} = {score:.2f}/10 | Threshold = {threshold:.2f} | Lot Size = {lot_size}")

                if score < threshold:
                    logger.info(f"🚫 Ignored weak signal ({score:.2f} < {threshold:.2f}) for {pair}")
                    continue

                if is_in_cooldown(pair, broker_name) or is_duplicate(pair, broker_name):
                    logger.info(f"⏳ Skipping {pair} - cooldown or duplicate active.")
                    continue

                if DRY_RUN:
                    logger.info(f"🤖 [DRY-RUN] Would place order: {pair} | Side: {signal['side']} | Size: {lot_size}")
                else:
                    result = broker.place_order(
                        pair=pair,
                        side=signal["side"],
                        price=signal["price"],
                        sl=signal["stop_loss"],
                        tp=signal["take_profit"],
                        lot_size=lot_size
                    )
                    logger.info(f"✅ Order Placed: {result}")
                    update_trade_log(pair, broker_name)

        time.sleep(30)  # 🕒 Delay between full broker loops

if __name__ == "__main__":
    main()
