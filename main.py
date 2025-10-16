import os
import sys
import time
#!/usr/bin/env python3
# ============================================================
# ExtremeViper Main Controller (Hyper-Scalping Simulation)
# ============================================================

import os
import sys
import time
import threading
import logging
import random
from dotenv import load_dotenv

from broker import get_broker
from core.order_executor import execute_order
from core.risk_manager import (
    can_trade,
    can_trade_pair,
    check_daily_drawdown,
    init_daily_balance,
    record_trade_result
)
from notify.notify import send_telegram
from utils.safe_main_wrapper import run_safe
from utils.score_engine import score_trade   # ← import your scoring logic

# === Initial Setup ===
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/extremeviper.log", mode="a")
    ]
)
logger = logging.getLogger(__name__)

# === Config ===
run_mode = os.getenv("RUN_MODE", "dryrun").lower()
monitor_interval = int(os.getenv("MONITOR_INTERVAL", "60"))
max_failures = int(os.getenv("MAX_BROKER_FAILURES", "3"))
enable_telegram = os.getenv("ENABLE_TELEGRAM_ALERTS", "false").lower() == "true"
broker_name = sys.argv[1] if len(sys.argv) > 1 else os.getenv("DEFAULT_BROKER", "oanda")

# === Broker Load ===
broker = get_broker(broker_name)
logger.info(f"🔄 Broker module loaded: {broker_name}")
logger.info(f"🚀 ExtremeViper started | Broker={broker_name} | DRY_RUN={run_mode.upper() != 'LIVE'}")

# === Kill Switch (Always On) ===
def kill_switch_monitor():
    while True:
        if os.path.exists(".kill_extremeviper"):
            logger.critical("🛑 Kill switch file detected! Shutting down.")
            if enable_telegram:
                send_telegram("🛑 Kill switch triggered — ExtremeViper shutting down.")
            sys.exit(1)
        time.sleep(5)

threading.Thread(target=kill_switch_monitor, daemon=True).start()

# === Broker Heartbeat + Auto-Fallback ===
failure_count = 0
def broker_heartbeat():
    global failure_count, run_mode
    while True:
        try:
            if broker.ping():
                logger.info("✅ Broker heartbeat OK")
                failure_count = 0
            else:
                raise Exception("❌ Broker ping failed.")
        except Exception as e:
            failure_count += 1
            logger.warning(f"⚠️ Broker failure {failure_count}/{max_failures}: {e}")
            if failure_count >= max_failures:
                if run_mode == "live":
                    logger.critical("🛑 Too many failures — switching to DRY_RUN.")
                    run_mode = "dryrun"
                    if enable_telegram:
                        send_telegram("🛑 Broker down — switched to DRY_RUN mode.")
        time.sleep(monitor_interval)

threading.Thread(target=broker_heartbeat, daemon=True).start()

# === Mock Signal Generator ===
def generate_mock_signal():
    """Simulates RSI, MACD, EMA slope & Volume spike for testing."""
    rsi = random.uniform(20, 80)
    macd_hist = random.uniform(-0.003, 0.003)
    ema_slope = random.uniform(-0.15, 0.15)
    volume_spike = random.choice([True, False, False])  # 33% chance
    return {
        "rsi": rsi,
        "macd_hist": macd_hist,
        "ema_slope": ema_slope,
        "volume_spike": volume_spike,
    }

# === Core Trading Loop ===
def main():
    balance = broker.get_balance()
    init_daily_balance(balance)

    while True:
        try:
            # --- Generate mock trade data ---
            signal = generate_mock_signal()
            score = score_trade(signal)
            pair = random.choice(["EUR/USD", "BTC/USD", "ETH/USD", "XAU/USD"])
            side = "buy" if signal["rsi"] < 50 else "sell"
            price = broker.get_price(pair)
            tp = price * (1.002 if side == "buy" else 0.998)
            sl = price * (0.998 if side == "buy" else 1.002)

            logger.info(
                f"📊 Signal: RSI={signal['rsi']:.2f} | MACD={signal['macd_hist']:.4f} | "
                f"EMA={signal['ema_slope']:.3f} | VolSpike={signal['volume_spike']} | Score={score}"
            )

            # --- Risk & Safety Filters ---
            if not can_trade():
                time.sleep(3)
                continue
            if not can_trade_pair(pair):
                time.sleep(3)
                continue
            if not check_daily_drawdown(balance):
                logger.critical("🚫 Daily drawdown limit hit — stopping trading.")
                break

            # --- Execute Order (Simulated if DRY_RUN) ---
            order = execute_order(broker, pair, side, price, score, tp, sl, balance)
            if order:
                msg = f"✅ Sim Trade: {side.upper()} {pair} | Score={score:.1f}/10"
                logger.info(msg)
                if enable_telegram:
                    send_telegram(msg)
            else:
                logger.warning(f"⚠️ Trade skipped or failed: {pair}")

            # --- Balance & Result Tracking ---
            new_balance = broker.get_balance()
            record_trade_result(new_balance, balance)
            balance = new_balance

            time.sleep(10)  # ← hyper-scalping loop cycle

        except KeyboardInterrupt:
            logger.warning("🟡 Manual stop detected (CTRL+C).")
            break
        except Exception as e:
            logger.error(f"❌ Exception in main loop: {e}")
            time.sleep(5)

# === Self-Healing Entry ===
if __name__ == "__main__":
    run_safe(main, bot_name=f"ExtremeViper-{broker_name}")