from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=".env")   # explicitly point to file

print("BOT_TOKEN =", os.getenv("TELEGRAM_BOT_TOKEN"))
print("CHAT_ID   =", os.getenv("TELEGRAM_CHAT_ID"))
print("ENABLE    =", os.getenv("ENABLE_TELEGRAM_ALERTS"))
