#!/usr/bin/env python3
# ============================================================
# generate_env_example.py — Strip secrets or redact placeholders for .env.example
# ============================================================

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
env_path = BASE / ".env"
example_path = BASE / ".env.example"

EXCLUDE_KEYWORDS = ["SECRET", "TOKEN", "KEY", "PASSWORD", "PRIVATE", "BEARER"]

def is_sensitive(key):
    return any(term in key.upper() for term in EXCLUDE_KEYWORDS)

def sanitize_line(line, safe_mode=False):
    if "=" not in line or line.strip().startswith("#"):
        return line.strip()

    key, value = line.split("=", 1)
    key = key.strip()

    if safe_mode and is_sensitive(key):
        return f"# {key}=🔒 OMITTED FOR SAFETY"
    return f"{key}=your_{key.lower()}_here"

def main():
    safe_mode = "--safe" in sys.argv
    if not env_path.exists():
        print("❌ .env file not found.")
        return

    with open(env_path) as f:
        lines = f.readlines()

    sanitized = [sanitize_line(line, safe_mode=safe_mode) for line in lines]
    example_path.write_text("\n".join(sanitized) + "\n")

    mode_msg = "🔐 SAFE MODE" if safe_mode else "default"
    print(f"✅ .env.example generated ({len(sanitized)} entries) using {mode_msg}")

if __name__ == "__main__":
    main()
