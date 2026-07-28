
        
import os
import telebot
import urllib.parse
import requests
from bs4 import BeautifulSoup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

book_storage = {}

def get_google_first_result(book_name):
    try:
        query = f'"{book_name}"pdfdrive.com'
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for g in soup.find_all('div', class_='g'):
                anchor = g.find('a')
                if anchor and 'href' in anchor.attrs:
                    link = anchor['href']
                    if link.startswith('http'):
                        return link
                        
            for a in soup.find_all('a', href=True):
                link = a['href']
                if link.startswith('/url?q='):
                    actual_link = link.split('/url?q=')[1].split('&sa=')[0]
                    if actual_link.startswith('http'):
                        return actual_link
                        
        return f"https://www.google.com/search?q={urllib.parse.quote(f'\"{book_name}\"pdfdrive.com')}"
    except Exception:
        return f"https://www.google.com/search?q={urllib.parse.quote(f'\"{book_name}\"pdfdrive.com')}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Hello! 📚\n\n"
        "I am your Book Finder Bot.\n"
        "Send me the book name to get the first website link from Google search directly!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def search_book(message):
    chat_id = message.chat.id
    book_query = message.text.strip()
    wait_msg = bot.reply_to(message, "🔍 Searching Google and finding the first website, please wait...")

    try:
        found_url = get_google_first_result(book_query)
        
        markup = InlineKeyboardMarkup(row_width=1)
        btn_download = InlineKeyboardButton("📥 Open First Website Link", url=found_url)
        markup.add(btn_download)

        success_text = (
            f"📖 <b>Book Name:</b> {book_query}\n\n"
            f"🎉 <b>Success!</b> The first website link from Google search is ready.\n\n"
            f"👇 Click the button below to open it:"
        )
        
        bot.edit_message_text(
            success_text, 
            chat_id=chat_id, 
            message_id=wait_msg.message_id, 
            parse_mode='HTML', 
            disable_web_page_preview=True,
            reply_markup=markup
        )
    except Exception:
        bot.edit_message_text("❌ An error occurred. Please try again.", chat_id=chat_id, message_id=wait_msg.message_id)

if __name__ == "__main__":
    bot.infinity_polling()
                
