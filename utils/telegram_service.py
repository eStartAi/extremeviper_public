import os
import time
import logging
import threading
import requests
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FLAG_FILE = "kill.flag"
POLL_INTERVAL = 5  # seconds


# -----------------------------------------------------------
#  Core message + kill-switch functions
# -----------------------------------------------------------

def send_telegram_message(text: str):
    """Send any text message to Telegram with debug logging."""
    if not BOT_TOKEN or not CHAT_ID:
        logger.warning("⚠️ Telegram not configured; message skipped.")
        return

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        response = requests.post(url, data={"chat_id": CHAT_ID, "text": text})
        if response.status_code != 200:
            logger.error(
                f"❌ Telegram send failed [{response.status_code}]: {response.text}"
            )
        else:
            logger.info("📨 Telegram message sent successfully.")
    except Exception as e:
        logger.error(f"❌ Telegram send error: {e}")


def is_killed() -> bool:
    return os.path.exists(FLAG_FILE)


def set_kill_flag():
    with open(FLAG_FILE, "w") as f:
        f.write(f"Killed at {time.ctime()}")
    logger.warning("🛑 Kill flag activated.")


def clear_kill_flag():
    if os.path.exists(FLAG_FILE):
        os.remove(FLAG_FILE)
        logger.info("✅ Kill flag cleared. Trading resumed.")


def get_status_text():
    if is_killed():
        return "🛑 ExtremeViper is *PAUSED* (kill flag active)."
    return "✅ ExtremeViper is *RUNNING* normally."


# -----------------------------------------------------------
#  Telegram polling listener for /kill /resume /status
# -----------------------------------------------------------

def start_telegram_listener():
    """Background thread to handle Telegram commands via polling."""
    if not BOT_TOKEN or not CHAT_ID:
        logger.warning("⚠️ Telegram not configured; listener skipped.")
        return

    def poll_loop():
        logger.info("🤖 Telegram listener started.")
        offset = None
        while True:
            try:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
                if offset:
                    url += f"?offset={offset}"
                res = requests.get(url, timeout=30).json()

                for update in res.get("result", []):
                    offset = update["update_id"] + 1
                    msg = update.get("message", {})
                    text = msg.get("text", "").strip().lower()
                    user = msg.get("from", {}).get("username", "unknown")

                    if text == "/kill":
                        set_kill_flag()
                        send_telegram_message(f"🧨 Bot stopped by @{user}")
                    elif text == "/resume":
                        clear_kill_flag()
                        send_telegram_message(f"🚀 Bot resumed by @{user}")
                    elif text == "/status":
                        send_telegram_message(get_status_text())
                    else:
                        send_telegram_message(
                            "⚙️ Commands:\n"
                            "/kill – stop trading\n"
                            "/resume – resume trading\n"
                            "/status – bot status"
                        )
            except Exception as e:
                logger.error(f"Telegram listener error: {e}")
            time.sleep(POLL_INTERVAL)

    threading.Thread(target=poll_loop, daemon=True).start()
import os
import time
import logging
import threading
import requests

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FLAG_FILE = "kill.flag"
POLL_INTERVAL = 5  # seconds


# -----------------------------------------------------------
#  Core message + kill-switch functions
# -----------------------------------------------------------

def send_telegram_message(text: str):
    """Send any text message to Telegram with debug logging."""
    if not BOT_TOKEN or not CHAT_ID:
        logger.warning("⚠️ Telegram not configured; message skipped.")
        return

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        response = requests.post(url, data={"chat_id": CHAT_ID, "text": text})
        if response.status_code != 200:
            logger.error(
                f"❌ Telegram send failed [{response.status_code}]: {response.text}"
            )
        else:
            logger.info("📨 Telegram message sent successfully.")
    except Exception as e:
        logger.error(f"❌ Telegram send error: {e}")


def is_killed() -> bool:
    return os.path.exists(FLAG_FILE)


def set_kill_flag():
    with open(FLAG_FILE, "w") as f:
        f.write(f"Killed at {time.ctime()}")
    logger.warning("🛑 Kill flag activated.")


def clear_kill_flag():
    if os.path.exists(FLAG_FILE):
        os.remove(FLAG_FILE)
        logger.info("✅ Kill flag cleared. Trading resumed.")


def get_status_text():
    if is_killed():
        return "🛑 ExtremeViper is *PAUSED* (kill flag active)."
    return "✅ ExtremeViper is *RUNNING* normally."


# -----------------------------------------------------------
#  Telegram polling listener for /kill /resume /status
# -----------------------------------------------------------

def start_telegram_listener():
    """Background thread to handle Telegram commands via polling."""
    if not BOT_TOKEN or not CHAT_ID:
        logger.warning("⚠️ Telegram not configured; listener skipped.")
        return

    def poll_loop():
        logger.info("🤖 Telegram listener started.")
        offset = None
        while True:
            try:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
                if offset:
                    url += f"?offset={offset}"
                res = requests.get(url, timeout=30).json()

                for update in res.get("result", []):
                    offset = update["update_id"] + 1
                    msg = update.get("message", {})
                    text = msg.get("text", "").strip().lower()
                    user = msg.get("from", {}).get("username", "unknown")

                    if text == "/kill":
                        set_kill_flag()
                        send_telegram_message(f"🧨 Bot stopped by @{user}")
                    elif text == "/resume":
                        clear_kill_flag()
                        send_telegram_message(f"🚀 Bot resumed by @{user}")
                    elif text == "/status":
                        send_telegram_message(get_status_text())
                    else:
                        send_telegram_message(
                            "⚙️ Commands:\n"
                            "/kill – stop trading\n"
                            "/resume – resume trading\n"
                            "/status – bot status"
                        )
            except Exception as e:
                logger.error(f"Telegram listener error: {e}")
            time.sleep(POLL_INTERVAL)

    threading.Thread(target=poll_loop, daemon=True).start()
