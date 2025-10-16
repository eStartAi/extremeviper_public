import os
import requests

def send_telegram(message: str):
    if os.getenv("ENABLE_TELEGRAM_ALERTS", "false").lower() != "true":
        return
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": message}
        )
    except Exception as e:
        print(f"[Telegram Error] {e}")
