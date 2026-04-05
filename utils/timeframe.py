# utils/timeframe.py
import os

def parse_timeframe(raw: str) -> str:
    raw = str(raw).strip().upper()
    if raw.startswith("M") or raw.startswith("H"):
        return raw
    return f"M{raw}"

def parse_timeframe_minutes(raw: str) -> int:
    raw = str(raw).strip().upper()
    if raw.startswith("M"):
        return int(raw[1:])
    elif raw.startswith("H"):
        return int(raw[1:]) * 60
    return int(raw)

# Global constants
TIMEFRAME = parse_timeframe(os.getenv("TIMEFRAME", "5"))
TIMEFRAME_MINUTES = parse_timeframe_minutes(os.getenv("TIMEFRAME", "5"))
