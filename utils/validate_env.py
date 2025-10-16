#!/usr/bin/env python3
"""
Enhanced Environment Validator for ExtremeViper
✅ Backward compatible: supports both old (DEFAULT_SL_PCT) and new (STOP_LOSS_PCT) naming
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Core required variables (canonical names) ---
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

# --- Backward-compatibility mapping ---
ALTERNATE_KEYS = {
    "DEFAULT_SL_PCT": ["STOP_LOSS_PCT"],
    "DEFAULT_TP_PCT": ["TAKE_PROFIT_PCT"],
    "MAX_DAILY_LOSS": ["MAX_DAILY_DRAWDOWN_PCT"],
    # Optionally also accept generic risk sizing keys
    "RISK_PCT": ["RISK_PERCENT", "RISK_PER_TRADE"],
}

missing = []

for var in REQUIRED_VARS:
    # check if canonical var exists
    if os.getenv(var):
        continue

    # check alternates
    alternates = ALTERNATE_KEYS.get(var, [])
    if any(os.getenv(alt) for alt in alternates):
        continue

    # mark missing
    missing.append(var)

if missing:
    print("❌ Missing required environment variables:\n")
    for m in missing:
        print(f" - {m}")
    print("\n🛑 Fix your .env file.")
    exit(1)

print("✅ Environment validated successfully!")

