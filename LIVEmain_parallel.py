# LIVEmain_parallel.py

import os
import time
import logging
from rich.table import Table
from rich.console import Console
from dotenv import load_dotenv
from utils.validate_env import validate_env   # ✅ correct path
from utils.pnl_guard import check_daily_pnl_limit
from utils.signal_fetcher import fetch_signal
from utils.telegram_service import start_telegram_listener
from utils.broker_selector import get_smart_broker
from utils.order_executor import execute_trade
from utils.score_engine import MIN_SCORE_THRESHOLD

# === Setup ===
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
ENABLED_PAIRS = [
    "BTC/USD", "ETH/USD", "EUR/USD", "GBP/USD"
]  # or import from pairmap if desired

# === Main Bot Loop ===
def main():
    logger.warning("🟢 ExtremeViper Parallel LIVE Mode started.")
    if not validate_env():
        logger.error("❌ .env validation failed.")
        return

    start_telegram_listener()
    console.print("✅ Environment validated successfully!")

    while True:
        if not check__daily_pnl_limit():
            logger.warning("🔴 Daily PnL limit breached. Trading paused.")
            time.sleep(300)
            continue

        rows = []

        for pair in ENABLED_PAIRS:
            try:
                broker = get_smart_broker(pair)
                signal_data = fetch_signal(pair, broker)

                if not signal_data:
                    rows.append([pair, broker, "-", "❌ No Signal", "-"])
                    continue

                score = signal_data["score"]
                signal = signal_data["signal"]

                if score >= MIN_SCORE_THRESHOLD:
                    result = execute_trade(pair, broker, signal, score, dry_run=DRY_RUN)
                    status = "✅ Executed" if not DRY_RUN else "🟡 Simulated"
                    rows.append([pair, broker, f"{score:.2f}", status, signal["side"].upper()])
                else:
                    rows.append([pair, broker, f"{score:.2f}", "🚫 Ignored", "-"])

            except Exception as e:
                logger.exception(f"⚠️ Error for {pair}: {e}")
                rows.append([pair, "?", "-", "💥 Error", "-"])

        show_table(rows)
        logger.info("INFO:__main__:Waiting for next cycle...\n")
        time.sleep(60)

# === Table Output ===
def show_table(rows):
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("PAIR")
    table.add_column("BROKER")
    table.add_column("SCORE")
    table.add_column("STATUS")
    table.add_column("INFO")

    for row in rows:
        table.add_row(*row)

    console.print(table)

# === Entry Point ===
if __name__ == "__main__":
    main()
