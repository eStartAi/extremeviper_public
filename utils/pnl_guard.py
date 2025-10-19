# utils/pnl_guard.py

import os
import json
from datetime import datetime
from utils.kill_switch import trigger_kill_switch

PNL_LOG_PATH = "logs/pnl_log.json"
MAX_DRAW_PCT = float(os.getenv("MAX_DAILY_DRAWDOWN_PCT", 0.10))
MAX_LOSSES = int(os.getenv("MAX_CONSECUTIVE_LOSSES", 3))
START_BALANCE = float(os.getenv("STARTING_BALANCE", 1000))  # Required in .env

def _load_log():
    if not os.path.exists(PNL_LOG_PATH):
        return {"date": "", "trades": [], "balance": START_BALANCE}
    with open(PNL_LOG_PATH, "r") as f:
        return json.load(f)

def _save_log(data):
    with open(PNL_LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def log_trade(profit_pct):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    data = _load_log()

    if data["date"] != today:
        data = {"date": today, "trades": [], "balance": START_BALANCE}

    data["trades"].append(profit_pct)
    data["balance"] *= (1 + profit_pct)
    _save_log(data)
    check_limits(data)

def check_limits(data=None):
    if data is None:
        data = _load_log()

    pnl_today = data["balance"] - START_BALANCE
    drawdown_pct = abs(pnl_today / START_BALANCE)

    # Consecutive loss check
    losses = 0
    for result in reversed(data["trades"]):
        if result < 0:
            losses += 1
        else:
            break

    if drawdown_pct >= MAX_DRAW_PCT:
        print("🛑 Max daily drawdown hit. Triggering kill-switch.")
        trigger_kill_switch("Drawdown Limit Exceeded")

    elif losses >= MAX_LOSSES:
        print("🛑 Max consecutive losses hit. Triggering kill-switch.")
        trigger_kill_switch("Consecutive Losses Exceeded")
