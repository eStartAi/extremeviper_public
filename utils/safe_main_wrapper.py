import time
import logging
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
