# utils/adaptive_throttle.py
from datetime import datetime
import os

def get_adaptive_score_threshold(signal: dict, now_utc: datetime = None) -> float:
    """
    Adjusts score threshold dynamically based on volatility and time of day.
    Accepts the full signal dict for safety.
    """
    now = now_utc or datetime.utcnow()
    hour = now.hour

    base = float(os.getenv("BASE_SCORE_THRESHOLD", 6.0))
    min_score = float(os.getenv("ADAPTIVE_MIN_SCORE", 5.0))
    max_score = float(os.getenv("ADAPTIVE_MAX_SCORE", 8.0))
    asia_hours = os.getenv("ASIA_SESSION_HOURS", "0-7")
    vol_boost = float(os.getenv("VOL_SPIKE_BOOST", 1.3))

    # --- pull volatility safely ---
    vol_spike = signal.get("volume_spike", 1.0)
    if isinstance(vol_spike, dict):
        # unwrap dict form like {"value": 1.12}
        vol_spike = next(iter(vol_spike.values()), 1.0)
    try:
        vol_spike = float(vol_spike)
    except Exception:
        vol_spike = 1.0

    # --- parse Asia range safely ---
    try:
        start, end = map(int, asia_hours.split("-"))
        asia_range = range(start, end + 1)
    except Exception:
        asia_range = range(0, 8)

    score = base
    if vol_spike > vol_boost:
        score -= 0.5
    if hour in asia_range:
        score += 1.0

    score = max(min_score, min(score, max_score))
    return round(score, 2)

# backward compatible alias
get_adaptive_threshold = get_adaptive_score_threshold

