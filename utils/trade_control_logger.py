import os
import json
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
LOG_PATH = Path("logs/trade_control.json")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

MIN_SCORE = float(os.getenv("MIN_SCORE_THRESHOLD", 7.0))
COOLDOWN = int(os.getenv("PAIR_COOLDOWN_SECONDS", 60))

# -----------------------------------------------------
# internal cache for quick lookup
# -----------------------------------------------------
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

def is_in_cooldown(pair: str) -> bool:
    """Return True if pair triggered within cooldown window."""
    now = time.time()
    last = _cache.get(pair, 0)
    if now - last < COOLDOWN:
        return True
    return False

def update_trade_log(pair: str):
    """Update last-trade time for a pair."""
    now = time.time()
    _cache[pair] = now
    data = _load_log()
    data[pair] = now
    _save_log(data)
    logger.info(f"⏱️ Cooldown started for {pair} ({COOLDOWN}s)")

def init_cache():
    """Load previous log at startup."""
    data = _load_log()
    _cache.update(data)
    logger.info(f"📒 Loaded {len(_cache)} trade cooldown records.")
import os
import json
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
LOG_PATH = Path("logs/trade_control.json")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

MIN_SCORE = float(os.getenv("MIN_SCORE_THRESHOLD", 7.0))
COOLDOWN = int(os.getenv("PAIR_COOLDOWN_SECONDS", 60))

# -----------------------------------------------------
# internal cache for quick lookup
# -----------------------------------------------------
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

def is_in_cooldown(pair: str) -> bool:
    """Return True if pair triggered within cooldown window."""
    now = time.time()
    last = _cache.get(pair, 0)
    if now - last < COOLDOWN:
        return True
    return False

def update_trade_log(pair: str):
    """Update last-trade time for a pair."""
    now = time.time()
    _cache[pair] = now
    data = _load_log()
    data[pair] = now
    _save_log(data)
    logger.info(f"⏱️ Cooldown started for {pair} ({COOLDOWN}s)")

def init_cache():
    """Load previous log at startup."""
    data = _load_log()
    _cache.update(data)
    logger.info(f"📒 Loaded {len(_cache)} trade cooldown records.")
