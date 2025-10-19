import json
from datetime import datetime
from os import getenv

START_BALANCE = float(getenv("STARTING_BALANCE", 1000))
today = datetime.utcnow().strftime("%Y-%m-%d")

reset_data = {
    "date": today,
    "trades": [],
    "balance": START_BALANCE
}

with open("logs/pnl_log.json", "w") as f:
    json.dump(reset_data, f, indent=2)

print("✅ PnL log reset.")
