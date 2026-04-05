# utils/kill_switch.py

import os
import logging

logger = logging.getLogger(__name__)

def check_kill_switch() -> bool:
    """
    Checks if the kill switch flag file exists.
    If yes, disables trading.
    """
    flag_path = os.getenv("KILL_SWITCH_PATH", "kill_switch.flag")
    if os.path.exists(flag_path):
        logger.warning("🛑 Kill switch detected! Aborting trading.")
        return True
    return False

def trigger_kill_switch(reason: str = "Triggered manually or by PnL guard"):
    """
    Triggers the kill switch by creating the flag file and logging the reason.
    """
    flag_path = os.getenv("KILL_SWITCH_PATH", "kill_switch.flag")
    with open(flag_path, "w") as f:
        f.write(reason)
    logger.critical(f"💀 Kill switch triggered: {reason}")
