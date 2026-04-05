import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# =====================================================
# 🔧 Config
# =====================================================
LOG_PATH = Path("logs/trade_control.json")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

LOG_FILE = Path("logs/trade_log.json")
MAX_TRADES_PER_HOUR = int(os.getenv("MAX_TRADES_PER_HOUR", 25))
MIN_SCORE = float(os.getenv("MIN_SCORE_THRESHOLD", 7.0))
COOLDOWN = int(os.getenv("PAIR_COOLDOWN_SECONDS", 60))

# Internal in-memory cache
_cache = {}
_throttle = {}  # broker: [timestamps]


# =====================================================
# 🔁 JSON Helpers
# =====================================================
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


# =====================================================
# ⏱️ Cooldown + Duplicate Detection
# =====================================================
def is_in_cooldown(pair: str, broker: str = "") -> bool:
    """Return True if pair is still in cooldown window."""
    key = f"{broker}:{pair}" if broker else pair
    now = time.time()
    last = _cache.get(key, 0)
    return now - last < COOLDOWN

def is_duplicate(pair: str, broker: str = "") -> bool:
    """Return True if same pair+broker traded in same minute."""
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


# =====================================================
# 🧠 Throttle: Limit total trades/hour
# =====================================================
def can_trade(broker: str) -> bool:
    """Return False if broker exceeded trades/hour limit."""
    now = time.time()
    one_hour_ago = now - 3600

    if broker not in _throttle:
        _throttle[broker] = []

    # Purge old timestamps
    _throttle[broker] = [t for t in _throttle[broker] if t > one_hour_ago]

    if len(_throttle[broker]) >= MAX_TRADES_PER_HOUR:
        logger.warning(f"[Throttle] Max {MAX_TRADES_PER_HOUR}/hour reached.")
        return False

    _throttle[broker].append(now)
    return True


# =====================================================
# 📒 Persistent Cache Init
# =====================================================
def init_cache():
    """Load cooldown + throttle history into memory."""
    data = _load_log()
    _cache.update(data)
    logger.info(f"📒 Loaded {len(_cache)} trade cooldown records.")


# =====================================================
# 🕒 Get last success time (for smart router)
# =====================================================
def get_last_success_time(pair: str, broker_name: str) -> float:
    """
    Return last trade timestamp (epoch) for given broker/pair.
    """
    if not LOG_FILE.exists():
        return 0
    try:
        with open(LOG_FILE, "r") as f:
            log_data = json.load(f)

        entries = log_data.get(broker_name.lower(), {}).get(pair.upper(), [])
        if entries:
            last_entry = entries[-1]
            return float(last_entry.get("timestamp", 0))
    except Exception:
        return 0
    return 0
