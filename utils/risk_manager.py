import os
from decimal import Decimal
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

def calculate_trade_size(balance: float) -> float:
    pct = float(os.getenv("RISK_PCT", "0.10"))
    return round(balance * pct, 2)

def should_stop_trading(today_loss_pct: float, consecutive_losses: int) -> bool:
    max_dd = float(os.getenv("MAX_DAILY_DRAWDOWN_PCT", "0.10"))
    max_losses = int(os.getenv("MAX_CONSECUTIVE_LOSSES", "3"))
    if today_loss_pct >= max_dd:
        return True
    if consecutive_losses >= max_losses:
        return True
    if Path(os.getenv("KILL_FILE", "control/kill.flag")).exists():
        return True
    if Path(os.getenv("STOP_TODAY_FILE", "control/stop_today.flag")).exists():
        return True
    return False
