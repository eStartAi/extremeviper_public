# utils/safe_main_wrapper.py
# ✅ required by main.py

import time
import logging
import traceback
from functools import wraps

logger = logging.getLogger(__name__)

def safe_main(func):
    """
    Decorator that keeps the main loop running safely.
    Restarts after any crash or unexpected error with a short delay.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            try:
                func(*args, **kwargs)
            except KeyboardInterrupt:
                logger.info("🛑 Manual stop (Ctrl+C). Exiting gracefully.")
                break
            except Exception as e:
                logger.error(f"❌ Error: {e}. Restarting in 5s...")
                time.sleep(5)
    return wrapper

def run_safe(main_func):
    """
    Used by main.py to safely wrap and run its main() function once.
    """
    try:
        main_func()
    except Exception as e:
        logger.error("🛑 Unhandled Exception:")
        traceback.print_exc()
        # Optionally send Telegram alert, trigger kill switch, etc.
