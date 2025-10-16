#!/usr/bin/env python3
# ============================================================
# check_structure.py — Verifies ExtremeViper folder integrity
# ============================================================

import os
from pathlib import Path

# === Expected Folder Structure ===
EXPECTED_TREE = {
    "root": [
        ".env", ".env.example", "README.md", "requirements.txt",
        "bootstrap_extremeviper.sh", "manage_viper.sh",
        "LIVEmain.py", "DRYRUNmain.py", "main.py",
        "logs/", "brokers/", "core/", "utils/", "notify/",
        "services/", "backups/", ".venv/"
    ],
    "brokers": [
        "__init__.py", "oanda.py", "kraken.py", "alpaca.py", "tos.py", "get_broker.py"
    ],
    "core": [
        "order_executor.py", "risk_manager.py", "recovery.py", "trailing_stop.py"
    ],
    "utils": [
        "__init__.py", "safe_main_wrapper.py", "score_engine.py",
        "signal_fetcher.py", "validate_env.py", "trade_control_logger.py"
    ],
    "notify": [
        "__init__.py", "notify.py"
    ],
    "services": [
        "extremeviper-live.service", "extremeviper-dryrun.service"
    ],
    "logs": [],
    "backups": [],
}

OPTIONAL_ITEMS = {
    "dashboards/", "analytics/", "tests/", "data/"
}

# === Check Logic ===
BASE_DIR = Path(__file__).resolve().parent.parent

def check_path_exists(relative_path):
    return (BASE_DIR / relative_path).exists()

def main():
    print("🔎 Checking ExtremeViper structure...\n")
    missing = []
    for folder, items in EXPECTED_TREE.items():
        base = BASE_DIR if folder == "root" else BASE_DIR / folder
        for item in items:
            path = base / item
            if not path.exists():
                missing.append(str(path.relative_to(BASE_DIR)))

    if missing:
        print("❌ Missing or misplaced items:")
        for m in missing:
            print(f"   - {m}")
    else:
        print("✅ All required files and folders found!")

    # Optional items
    optional_missing = [x for x in OPTIONAL_ITEMS if not check_path_exists(x)]
    if optional_missing:
        print("\n🟨 Optional (recommended) folders not found:")
        for o in optional_missing:
            print(f"   - {o}")

    print("\n📁 Base Directory:", BASE_DIR)
    print("✅ Check complete.\n")

if __name__ == "__main__":
    main()
