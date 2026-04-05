#!/usr/bin/env python3
# =====================================================
# 🧠 ExtremeViper Broker Audit Tool
# Purpose: Verify all broker modules implement core methods
# =====================================================

import importlib
import inspect
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("broker_audit")

# Define the expected functions every broker must implement
REQUIRED_FUNCS = ["fetch_candles", "get_price", "place_order", "ping", "get_balance"]

BROKERS_PATH = os.path.join(os.path.dirname(__file__), "..", "brokers")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def audit_broker(broker_name):
    """Import broker module and verify core functions exist."""
    try:
        module = importlib.import_module(f"brokers.{broker_name}")
        funcs = [name for name, obj in inspect.getmembers(module, inspect.isfunction)]

        missing = [f for f in REQUIRED_FUNCS if f not in funcs]
        if missing:
            logger.warning(f"⚠️ {broker_name.upper()}: Missing functions → {', '.join(missing)}")
        else:
            logger.info(f"✅ {broker_name.upper()}: All core functions OK")
        return missing
    except Exception as e:
        logger.error(f"💥 Failed to import {broker_name}: {e}")
        return REQUIRED_FUNCS


def main():
    logger.info("🔍 Running ExtremeViper Broker Audit...\n")
    brokers = [f.replace(".py", "") for f in os.listdir(BROKERS_PATH)
               if f.endswith(".py") and f not in ("__init__.py", "get_broker.py")]

    all_missing = {}
    for b in brokers:
        missing = audit_broker(b)
        if missing:
            all_missing[b] = missing

    logger.info("\n---------------------------------------------")
    if all_missing:
        logger.warning("⚠️ Audit completed with missing definitions:")
        for b, funcs in all_missing.items():
            logger.warning(f"  • {b}: {', '.join(funcs)}")
    else:
        logger.info("✅ All broker modules pass the audit check!")
    logger.info("---------------------------------------------")


if __name__ == "__main__":
    main()
