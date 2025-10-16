from utils import tos_api

def ping():
    try:
        return tos_api.check_connection()
    except Exception:
        return False

