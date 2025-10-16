# utils/adaptive_throttle.py

from datetime import datetime
import os

def get_adaptive_score_threshold(vol_spike: float, now_utc: datetime = None) -> float:
    """
    Dynamically adjusts the score threshold based on volatility and time of day.
    """
    now = now_utc or datetime.utcnow()
    hour = now.hour

    base = float(os.getenv("BASE_SCORE_THRESHOLD", 6.0))
    min_score = float(os.getenv("ADAPTIVE_MIN_SCORE", 5.0))
    max_score = float(os.getenv("ADAPTIVE_MAX_SCORE", 8.0))
    asia_hours = os.getenv("ASIA_SESSION_HOURS", "0-7")
    vol_boost = float(os.getenv("VOL_SPIKE_BOOST", 1.3))

    # Parse Asia hours range like "0-7" → range(0, 7)
    parts = list(map(int, asia_hours.split("-")))
    asia_range = range(parts[0], parts[1] + 1)

    score = base

    # Lower threshold if high volatility
    if vol_spike > vol_boost:
        score -= 0.5

    # Raise threshold during Asia session
    if hour in asia_range:
        score += 1.0

    # Clamp to min/max range
    score = max(min_score, min(score, max_score))
    return round(score, 2)
