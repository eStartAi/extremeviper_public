import os, requests, time, logging

OANDA_API_TOKEN = os.getenv("OANDA_API_TOKEN")
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
OANDA_ENV = os.getenv("OANDA_ENV", "practice")

BASE_URL = "https://api-fxpractice.oanda.com/v3" if OANDA_ENV == "practice" else "https://api-fxtrade.oanda.com/v3"
HEADERS = {"Authorization": f"Bearer {OANDA_API_TOKEN}"}

def get_price(pair):
    """Fetch latest price from OANDA safely"""
    try:
        pair_fmt = pair.replace("/", "_")
        url = f"{BASE_URL}/accounts/{OANDA_ACCOUNT_ID}/pricing?instruments={pair_fmt}"
        r = requests.get(url, headers=HEADERS, timeout=10)

        if r.status_code == 429:
            logging.warning("⏳ OANDA rate limit hit, sleeping 5s...")
            time.sleep(5)
            return None

        r.raise_for_status()
        data = r.json()

        if "prices" in data and len(data["prices"]) > 0:
            price = float(data["prices"][0]["bids"][0]["price"])
            logging.debug(f"OANDA {pair} → {price}")
            return {"price": price}
    except Exception as e:
        logging.error(f"❌ OANDA get_price error: {e}")
    return None
def check_connection():
    return True  # Replace with real OANDA API ping later
