#!/usr/bin/env python3
import os, logging
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from telegram.ext import Updater, CommandHandler, Filters

load_dotenv()
logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL","INFO")))

TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID  = int(os.getenv("TELEGRAM_CHAT_ID","0"))
APP_DIR  = Path(os.getenv("APP_DIR", str(Path.home() / "extremeviper")))
KILL_FILE = APP_DIR / os.getenv("KILL_FILE", "control/kill.flag")
STOP_TODAY_FILE = APP_DIR / os.getenv("STOP_TODAY_FILE", "control/stop_today.flag")
LOG_FILE = APP_DIR / "logs/runtime.log"

assert TG_TOKEN and CHAT_ID, "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"

def restricted(func):
    def wrapper(update, context, *args, **kwargs):
        if update.effective_chat.id != CHAT_ID:
            return
        return func(update, context, *args, **kwargs)
    return wrapper

@restricted
def hello(update, context):
    update.message.reply_text("🐍 ExtremeViper control online. Commands: /status /kill /resume /halt /unhalt /tail")

@restricted
def status(update, context):
    state = []
    state.append(f"KILL: {'ON' if KILL_FILE.exists() else 'off'}")
    state.append(f"HALT_TODAY: {'ON' if STOP_TODAY_FILE.exists() else 'off'}")
    # tail the last 8 lines of runtime.log if present
    tail = "no log yet"
    if LOG_FILE.exists():
        try:
            lines = LOG_FILE.read_text(errors='ignore').splitlines()[-8:]
            tail = "\n".join(lines)
        except Exception:
            pass
    update.message.reply_text(f"📊 Status @ {datetime.now().strftime('%H:%M:%S')}:\n" + "\n".join(state) + f"\n\n📝 Log tail:\n{tail}")

@restricted
def kill(update, context):
    KILL_FILE.parent.mkdir(parents=True, exist_ok=True)
    KILL_FILE.write_text("1")
    update.message.reply_text("🛑 Kill-switch ENABLED. Bot loop should idle.")

@restricted
def resume(update, context):
    if KILL_FILE.exists():
        KILL_FILE.unlink()
    update.message.reply_text("▶️ Kill-switch DISABLED. Bot may resume loop.")

@restricted
def halt(update, context):
    STOP_TODAY_FILE.parent.mkdir(parents=True, exist_ok=True)
    STOP_TODAY_FILE.write_text("1")
    update.message.reply_text("⏸️ Halt for TODAY set. Bot should stand down until file removed.")

@restricted
def unhalt(update, context):
    if STOP_TODAY_FILE.exists():
        STOP_TODAY_FILE.unlink()
    update.message.reply_text("✅ Halt for TODAY removed.")

@restricted
def tail(update, context):
    if LOG_FILE.exists():
        lines = LOG_FILE.read_text(errors='ignore').splitlines()[-20:]
        update.message.reply_text("🧾 Last 20 log lines:\n" + "\n".join(lines))
    else:
        update.message.reply_text("No log file yet.")

def main():
    updater = Updater(TG_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", hello))
    dp.add_handler(CommandHandler("help", hello))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("kill", kill))
    dp.add_handler(CommandHandler("resume", resume))
    dp.add_handler(CommandHandler("halt", halt))
    dp.add_handler(CommandHandler("unhalt", unhalt))
    dp.add_handler(CommandHandler("tail", tail))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
