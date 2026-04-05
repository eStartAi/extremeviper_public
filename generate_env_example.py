# generate_env_example.py

import os

SENSITIVE_KEYS = [
    "API_KEY", "API_SECRET", "ACCESS_TOKEN", "WEBHOOK_SECRET",
    "KRAKEN_API_KEY", "KRAKEN_API_SECRET",
    "OANDA_API_KEY", "OANDA_ACCOUNT_ID",
    "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"
]

def sanitize_env(env_path=".env", output_path=".env.example"):
    if not os.path.exists(env_path):
        print(f"❌ File not found: {env_path}")
        return

    with open(env_path, "r") as f:
        lines = f.readlines()

    safe_lines = []
    for line in lines:
        if "=" not in line or line.strip().startswith("#"):
            safe_lines.append(line)
            continue

        key, val = line.strip().split("=", 1)
        if any(secret_key in key for secret_key in SENSITIVE_KEYS):
            safe_lines.append(f"{key}=YOUR_{key}_HERE\n")
        else:
            safe_lines.append(f"{key}={val}\n")

    with open(output_path, "w") as f:
        f.writelines(safe_lines)

    print(f"✅ Safe .env.example created at {output_path}")

if __name__ == "__main__":
    sanitize_env()

