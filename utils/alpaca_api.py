import os, requests, time, logging

ALPACA_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://data.alpaca.markets/v2/stocks")

HEADERS = {
    "APCA-API-KEY-ID": ALPACA_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET
}

def normalize_symbol(pair):
    # Example: AAPL or TSLA or SPY
    return pair.split("/")[0] if "/" in pair else pair.upper()

def get_price(pair):
    """Fetch latest stock/ETF price from Alpaca"""
    try:
        symbol = normalize_symbol(pair)
        url = f"{ALPACA_BASE_URL}/{symbol}/quotes/latest"
        r = requests.get(url, headers=HEADERS, timeout=10)

        if r.status_code == 429:
            logging.warning("⏳ Alpaca rate limit hit, sleeping 5s...")
            time.sleep(5)
            return None

        r.raise_for_status()
        data = r.json()
        price = float(data["quote"]["ap"])
        logging.debug(f"Alpaca {symbol} → {price}")
        return {"price": price}
    except Exception as e:
        logging.error(f"❌ Alpaca get_price error: {e}")
    return None
def check_connection():
    return True  # Replace with real alpaca API ping later

