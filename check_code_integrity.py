#!/usr/bin/env python3

import os
import ast
import time
import traceback
from dotenv import dotenv_values

REQUIRED_FILES = [
    "main.py", ".env", "utils", "brokers", "core", "notify"
]

REQUIRED_ENV_VARS = [
    "WEBHOOK_SECRET", "RISK_PCT", "TAKE_PROFIT_PCT", "STOP_LOSS_PCT", "MAX_DAILY_DRAWDOWN_PCT"
]

ROOT = os.path.abspath(os.path.dirname(__file__))
failures = []

def check_required_files():
    print("📂 Checking required files/folders...")
    for path in REQUIRED_FILES:
        full_path = os.path.join(ROOT, path)
        if not os.path.exists(full_path):
            print(f"❌ Missing: {path}")
            failures.append(f"Missing file or folder: {path}")
        else:
            print(f"✅ Found: {path}")

def check_env_vars():
    print("\n🔐 Checking required environment variables...")
    env_path = os.path.join(ROOT, ".env")
    if not os.path.exists(env_path):
        print("❌ .env file not found.")
        failures.append(".env file missing.")
        return
    env = dotenv_values(env_path)
    for key in REQUIRED_ENV_VARS:
        if key not in env:
            print(f"❌ Missing in .env: {key}")
            failures.append(f".env variable missing: {key}")
        else:
            print(f"✅ Found: {key}")

def safe_ast_parse(file_path):
    try:
        with open(file_path, "r") as f:
            source = f.read()
        ast.parse(source, filename=file_path)
        return True
    except Exception as e:
        print(f"❌ AST parse failed: {file_path} → {e}")
        failures.append(f"Parse error in {file_path}")
        return False

def check_py_files():
    print("\n🧠 Scanning Python files for syntax errors...")
    for root, dirs, files in os.walk(ROOT):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                safe_ast_parse(full_path)

if __name__ == "__main__":
    print("🛠️  Running ExtremeViper Integrity Check...\n")
    check_required_files()
    check_env_vars()
    check_py_files()

    print("\n🧾 Summary:")
    if failures:
        print(f"❌ {len(failures)} issues found:")
        for f in failures:
            print(f"   - {f}")
        exit(1)
    else:
        print("✅ All checks passed successfully.")
