import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from duckduckgo_search import DDGS

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (
        f"👋 **Hello {update.effective_user.first_name}! Welcome to the PDF Book Finder Bot.**\n\n"
        "📚 **How to use this bot:**\n"
        "1. Simply type and send the **title of the book**.\n"
        "2. The bot will automatically search the web and send you the first available PDF link.\n\n"
        "💡 *Example:* `Rich Dad Poor Dad`\n\n"
        "Type a book name below to get started!"
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

def search_first_pdf_link(query: str) -> str:
    """Search DuckDuckGo directly for PDF and return the first result link."""
    search_query = f"{query} filetype:pdf"
    
    try:
        results = list(DDGS().text(search_query, max_results=1))
        
        if results:
            first_result = results[0]
            title = first_result.get("title", "PDF Document")
            link = first_result.get("href", "")
            snippet = first_result.get("body", "")
            
            return (
                f"📖 **Book Found!**\n\n"
                f"📌 **Title:** {title}\n"
                f"📝 **Description:** {snippet}\n\n"
                f"🔗 **Download Link:** {link}"
            )
        else:
            return "❌ Sorry, no direct PDF links were found for this book."
    except Exception as e:
        logger.error(f"Search error: {e}")
        return "⚠️ An error occurred while searching. Please try again later."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_query = update.message.text.strip()
    if not user_query:
        return

    status_message = await update.message.reply_text("🔍 Searching the web for your PDF, please wait...")
    result_text = search_first_pdf_link(user_query)
    await status_message.edit_text(result_text, parse_mode="Markdown", disable_web_page_preview=False)

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
            
