import os, requests, time, logging

KRAKEN_BASE_URL = os.getenv("KRAKEN_BASE_URL", "https://api.kraken.com/0/public/Ticker")

def normalize_pair(pair):
    # Convert like BTC/USD → XBTUSD
    return pair.replace("/", "").replace("BTC", "XBT")

def get_price(pair):
    """Fetch latest ticker price from Kraken"""
    try:
        pair_fmt = normalize_pair(pair)
        r = requests.get(f"{KRAKEN_BASE_URL}?pair={pair_fmt}", timeout=10)

        if r.status_code == 429:
            logging.warning("⏳ Kraken rate limit hit, sleeping 5s...")
            time.sleep(5)
            return None

        r.raise_for_status()
        data = r.json()
        result = list(data.get("result", {}).values())[0]
        price = float(result["c"][0])  # last trade price
        logging.debug(f"Kraken {pair} → {price}")
        return {"price": price}
    except Exception as e:
        logging.error(f"❌ Kraken get_price error: {e}")
    return None


def check_connection():
    return True  # Replace with real kraken ping later
