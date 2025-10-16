from utils import alpaca_api

def ping():
    try:
        return alpaca_api.check_connection()
    except Exception:
        return False
