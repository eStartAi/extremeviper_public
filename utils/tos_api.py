import os
import logging
import requests
import json
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

# === Load OAuth2 Config ===
CLIENT_ID = os.getenv("TOS_CLIENT_ID")             # e.g. 7tJdlgAfSKX32YdSmgDBIlF4nowc4ALc5A1db6OXqDLA2EJy
CLIENT_SECRET = os.getenv("TOS_CLIENT_SECRET")     # optional for confidential apps
REDIRECT_URI = os.getenv("TOS_REDIRECT_URI")       # e.g. https://yourdomain.com/callback
REFRESH_TOKEN = os.getenv("TOS_REFRESH_TOKEN")
TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"
API_BASE_URL = "https://api.schwabapi.com/v1"

# === Token Management ===
def get_access_token():
    try:
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
            "client_id": f"{CLIENT_ID}@AMER.OAUTHAP",
        }
        if CLIENT_SECRET:
            payload["client_secret"] = CLIENT_SECRET

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        resp = requests.post(TOKEN_URL, data=payload, headers=headers)
        resp.raise_for_status()
        token = resp.json()["access_token"]
        return token

    except Exception as e:
        logger.error(f"❌ Failed to refresh Schwab access token: {e}")
        return None

# === Connection Check ===
def check_connection():
    try:
        token = get_access_token()
        if not token:
            return False

        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{API_BASE_URL}/userprincipals", headers=headers)
        return resp.status_code == 200

    except Exception as e:
        logger.warning(f"⚠️ TOS ping error: {e}")
        return False

# === Get Account Balance ===
def get_balance():
    try:
        token = get_access_token()
        if not token:
            raise Exception("Access token missing")

        ACCOUNT_ID = os.getenv("TOS_ACCOUNT_ID")
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{API_BASE_URL}/accounts/{ACCOUNT_ID}?fields=positions"
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        balance = float(data[0]["securitiesAccount"]["currentBalances"]["liquidationValue"])
        return balance

    except Exception as e:
        logger.error(f"❌ Failed to fetch TOS balance: {e}")
        return float(os.getenv("DEFAULT_BALANCE", 1000))

# === Place Market Order ===
def place_order(symbol, qty, side, sl=None, tp=None, score=None):
    try:
        token = get_access_token()
        if not token:
            raise Exception("Access token missing")

        ACCOUNT_ID = os.getenv("TOS_ACCOUNT_ID")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        order = {
            "orderType": "MARKET",
            "session": "NORMAL",
            "duration": "DAY",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                    "instruction": "BUY" if side.lower() == "buy" else "SELL",
                    "quantity": float(qty),
                    "instrument": {
                        "symbol": symbol,
                        "assetType": "EQUITY"  # Update if you use options/futures/etc
                    }
                }
            ]
        }

        url = f"{API_BASE_URL}/accounts/{ACCOUNT_ID}/orders"
        resp = requests.post(url, headers=headers, json=order)

        if not resp.ok:
            logger.error(f"💥 TOS Order Error: {resp.status_code} {resp.text}")
            return None

        logger.info(f"✅ TOS Order Placed: {side.upper()} {qty} {symbol} | Score={score}/10")
        return resp.json()

    except Exception as e:
        logger.error(f"💥 Unexpected TOS order error: {e}")
        return None

