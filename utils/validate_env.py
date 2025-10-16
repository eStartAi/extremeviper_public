#!/usr/bin/env python3
"""
Enhanced Environment Validator for ExtremeViper
✅ Supports alternate variable names (STOP_LOSS_PCT, TAKE_PROFIT_PCT, etc.)
"""

import os
from dotenv import load_dotenv

load_dotenv()

REQUIRED_VARS = [
    "DEFAULT_BROKER",
    "DRY_RUN",
    "KRAKEN_API_KEY",
    "KRAKEN_API_SECRET",
    "KRAKEN_BASE_URL",
    "DEFAULT_SL_PCT",
    "DEFAULT_TP_PCT",
    "DAILY_PROFIT_TARGET",
    "MAX_DAILY_LOSS",
    "MAX_CONSECUTIVE_LOSSES",
    "WATCHLIST",
    "WEBHOOK_SECRET",
    "LOG_LEVEL",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "ENABLE_TELEGRAM_ALERTS",
]

ALTERNATE_KEYS = {
    "DEFAULT_SL_PCT": ["STOP_LOSS_PCT"],
    "DEFAULT_TP_PCT": ["TAKE_PROFIT_PCT"],
    "MAX_DAILY_LOSS": ["MAX_DAILY_DRAWDOWN_PCT"],
    "RISK_PCT": ["RISK_PERCENT", "RISK_PER_TRADE"],
}

def validate_env():
    missing = []

    for var in REQUIRED_VARS:
        if os.getenv(var):
            continue

        alternates = ALTERNATE_KEYS.get(var, [])
        if any(os.getenv(alt) for alt in alternates):
            continue

        missing.append(var)

    if missing:
        print("❌ Missing required environment variables:\n")
        for m in missing:
            print(f" - {m}")
        print("\n🛑 Fix your .env file.")
        return False

    print("✅ Environment validated successfully!")
    return True

# Optional direct run mode for testing:
if __name__ == "__main__":
    validate_env()
