import os
import logging
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="apscheduler")
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import subprocess

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
FLAG_FILE = "kill.flag"
MODE_FILE = "mode.flag"  # stores LIVE or DRYRUN

# =========================
# === Utility Functions ===
# =========================

def set_mode(mode: str):
    """Write mode (LIVE / DRYRUN) to file."""
    with open(MODE_FILE, "w") as f:
        f.write(mode)
    logger.info(f"Mode set to {mode}")

def get_mode() -> str:
    """Read mode file or default to DRYRUN."""
    if not os.path.exists(MODE_FILE):
        return "DRYRUN"
    return open(MODE_FILE).read().strip().upper()

def set_kill_flag():
    open(FLAG_FILE, "w").close()
    logger.warning("🚨 Kill switch activated!")

def clear_kill_flag():
    if os.path.exists(FLAG_FILE):
        os.remove(FLAG_FILE)
        logger.info("✅ Kill switch deactivated.")

def restart_bot():
    """Restart the systemd service for ExtremeViper."""
    try:
        subprocess.run(
            ["sudo", "systemctl", "restart", "extremeviper.service"],
            check=True,
        )
        return "🔁 Bot service restarted successfully!"
    except Exception as e:
        return f"❌ Restart failed: {e}"

# =========================
# === Telegram Commands ===
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main menu when /start is sent."""
    keyboard = [
        [
            InlineKeyboardButton("🟢 Enable Live Mode", callback_data="enable_live"),
            InlineKeyboardButton("🔴 Enable DRYRUN Mode", callback_data="enable_dryrun"),
        ],
        [
            InlineKeyboardButton("📊 Show Stats", callback_data="show_stats"),
            InlineKeyboardButton("🔁 Restart Bot", callback_data="restart_bot"),
        ],
        [
            InlineKeyboardButton("🛑 Kill Switch", callback_data="kill_bot"),
            InlineKeyboardButton("♻️ Resume Bot", callback_data="resume_bot"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"🤖 <b>ExtremeViper Control Panel</b>\n\n"
        f"Current Mode: <b>{get_mode()}</b>\n"
        f"Kill Flag: {'🚫 ACTIVE' if os.path.exists(FLAG_FILE) else '✅ CLEAR'}",
        reply_markup=reply_markup,
        parse_mode="HTML",
    )

# =========================
# === Button Callbacks ===
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data

    if action == "enable_live":
        set_mode("LIVE")
        await query.edit_message_text("🟢 Live Mode Enabled.")
    elif action == "enable_dryrun":
        set_mode("DRYRUN")
        await query.edit_message_text("🔴 DRYRUN Mode Enabled.")
    elif action == "show_stats":
        # Placeholder – connect to your PnL or score system later
        await query.edit_message_text("📊 Bot Stats:\n\n- Pairs Scanned: 8\n- Trades Today: 3\n- Win Rate: 66%")
    elif action == "restart_bot":
        msg = restart_bot()
        await query.edit_message_text(msg)
    elif action == "kill_bot":
        set_kill_flag()
        await query.edit_message_text("🛑 Kill switch activated! All trading halted.")
    elif action == "resume_bot":
        clear_kill_flag()
        await query.edit_message_text("♻️ Bot resumed. Safe to continue trading.")
    else:
        await query.edit_message_text("❓ Unknown command")

# =========================
# === Run Telegram Bot ===
# =========================

def run_telegram_service():
    """Launch Telegram control interface."""
    if not BOT_TOKEN:
        print("⚠️ TELEGRAM_BOT_TOKEN missing in .env")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    logger.info("🚀 Telegram control service running...")
    app.run_polling()

if __name__ == "__main__":
    run_telegram_service()
