import traceback
import time
from notify.notify import send_telegram

def run_safe(main_fn, bot_name="Bot"):
    while True:
        try:
            main_fn()
        except Exception as e:
            print(f"💥 {bot_name} crashed: {e}")
            traceback.print_exc()
            send_telegram(f"💥 {bot_name} crashed: {e}\nRestarting in 5s...")
            time.sleep(5)