import os
import json
import time
import logging
from datetime import datetime
from utils.telegram_service import send_telegram_message, set_kill_flag

logger = logging.getLogger(__name__)

# === Config & Paths ===
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Load limits from .env
MAX_DAILY_DRAWDOWN_PCT = float(os.getenv("MAX_DAILY_DRAWDOWN_PCT", 0.10))  # 10%
DAILY_PROFIT_TARGET_PCT = float(os.getenv("DAILY_PROFIT_TARGET_PCT", 0.20))  # 20%
ACCOUNT_BALANCE = float(os.getenv("ACCOUNT_BALANCE", 1000))  # base equity

PNL_FILE = os.path.join(LOG_DIR, f"pnl_{datetime.utcnow().strftime('%Y%m%d')}.json")


def _load_pnl():
    """Load existing PnL log or create a new one."""
    if not os.path.exists(PNL_FILE):
        return {"trades": [], "total_pnl": 0.0}
    try:
        with open(PNL_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"trades": [], "total_pnl": 0.0}


def _save_pnl(data):
    """Save PnL data safely to file."""
    with open(PNL_FILE, "w") as f:
        json.dump(data, f, indent=2)


def log_trade_result(pair: str, broker: str, profit_usd: float):
    """
    Append trade result to today's PnL file and check drawdown limits.
    profit_usd can be positive or negative.
    """
    data = _load_pnl()
    trade = {
        "timestamp": datetime.utcnow().isoformat(),
        "pair": pair,
        "broker": broker,
        "profit_usd": profit_usd,
    }
    data["trades"].append(trade)
    data["total_pnl"] = round(sum(t["profit_usd"] for t in data["trades"]), 2)
    _save_pnl(data)

    logger.info(
        f"💰 Recorded {profit_usd:+.2f} USD for {pair} ({broker}). "
        f"Total={data['total_pnl']:.2f}"
    )

    # Evaluate drawdown/profit limits
    check_pnl_limits(data["total_pnl"])


def check_pnl_limits(total_pnl: float):
    """Stop trading if daily drawdown or profit target reached."""
    drawdown_limit = -ACCOUNT_BALANCE * MAX_DAILY_DRAWDOWN_PCT
    profit_target = ACCOUNT_BALANCE * DAILY_PROFIT_TARGET_PCT

    if total_pnl <= drawdown_limit:
        msg = (
            f"🛑 Daily loss limit hit ({total_pnl:.2f} USD ≤ "
            f"{drawdown_limit:.2f}). Bot stopped."
        )
        logger.warning(msg)
        send_telegram_message(msg)
        set_kill_flag()

    elif total_pnl >= profit_target:
        msg = (
            f"🏁 Daily profit target reached ({total_pnl:.2f} USD ≥ "
            f"{profit_target:.2f}). Bot stopped to lock profits."
        )
        logger.info(msg)
        send_telegram_message(msg)
        set_kill_flag()


def reset_daily_pnl():
    """Reset daily PnL log at midnight or on command."""
    global PNL_FILE
    PNL_FILE = os.path.join(LOG_DIR, f"pnl_{datetime.utcnow().strftime('%Y%m%d')}.json")
    if os.path.exists(PNL_FILE):
        os.remove(PNL_FILE)
    _save_pnl({"trades": [], "total_pnl": 0.0})
    logger.info("🔄 Daily PnL log reset.")
