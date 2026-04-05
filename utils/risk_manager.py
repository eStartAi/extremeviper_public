import os
from decimal import Decimal
from dotenv import load_dotenv
from pathlib import Path
import logging

load_dotenv()

def calculate_trade_size(balance: float) -> float:
    """
    Calculate trade size based on balance and fixed RISK_PCT from .env.
    Used in account-based brokers like OANDA.
    """
    try:
        pct = float(os.getenv("RISK_PCT", "0.10"))
        return round(balance * pct, 2)
    except Exception as e:
        logging.error(f"❌ Error in calculate_trade_size: {e}")
        return 0.0


def calculate_lot_size(score_or_balance, broker_name=None) -> float:
    """
    Dynamically calculate lot size based on either:
    - Score (0–10) for signal strength [score-based mode]
    - Balance (float) for risk % [balance-based mode]

    Returns:
        float: lot size (Kraken-style) or units (OANDA-style)
    """
    try:
        # Try to use score-based mode if broker_name is provided
        if broker_name is not None:
            score = float(score_or_balance)
            base_size = 0.01
            multiplier = max(1, score / 5)

            if broker_name.lower() == "oanda":
                return round(1000 * multiplier)  # OANDA uses units
            else:
                return round(base_size * multiplier, 5)  # Kraken, Alpaca, etc.

        # Else default to balance-based mode (fallback)
        balance = float(score_or_balance)
        return calculate_trade_size(balance)

    except Exception as e:
        logging.error(f"❌ Error in calculate_lot_size: {e}")
        return 0.01  # Safe fallback


def should_stop_trading(today_loss_pct: float, consecutive_losses: int) -> bool:
    """
    Decide whether to stop trading based on daily drawdown,
    loss streaks, or control flags.
    """
    try:
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
    except Exception as e:
        logging.error(f"❌ Error in should_stop_trading: {e}")
        return True  # Default to safety: stop if uncertain



