# ==============================================================
# 🐍 ExtremeViper LIVE Engine (v0.2.0-SMART-ROUTER)
# --------------------------------------------------------------
# Multi-broker LIVE engine with:
# - Adaptive threshold
# - Confidence-based risk sizing
# - Smart broker auto-selector (OANDA, Kraken, Alpaca)
# - Telegram kill-switch + status control
# - Cooldown, duplicate & PnL logging
# - Safe auto-fallback to DRY-RUN on failure
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
from utils.broker_selector import smart_broker_selector  # 🧭 Smart Router

# === ENV & Logging Setup ===
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
DEFAULT_BROKER = os.getenv("DEFAULT_BROKER", "oanda")
ENABLED_BROKERS = os.getenv("ENABLED_BROKERS", "oanda,kraken,alpaca").split(",")

PAIRMAP = {
    "oanda": os.getenv("OANDA_PAIRS", "").split(","),
    "kraken": os.getenv("KRAKEN_PAIRS", "").split(","),
    "alpaca": os.getenv("ALPACA_PAIRS", "").split(","),
}


def main():
    logger.info("🚀 Starting ExtremeViper LIVE Mode...")
    if not validate_env():
        logger.error("❌ Missing required environment variables — exiting.")
        return

    start_telegram_listener()
    send_telegram_message("🟢 ExtremeViper LIVE Engine started successfully.")

    while True:
        if is_killed():
            logger.warning("🛑 Kill-switch active — halting trades temporarily.")
            time.sleep(10)
            continue

        for broker_name in ENABLED_BROKERS:
            broker_name = broker_name.strip().lower()
            pairs = [p.strip() for p in PAIRMAP.get(broker_name, []) if p.strip()]
            if not pairs:
                continue

            broker = get_broker(broker_name)

            for pair in pairs:
                try:
                    # === Smart Broker Auto-Selector ===
                    selected_broker = smart_broker_selector(
                        pair, os.getenv("ENABLED_BROKERS", "oanda,kraken,alpaca")
                    ) or broker_name

                    if selected_broker != broker_name:
                        broker = get_broker(selected_broker)
                        broker_name = selected_broker

                    # === Fetch Signal ===
                    logger.info(f"📡 Fetching live signal for {pair} via {broker_name.upper()}...")
                    signal = fetch_live_signal(pair, broker_name)
                    if not signal:
                        logger.warning(f"⚠️ No signal data for {pair}")
                        continue

                    # === Score Signal ===
                    scored = score_signal(signal)
                    score = float(scored.get("score", 0)) if isinstance(scored, dict) else float(scored)
                    threshold = get_adaptive_threshold(signal)
                    lot_size = calculate_lot_size(score, broker_name)

                    logger.info(
                        f"🧠 {broker_name.upper()} {pair} → score={score:.2f} "
                        f"| threshold={threshold:.2f} | lot={lot_size:.5f}"
                    )

                    # === Decision Filters ===
                    if score < threshold:
                        logger.info(f"🚫 Ignored weak signal ({score:.2f} < {threshold:.2f}) for {pair}")
                        continue

                    if is_in_cooldown(pair, broker_name) or is_duplicate(pair, broker_name):
                        logger.info(f"⏳ Skipping {pair} - cooldown/duplicate active.")
                        continue

                    # === Execute LIVE Order ===
                    side = signal.get("side")
                    try:
                        result = broker.place_order(
                            pair=pair,
                            side=side,
                            price=signal.get("price"),
                            sl=signal.get("stop_loss"),
                            tp=signal.get("take_profit"),
                            lot_size=lot_size,
                        )
                        logger.info(f"✅ LIVE ORDER [{broker_name.upper()}]: {result}")
                        update_trade_log(pair, broker_name)

                        send_telegram_message(
                            f"✅ LIVE ORDER: {pair} | {broker_name.upper()} | "
                            f"{side.upper()} | Size={lot_size:.5f}"
                        )

                        # Record realized or 0 profit
                        profit_usd = float(result.get("profit_usd", 0.0)) if result else 0.0
                        log_trade_result(pair, broker_name, profit_usd)

                    except Exception as e:
                        logger.error(f"💥 Order failed for {pair} ({broker_name}): {e}")
                        send_telegram_message(f"⚠️ LIVE ORDER ERROR for {pair}: {e}")
                        os.environ["DRY_RUN"] = "true"  # Safe fallback
                        logger.warning("🔁 Switching temporarily to DRY-RUN mode for safety.")

                except Exception as e:
                    logger.error(f"💥 Error processing {pair} ({broker_name}): {e}")

        time.sleep(int(os.getenv("CYCLE_DELAY_SECONDS", 30)))


if __name__ == "__main__":
    main()
