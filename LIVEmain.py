#!/usr/bin/env python3
# ============================================================
# ExtremeViper (LIVE Mode)
# Executes actual trades via broker API
# ============================================================

import os, sys, time, threading, logging
from dotenv import load_dotenv
from broker import get_broker
from core.order_executor import execute_order
from core.risk_manager import can_trade, can_trade_pair, check_daily_drawdown, init_daily_balance, record_trade_result
from notify.notify import send_telegram
from utils.safe_main_wrapper import run_safe
from utils.signal_fetcher import fetch_live_signal  # ← live scanner you’ll build next
from utils.score_engine import score_trade

# === Setup ===
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("logs/extremeviper_live.log", mode="a")])
logger = logging.getLogger(__name__)

enable_telegram = os.getenv("ENABLE_TELEGRAM_ALERTS", "false").lower() == "true"
broker_name = os.getenv("DEFAULT_BROKER", "oanda")
broker = get_broker(broker_name)

logger.info("🚀 ExtremeViper LIVE mode engaged — real trades enabled!")

def main():
    balance = broker.get_balance()
    init_daily_balance(balance)
    while True:
        try:
            data = fetch_live_signal(broker)  # ← your real signal logic
            score = score_trade(data)
            pair, side, price, tp, sl = data["pair"], data["side"], data["price"], data["tp"], data["sl"]

            logger.info(f"📊 LiveSignal {pair} | Score={score:.1f}")

            if not can_trade() or not can_trade_pair(pair) or not check_daily_drawdown(balance):
                time.sleep(5); continue

            order = execute_order(broker, pair, side, price, score, tp, sl, balance)
            if order and enable_telegram:
                send_telegram(f"✅ LIVE {side.upper()} {pair} | Score={score:.1f}")

            new_balance = broker.get_balance()
            record_trade_result(new_balance, balance)
            balance = new_balance
            time.sleep(5)  # hyper-scalping loop

        except KeyboardInterrupt:
            logger.warning("🟡 Manual stop detected.")
            break
        except Exception as e:
            logger.error(f"❌ Exception in main loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_safe(main, bot_name=f"ExtremeViper-LIVE-{broker_name}")