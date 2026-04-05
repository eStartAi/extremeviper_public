import logging, time
log = logging.getLogger(__name__)

def safe_restart(main_func, delay=5):
    while True:
        try:
            main_func()
        except Exception as e:
            log.error(f"⚠️ Crash detected: {e}. Restarting in {delay}s...")
            time.sleep(delay)
