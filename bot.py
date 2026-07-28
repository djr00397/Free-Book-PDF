import os
import telebot
import requests
import urllib.parse
from duckduckgo_search import DDGS

BOT_TOKEN = os.environ.get('BOT_TOKEN')
SHRINKME_API_KEY = os.environ.get('SHRINKME_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Hello! 📚\n\n"
        "I am your PDF Book Finder Bot.\n"
        "Just send me the name of the book you want, and I will find it for you from PDFDrive!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def search_book(message):
    book_query = message.text.strip()
    wait_msg = bot.reply_to(message, "🔍 Searching for the book and details, please wait...")

    try:
        # আপনার চাওয়া ফরম্যাট অনুযায়ী কুয়েরি তৈরি করা: "Book Name" pdfdrive.com
        formatted_query = f'"{book_query}" pdfdrive.com'
        
        found_url = None
        book_title = book_query
        book_snippet = "No description available."
        
        # DuckDuckGo দিয়ে সার্চ করা
        with DDGS() as ddgs:
            results = list(ddgs.text(formatted_query, max_results=1))
            if results:
                found_url = results[0].get('href')
                book_title = results[0].get('title', book_query)
                book_snippet = results[0].get('body', 'Click the link below to view and download the book.')

        # যদি লিংক না পাওয়া যায়, তবে সরাসরি পিডিএফ ড্রাইভের সার্চ পেজ জেনারেট করবে
        if not found_url:
            encoded_query = urllib.parse.quote(book_query)
            found_url = f"https://www.pdfdrive.com/search?q={encoded_query}"

        # ShrinkMe দিয়ে লিংক শর্ট করা
        api_url = f"https://shrinkme.io/api?api={SHRINKME_API_KEY}&url={found_url}"
        response = requests.get(api_url).json()
        
        if response.get('status') == 'success':
            short_link = response['shortenedUrl']
            
            # আকর্ষণীয় ফরম্যাটে আউটপুট সাজানো (বইয়ের নাম, বিবরণ ও শর্ট লিংক)
            reply_text = (
                f"📖 <b>Book:</b> {book_title}\n\n"
                f"📝 <b>Details:</b> {book_snippet}\n\n"
                f"🔗 <b>Download Link:</b> {short_link}"
            )
            
            bot.edit_message_text(
                reply_text, 
                chat_id=message.chat.id, 
                message_id=wait_msg.message_id, 
                parse_mode='HTML', 
                disable_web_page_preview=False
            )
        else:
            bot.edit_message_text("❌ Failed to generate the short link. Please try again.", chat_id=message.chat.id, message_id=wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text("❌ An error occurred while searching. Please try again later.", chat_id=message.chat.id, message_id=wait_msg.message_id)

if __name__ == "__main__":
    print("Bot is successfully running...")
    bot.infinity_polling()
            
