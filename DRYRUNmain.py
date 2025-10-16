import os
import time
import logging
from datetime import datetime, timezone

from utils.signal_fetcher import fetch_live_signal
from utils.score_engine import score_signal
from utils.safe_main_wrapper import safe_main
from utils.trade_control_logger import is_in_cooldown, update_trade_log, init_cache
from utils.adaptive_throttle import get_adaptive_score_threshold
from utils.position_sizer import calculate_lot_size

# =====================================================
# Logging Setup
# =====================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# =====================================================
# Core Logic
# =====================================================
@safe_main
def main():
    pairs = [p.strip() for p in os.getenv(
        "PAIRS",
        "EUR/USD,GBP/USD,USD/JPY,AUD/JPY,USD/CAD,NZD/USD,EUR/JPY,GBP/JPY,EUR/GBP,AUD/USD"
    ).split(",")]
    timeframe = os.getenv("TIMEFRAME", "M5")
    dry_run = os.getenv("DRY_RUN", "true").lower() == "true"

    logger.info("🧠 Starting ExtremeViper-DRYRUN safely...")
    init_cache()

    while True:
        for pair in pairs:
            try:
                logger.info(f"📡 Fetching live signal for {pair}...")
                signal = fetch_live_signal(pair=pair, timeframe=timeframe)

                if not signal:
                    logger.warning(f"⚠️ No signal returned for {pair}")
                    continue

                scored = score_signal(signal)
                score = scored.get("score", 0)
                vol_spike = signal.get("VolSpike", 1.0)

                # 🧠 Dynamic minimum score threshold
                threshold = get_adaptive_score_threshold(vol_spike)

                # Optional: Add session label logging
                hour = datetime.now(timezone.utc).hour
                if 0 <= hour <= 7:
                    session = "Asia"
                elif 8 <= hour <= 15:
                    session = "London"
                else:
                    session = "New York"

                logger.info(f"📊 Adaptive threshold: {threshold} | VolSpike={vol_spike} | Session: {session}")

                # =====================================================
                # Filter and cooldown logic
                # =====================================================
                if score >= threshold:
			price = scored["price"]
			lot_size = calculate_lot_size(score, price)
			logger.info(f"📏 Position size based on score {score}/10 → Lot Size: {lot_size}")

                    if is_in_cooldown(pair):
                        logger.info(f"⏸️ Skipped {pair} (cooldown active)")
                        continue

                    logger.info(
                        f"🤖 Trade Confidence Score ({pair}): {score}/10 "
                        f"{scored['signal_strength']} | Price={scored['price']}"
                    )

                    update_trade_log(pair)

                    if dry_run:
                        logger.info("💤 DRYRUN mode active — no orders executed.")
                else:
                    logger.info(f"🚫 Ignored weak signal ({score}/10 < {threshold}) for {pair}")
                    continue

                time.sleep(5)

            except Exception as e:
                logger.error(f"❌ Error while processing {pair}: {e}")
                time.sleep(5)
                continue

        logger.info("🔁 Cycle complete. Sleeping 30s before next scan...\n")
        time.sleep(30)


if __name__ == "__main__":
    main()

