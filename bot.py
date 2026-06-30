import os  # <-- FIX 1: ADD THIS IMPORT
import re
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pyshorteners

# --- Configuration ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # <-- FIX 2: READ FROM ENV
BOT_NAME = os.environ.get("BOT_NAME", "ShortLinkerBot")

# <-- FIX 3: ADD THIS CHECK
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize the URL shortener
s = pyshorteners.Shortener()

# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (
        f"👋 Hello! I'm {BOT_NAME}, your URL Shortener Bot.\n\n"
        "Just send me any link, and I'll make it shorter for you!\n"
        "For example, send: https://www.example.com/very/long/url\n\n"
        "Type /help for more info."
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_message = (
        "📚 **How to use me:**\n\n"
        "1.  Send me any valid URL starting with http:// or https://\n"
        "2.  I will reply with a shortened version.\n\n"
        "For example:\n"
        "`https://www.youtube.com/watch?v=dQw4w9WgXcQ`\n\n"
        "I will reply with something like: `https://tinyurl.com/abc123`"
    )
    await update.message.reply_text(help_message)

async def shorten_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    original_link = update.message.text.strip()
    url_pattern = re.compile(r'^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/.*)?$')
    if not url_pattern.match(original_link):
        await update.message.reply_text("🤔 That doesn't look like a valid web link. Please send a link starting with http:// or https://")
        return

    try:
        short_url = s.tinyurl.short(original_link)
        await update.message.reply_text(f"✨ **Short link:** {short_url}")
        user = update.message.from_user
        logger.info(f"User {user.first_name} (@{user.username}) shortened: {original_link} -> {short_url}")

    except Exception as e:
        logger.error(f"Error shortening URL: {e}")
        await update.message.reply_text("😔 Sorry, I couldn't shorten that link. It might be an invalid URL or a temporary issue.")

# --- Main Function ---
def main() -> None:
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN is not set. Please add it to your environment variables in Railway.")
        return

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, shorten_url))
    
    logger.info(f"✅ {BOT_NAME} is starting and polling for updates...")
    application.run_polling()

if __name__ == "__main__":
    main()
