import os
import telebot
import requests
from flask import Flask
from threading import Thread
from duckduckgo_search import DDGS

# Fetching Token and API Key from Environment Variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
SHRINKME_API_KEY = os.environ.get('SHRINKME_API_KEY')

# Initializing the bot and Flask app
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# 1. Handling the /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Hello! 📚\n\n"
        "I am a free PDF book finder bot.\n"
        "Send me a book's name (and author's name), and I will provide you with the download link!"
    )
    bot.reply_to(message, welcome_text)

# 2. Searching for the book link via DuckDuckGo
@bot.message_handler(func=lambda message: True)
def search_book(message):
    book_query = message.text
    wait_msg = bot.reply_to(message, "🔍 Searching for the book, please wait...")

    try:
        query = f"site:pdfdrive.com {book_query}"
        found_url = None
        book_title = book_query
        
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=1))
            if results:
                found_url = results[0].get('href')
                book_title = results[0].get('title', book_query)
        
        if found_url:
            api_url = f"https://shrinkme.io/api?api={SHRINKME_API_KEY}&url={found_url}"
            response = requests.get(api_url).json()
            
            if response.get('status') == 'success':
                short_link = response['shortenedUrl']
                reply_text = (
                    f"📖 <b>Book:</b> {book_title}\n\n"
                    f"✅ <b>Download Link:</b> {short_link}"
                )
                bot.edit_message_text(reply_text, chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode='HTML', disable_web_page_preview=True)
            else:
                bot.edit_message_text("❌ There was a problem shortening the link.", chat_id=message.chat.id, message_id=wait_msg.message_id)
        else:
            bot.edit_message_text(f"❌ Sorry, no book found for '{book_query}' on PDFDrive.", chat_id=message.chat.id, message_id=wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text("❌ A server error occurred. Please try again later.", chat_id=message.chat.id, message_id=wait_msg.message_id)

# Running Flask in background and Bot in main thread
if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    print("Bot and Flask server are successfully running...")
    bot.infinity_polling()
    
