import subprocess
import os

# === Define which brokers to launch ===
enabled_brokers = os.getenv("ENABLED_BROKERS", "kraken,oanda").split(",")

# === Path to Python script
python_exec = "python3"
main_script = "main.py"

print("🚀 Launching bots for:", ", ".join(enabled_brokers))

for broker in enabled_brokers:
    broker = broker.strip()
    print(f"🔁 Starting bot for: {broker.upper()}")

    subprocess.Popen(
        [python_exec, main_script, broker],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

print("✅ All broker bots launched in background.")
print("📍 Check logs or systemd for status.")
