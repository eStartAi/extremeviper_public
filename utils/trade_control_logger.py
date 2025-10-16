import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)
LOG_PATH = Path("logs/trade_control.json")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

MIN_SCORE = float(os.getenv("MIN_SCORE_THRESHOLD", 7.0))
COOLDOWN = int(os.getenv("PAIR_COOLDOWN_SECONDS", 60))

# Internal memory cache
_cache = {}

def _load_log():
    if LOG_PATH.exists():
        try:
            with open(LOG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_log(data):
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def is_in_cooldown(pair: str, broker: str = "") -> bool:
    """Return True if pair is still in cooldown window."""
    key = f"{broker}:{pair}" if broker else pair
    now = time.time()
    last = _cache.get(key, 0)
    return now - last < COOLDOWN

def is_duplicate(pair: str, broker: str = "") -> bool:
    """Return True if same pair+broker was traded in same minute."""
    key = f"{broker}:{pair}" if broker else pair
    last_ts = _cache.get(key, 0)
    if not last_ts:
        return False

    now = datetime.utcnow().replace(second=0, microsecond=0)
    last = datetime.utcfromtimestamp(last_ts).replace(second=0, microsecond=0)
    return now == last

def update_trade_log(pair: str, broker: str = ""):
    """Log current trade time for cooldown + duplicate tracking."""
    key = f"{broker}:{pair}" if broker else pair
    now = time.time()
    _cache[key] = now
    data = _load_log()
    data[key] = now
    _save_log(data)
    logger.info(f"⏱️ Cooldown started for {key} ({COOLDOWN}s)")

def init_cache():
    """Load cooldown history into memory."""
    data = _load_log()
    _cache.update(data)
    logger.info(f"📒 Loaded {len(_cache)} trade cooldown records.")

