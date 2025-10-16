import os, requests, time, logging

TOS_API_KEY = os.getenv("TOS_API_KEY")  # TD developer API key
TOS_BASE_URL = os.getenv("TOS_BASE_URL", "https://api.tdameritrade.com/v1/marketdata")

def get_price(pair):
    """Fetch latest quote from ThinkorSwim (TD Ameritrade API)"""
    try:
        symbol = pair.split("/")[0] if "/" in pair else pair.upper()
        params = {"apikey": TOS_API_KEY}
        r = requests.get(f"{TOS_BASE_URL}/{symbol}/quotes", params=params, timeout=10)

        if r.status_code == 429:
            logging.warning("⏳ TD Ameritrade rate limit hit, sleeping 5s...")
            time.sleep(5)
            return None

        r.raise_for_status()
        data = r.json()
        quote = data.get(symbol, {})
        price = quote.get("lastPrice") or quote.get("mark") or 0
        if price:
            logging.debug(f"TOS {symbol} → {price}")
            return {"price": float(price)}
    except Exception as e:
        logging.error(f"❌ TOS get_price error: {e}")
    return None
def check_connection():
    return True  # Replace with real tos API ping later
