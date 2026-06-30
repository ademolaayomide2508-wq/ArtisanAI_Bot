import re
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pyshorteners

# --- Configuration ---
# Replace with your actual bot token from BotFather
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Setup logging to see what's happening
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize the URL shortener
s = pyshorteners.Shortener()

# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is issued."""
    welcome_message = (
        "👋 Hello! I'm your URL Shortener Bot.\n\n"
        "Just send me any link, and I'll make it shorter for you!\n"
        "For example, send: https://www.example.com/very/long/url\n\n"
        "Type /help for more info."
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the /help command is issued."""
    help_message = (
        "📚 **How to use me:**\n\n"
        "1.  Send me any valid URL starting with http:// or https://\n"
        "2.  I will reply with a shortened version.\n\n"
        "For example:\n"
        "`https://www.youtube.com/watch?v=dQw4w9WgXcQ`\n\n"
        "I will reply with something like: `https://tinyurl.com/abc123`"
    )
    await update.message.reply_text(help_message)

# --- Message Handler ---
async def shorten_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shorten the URL that was sent as a message."""
    # Get the text the user sent
    original_link = update.message.text.strip()

    # Basic validation: Check if the text looks like a URL [citation:7]
    # This regex checks for typical web addresses
    url_pattern = re.compile(r'^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/.*)?$')
    if not url_pattern.match(original_link):
        await update.message.reply_text("🤔 That doesn't look like a valid web link. Please send a link starting with http:// or https://")
        return

    try:
        # Use pyshorteners to shorten the URL [citation:7]
        # The 'tinyurl' method is used as it requires no API key.
        short_url = s.tinyurl.short(original_link)
        await update.message.reply_text(f"✨ **Short link:** {short_url}")

        # Optional: Log the action to the console for debugging
        user = update.message.from_user
        logger.info(f"User {user.first_name} (@{user.username}) shortened: {original_link} -> {short_url}")

    except Exception as e:
        logger.error(f"Error shortening URL: {e}")
        await update.message.reply_text("😔 Sorry, I couldn't shorten that link. It might be an invalid URL or a temporary issue.")

# --- Main Function ---
def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    # The MessageHandler filters for text messages that are NOT commands (like /start) [citation:6]
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, shorten_url))

    # Start the bot using long-polling. This is the simplest method for Railway. [citation:6][citation:10]
    logger.info("Bot is starting and polling for updates...")
    application.run_polling()

if __name__ == "__main__":
    main()
