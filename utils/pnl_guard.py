# utils/pnl_guard.py

import os
import json
import logging
from datetime import datetime
from utils.kill_switch import trigger_kill_switch

logger = logging.getLogger(__name__)

PNL_LOG_PATH = os.getenv("PNL_LOG_PATH", "logs/pnl_log.json")
DAILY_DRAWDOWN_LIMIT = float(os.getenv("MAX_DAILY_DRAWDOWN_PCT", 0.10))  # Default = 10%

def get_today_pnl_total() -> float:
    """
    Reads today's PnL from PNL_LOG_PATH and returns the net total.
    """
    if not os.path.exists(PNL_LOG_PATH):
        return 0.0

    today = datetime.utcnow().strftime("%Y-%m-%d")
    try:
        with open(PNL_LOG_PATH, "r") as f:
            data = json.load(f)
        today_entries = [entry for entry in data if entry.get("date") == today]
        return sum(entry.get("pnl", 0.0) for entry in today_entries)
    except Exception as e:
        logger.error(f"❌ Failed to read PnL log: {e}")
        return 0.0

def check_daily_pnl_limit():
    """
    Checks if today's cumulative PnL exceeds the daily drawdown limit.
    If yes, triggers the kill switch.
    """
    pnl_total = get_today_pnl_total()
    account_balance = float(os.getenv("ACCOUNT_BALANCE", 1000))  # Default fallback
    threshold = -abs(account_balance * DAILY_DRAWDOWN_LIMIT)

    logger.info(f"📊 PnL check → Today: {pnl_total:.2f}, Threshold: {threshold:.2f}")
    if pnl_total <= threshold:
        reason = f"📉 Daily PnL limit hit: {pnl_total:.2f} ≤ {threshold:.2f}"
        trigger_kill_switch(reason)
        return False

    return True
