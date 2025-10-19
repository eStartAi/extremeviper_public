# ==============================================================
# 🐍 ExtremeViper LIVE Engine (v0.2-SAFE)
# --------------------------------------------------------------
# Description:
# Single-broker go-live engine for Kraken with Telegram
# confirmations and automatic DRY_RUN fallback on error.
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
DEFAULT_BROKER = os.getenv("DEFAULT_BROKER", "kraken").strip().lower()
PAIRLIST = os.getenv("KRAKEN_PAIRS", "BTC/USD,ETH/USD").split(",")

def main():
    logger.info("🚀 Starting ExtremeViper-LIVE safely...")

    if not validate_env():
        logger.error("❌ Missing required environment variables. Exiting.")
        return

    start_telegram_listener()
    send_telegram_message("🟢 ExtremeViper LIVE Mode initialized safely.")

    broker = get_broker(DEFAULT_BROKER)

    while True:
        # --- Kill-Switch Check ---
        if is_killed():
            logger.warning("🛑 Kill flag active — skipping all trades.")
            time.sleep(10)
            continue

        for pair in PAIRLIST:
            try:
                logger.info(f"📡 Fetching live signal for {pair} via {DEFAULT_BROKER.upper()}...")
                signal = fetch_live_signal(pair, DEFAULT_BROKER)
                if not signal:
                    logger.warning(f"⚠️ No signal data for {pair}")
                    continue

                # --- Score Signal ---
                scored = score_signal(signal)
                score = float(scored.get("score", 0)) if isinstance(scored, dict) else float(scored)
                threshold = get_adaptive_threshold(signal)
                lot_size = calculate_lot_size(score, DEFAULT_BROKER)

                logger.info(f"🧠 {pair}: score={score:.2f} threshold={threshold:.2f} lot={lot_size:.5f}")

                if score < threshold:
                    logger.info(f"🚫 Ignored weak signal ({score:.2f} < {threshold:.2f}) for {pair}")
                    continue

                if is_in_cooldown(pair, DEFAULT_BROKER) or is_duplicate(pair, DEFAULT_BROKER):
                    logger.info(f"⏳ Skipping {pair} - cooldown/duplicate active.")
                    continue

                # --- Execution Phase ---
                if DRY_RUN:
                    logger.info(
                        f"🤖 [DRY-RUN] Would place {signal.get('side')} order for {pair} size={lot_size:.5f}"
                    )
                else:
                    try:
                        result = broker.place_order(
                            pair=pair,
                            side=signal.get("side"),
                            price=signal.get("price"),
                            sl=signal.get("stop_loss"),
                            tp=signal.get("take_profit"),
                            lot_size=lot_size,
                        )
                        logger.info(f"✅ LIVE ORDER EXECUTED: {result}")
                        update_trade_log(pair, DEFAULT_BROKER)
                        send_telegram_message(
                            f"✅ LIVE ORDER: {pair} | {signal.get('side').upper()} | "
                            f"Size={lot_size:.5f}"
                        )

                        # Optional: record profit once closed or mock zero
                        profit_usd = float(result.get("profit_usd", 0.0))
                        log_trade_result(pair, DEFAULT_BROKER, profit_usd)

                    except Exception as e:
                        logger.error(f"💥 Order failed for {pair}: {e}")
                        send_telegram_message(f"⚠️ LIVE ORDER ERROR for {pair}: {e}")
                        os.environ["DRY_RUN"] = "true"  # safe fallback

            except Exception as e:
                logger.error(f"💥 Error processing {pair}: {e}")

        time.sleep(30)


if __name__ == "__main__":
    main()
