import os
import telebot
import urllib.parse
import requests
from bs4 import BeautifulSoup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.environ.get('BOT_TOKEN')
MONETAG_AD_LINK = "https://your-monetag-ad-link.com" 
EXTRA_AD_LINK = "https://your-extra-ad-link.com"

bot = telebot.TeleBot(BOT_TOKEN)

user_steps = {}
book_storage = {}

def get_first_pdfdrive_link(book_name):
    try:
        # আপনি যেভাবে চাচ্ছেন: "বইয়ের নাম" pdfdrive.com
        query = f'"{book_name}" pdfdrive.com'
        encoded_query = urllib.parse.quote_plus(query)
        
        # গুগল বা ডাকডাকগো সার্চের পরিবর্তে সরাসরি ইউআরএল তৈরি বা স্ক্র্যাপ করার নিরাপদ পদ্ধতি
        # এখানে সরাসরি DuckDuckGo HTML পেজ থেকে প্রথম লিংকটি নিখুঁতভাবে তুলে আনা হবে
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # সার্চ রেজাল্টের প্রথম লিংকটি খুঁজে বের করা
            for a in soup.find_all('a', class_='result__url', href=True):
                link = a['href']
                # ইউআরএল ডিকোড করা যদি রিডাইরেক্ট লিংক হয়
                if 'uddg=' in link:
                    parsed_url = urllib.parse.parse_qs(urllib.parse.urlparse(link).query)
                    if 'uddg' in parsed_url:
                        return parsed_url['uddg'][0]
                return link
                
        # যদি স্ক্র্যাপিং এ সমস্যা হয়, তবে ব্যাকআপ হিসেবে ডাইরেক্ট পিডিএফ ড্রাইভের সার্চ পেজ জেনারেট করবে
        return f"https://www.pdfdrive.com/search?q={urllib.parse.quote(book_name)}"
    except Exception as e:
        return f"https://www.pdfdrive.com/search?q={urllib.parse.quote(book_name)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Hello! 📚\n\n"
        "I am your PDF Book Finder Bot.\n"
        "Send me the name of the book, complete the ad steps, and get your exact website link!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def search_book(message):
    chat_id = message.chat.id
    book_query = message.text.strip()
    wait_msg = bot.reply_to(message, "🔍 Searching the exact website, please wait...")

    try:
        # আপনার চাওয়া ফরম্যাট অনুযায়ী প্রথম ওয়েবসাইটের লিংক বের করা
        found_url = get_first_pdfdrive_link(book_query)
        
        book_storage[chat_id] = found_url
        user_steps[chat_id] = 1

        markup = InlineKeyboardMarkup(row_width=1)
        btn_ad1 = InlineKeyboardButton("📺 Watch Ad 1 of 3 (Required)", url=MONETAG_AD_LINK)
        btn_extra = InlineKeyboardButton("🔥 Bonus Offer", url=EXTRA_AD_LINK)
        btn_next = InlineKeyboardButton("➡️ Next Step (After Watching Ad)", callback_data="next_step_2")
        
        markup.add(btn_ad1, btn_extra, btn_next)

        reply_text = (
            f"📖 <b>Book Query:</b> {book_query}\n\n"
            f"⚠️ <b>Rule:</b> Complete 3 steps to unlock the exact website link.\n"
            f"👉 Click 'Watch Ad 1', view the ad, close it, then click 'Next Step'."
        )
        
        bot.edit_message_text(
            reply_text, 
            chat_id=chat_id, 
            message_id=wait_msg.message_id, 
            parse_mode='HTML', 
            disable_web_page_preview=True,
            reply_markup=markup
        )

    except Exception as e:
        bot.edit_message_text("❌ An error occurred. Please try again.", chat_id=chat_id, message_id=wait_msg.message_id)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if chat_id not in user_steps:
        user_steps[chat_id] = 1

    if call.data == "next_step_2":
        user_steps[chat_id] = 2
        markup = InlineKeyboardMarkup(row_width=1)
        btn_ad2 = InlineKeyboardButton("📺 Watch Ad 2 of 3 (Required)", url=MONETAG_AD_LINK)
        btn_next = InlineKeyboardButton("➡️ Next Step (After Watching Ad)", callback_data="next_step_3")
        markup.add(btn_ad2, btn_next)
        
        bot.edit_message_text(
            "⚠️ <b>Progress:</b> Step 2 ready.\n👉 Click 'Watch Ad 2', view it, then click 'Next Step'.",
            chat_id=chat_id,
            message_id=message_id,
            parse_mode='HTML',
            reply_markup=markup
        )

    elif call.data == "next_step_3":
        user_steps[chat_id] = 3
        markup = InlineKeyboardMarkup(row_width=1)
        btn_ad3 = InlineKeyboardButton("📺 Watch Ad 3 of 3 (Required)", url=MONETAG_AD_LINK)
        btn_finish = InlineKeyboardButton("🔓 Unlock Website Link (Final)", callback_data="unlock_link")
        markup.add(btn_ad3, btn_finish)
        
        bot.edit_message_text(
            "⚠️ <b>Progress:</b> Step 3 ready.\n👉 Click 'Watch Ad 3', view it, then click 'Unlock Website Link'.",
            chat_id=chat_id,
            message_id=message_id,
            parse_mode='HTML',
            reply_markup=markup
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
            success_text,
            chat_id=chat_id,
            message_id=message_id,
            parse_mode='HTML',
            reply_markup=markup
        )
        
        if chat_id in user_steps:
            del user_steps[chat_id]
        if chat_id in book_storage:
            del book_storage[chat_id]

if __name__ == "__main__":
    print("Bot is running with exact search mechanism...")
    bot.infinity_polling()
        
