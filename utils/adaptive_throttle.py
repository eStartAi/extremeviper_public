from utils.timeframe import TIMEFRAME_MINUTES

def get_adaptive_score_threshold(signal: dict) -> float:
    """
    Dynamically adjust score threshold based on volume spike, time of day, and other metrics.
    """
    vol = signal.get("volume_spike", 1.0)
    hour = int(signal.get("timestamp", 0)) % 24 if signal.get("timestamp") else 0
    base = 5.5

    if vol > 2.0:
        base -= 0.2
    if 7 <= hour <= 11 or 13 <= hour <= 16:
        base -= 0.2

    base = max(3.5, min(base, 7.5))
    return round(base, 2)
