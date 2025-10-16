# utils/test_oanda_key.py

import os
import requests
from dotenv import load_dotenv

# Load from .env automatically
load_dotenv(dotenv_path=".env")

OANDA_API_KEY = os.getenv("OANDA_API_KEY")
OANDA_BASE_URL = os.getenv("OANDA_BASE_URL", "https://api-fxpractice.oanda.com/v3")

if not OANDA_API_KEY:
    print("❌ OANDA_API_KEY not loaded from .env")
    exit(1)

headers = {
    "Authorization": f"Bearer {OANDA_API_KEY}"
}

url = f"{OANDA_BASE_URL}/accounts"

try:
    r = requests.get(url, headers=headers)
    print(f"🔗 Request URL: {url}")
    print(f"📡 Response Status: {r.status_code}")
    print("🧾 Response:", r.json())
except Exception as e:
    print("❌ Failed to connect:", str(e))

import os
import requests

OANDA_API_KEY = os.getenv("OANDA_API_KEY")
OANDA_BASE_URL = os.getenv("OANDA_BASE_URL", "https://api-fxpractice.oanda.com/v3")

if not OANDA_API_KEY:
    print("❌ OANDA_API_KEY not loaded from .env")
    exit(1)

headers = {
    "Authorization": f"Bearer {OANDA_API_KEY}"
}

url = f"{OANDA_BASE_URL}/accounts"

try:
    r = requests.get(url, headers=headers)
    print(f"🔗 Request URL: {url}")
    print(f"📡 Response Status: {r.status_code}")
    print("🧾 Response:", r.json())
except Exception as e:
    print("❌ Failed to connect:", str(e))
