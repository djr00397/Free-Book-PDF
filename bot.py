import os
import telebot
import urllib.parse
import requests
from bs4 import BeautifulSoup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

user_steps = {}
book_storage = {}

def get_exact_first_link(book_name):
    try:
        query = f'"{book_name}" pdfdrive.com'
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for a in soup.find_all('a', class_='result__url', href=True):
                raw_link = a['href']
                if 'uddg=' in raw_link:
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_link).query)
                    if 'uddg' in parsed:
                        return parsed['uddg'][0]
                elif raw_link.startswith('http'):
                    return raw_link
        return f"https://www.pdfdrive.com/search?q={urllib.parse.quote(book_name)}"
    except Exception:
        return f"https://www.pdfdrive.com/search?q={urllib.parse.quote(book_name)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Hello! 📚\n\n"
        "I am your PDF Book Finder Bot.\n"
        "Send me the book name to get the exact website link after completing the ad steps."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def search_book(message):
    chat_id = message.chat.id
    book_query = message.text.strip()
    wait_msg = bot.reply_to(message, "🔍 Finding the exact website, please wait...")

    try:
        found_url = get_exact_first_link(book_query)
        book_storage[chat_id] = found_url
        user_steps[chat_id] = 1

        markup = InlineKeyboardMarkup(row_width=1)
        btn_ad1 = InlineKeyboardButton("📺 Watch Ad 1 of 3 (Required)", callback_data="watch_ad_1")
        btn_next = InlineKeyboardButton("➡️ Next Step", callback_data="next_step_2")
        markup.add(btn_ad1, btn_next)

        reply_text = (
            f"📖 <b>Book Name:</b> {book_query}\n\n"
            f"⚠️ <b>Rule:</b> Complete 3 steps to unlock the exact website link.\n"
            f"👉 Click 'Watch Ad 1', complete the ad, then click 'Next Step'."
        )
        
        bot.edit_message_text(
            reply_text, 
            chat_id=chat_id, 
            message_id=wait_msg.message_id, 
            parse_mode='HTML', 
            disable_web_page_preview=True,
            reply_markup=markup
        )
    except Exception:
        fallback_url = f"https://www.pdfdrive.com/search?q={urllib.parse.quote(book_query)}"
        book_storage[chat_id] = fallback_url
        user_steps[chat_id] = 1
        
        markup = InlineKeyboardMarkup(row_width=1)
        btn_ad1 = InlineKeyboardButton("📺 Watch Ad 1 of 3 (Required)", callback_data="watch_ad_1")
        btn_next = InlineKeyboardButton("➡️ Next Step", callback_data="next_step_2")
        markup.add(btn_ad1, btn_next)
        
        bot.edit_message_text(
            f"📖 <b>Book Name:</b> {book_query}\n\n⚠️ Complete 3 steps to unlock your link.",
            chat_id=chat_id,
            message_id=wait_msg.message_id,
            parse_mode='HTML',
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if chat_id not in user_steps:
        user_steps[chat_id] = 1

    if call.data == "watch_ad_1":
        bot.answer_callback_query(call.id, "Ad 1 triggered!", show_alert=False)
    elif call.data == "watch_ad_2":
        bot.answer_callback_query(call.id, "Ad 2 triggered!", show_alert=False)
    elif call.data == "watch_ad_3":
        bot.answer_callback_query(call.id, "Ad 3 triggered!", show_alert=False)
    elif call.data == "next_step_2":
        user_steps[chat_id] = 2
        markup = InlineKeyboardMarkup(row_width=1)
        btn_ad2 = InlineKeyboardButton("📺 Watch Ad 2 of 3 (Required)", callback_data="watch_ad_2")
        btn_next = InlineKeyboardButton("➡️ Next Step", callback_data="next_step_3")
        markup.add(btn_ad2, btn_next)
        bot.edit_message_text(
            "⚠️ <b>Progress:</b> Step 2 ready.\n👉 Click 'Watch Ad 2', complete it, then click 'Next Step'.",
            chat_id=chat_id, message_id=message_id, parse_mode='HTML', reply_markup=markup
        )
    elif call.data == "next_step_3":
        user_steps[chat_id] = 3
        markup = InlineKeyboardMarkup(row_width=1)
        btn_ad3 = InlineKeyboardButton("📺 Watch Ad 3 of 3 (Required)", callback_data="watch_ad_3")
        btn_finish = InlineKeyboardButton("🔓 Unlock Website Link (Final)", callback_data="unlock_link")
        markup.add(btn_ad3, btn_finish)
        bot.edit_message_text(
            "⚠️ <b>Progress:</b> Step 3 ready.\n👉 Click 'Watch Ad 3', complete it, then click 'Unlock Website Link'.",
            chat_id=chat_id, message_id=message_id, parse_mode='HTML', reply_markup=markup
        )
    elif call.data == "unlock_link":
        final_url = book_storage.get(chat_id, "https://www.pdfdrive.com")
        markup = InlineKeyboardMarkup(row_width=1)
        btn_download = InlineKeyboardButton("📥 Open Exact Website Link", url=final_url)
        markup.add(btn_download)
        success_text = (
            "🎉 <b>Success!</b>\n\n"
            "All steps completed. The exact website link is now unlocked!\n\n"
            "👇 Click the button below to open it:"
        )
        bot.edit_message_text(
            success_text, chat_id=chat_id, message_id=message_id, parse_mode='HTML', reply_markup=markup
        )
        if chat_id in user_steps:
            del user_steps[chat_id]
        if chat_id in book_storage:
            del book_storage[chat_id]

if __name__ == "__main__":
    bot.infinity_polling()
    
