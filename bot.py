import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from duckduckgo_search import DDGS

BOT_TOKEN = os.environ.get('BOT_TOKEN')
# আপনার মনিটেক বা অন্যান্য অ্যাড নেটওয়ার্কের ডাইরেক্ট লিংক এখানে বসাবেন
MONETAG_AD_LINK = "https://your-monetag-ad-link.com" 
EXTRA_AD_LINK_1 = "https://your-extra-ad-link-1.com"
EXTRA_AD_LINK_2 = "https://your-extra-ad-link-2.com"

bot = telebot.TeleBot(BOT_TOKEN)

user_steps = {}
book_storage = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Hello! 📚\n\n"
        "I am your PDF Book Finder Bot.\n"
        "Send me the name of the book you want, complete the 3 steps, and get your download link!"
    )
    # স্টার্ট মেসেজেও অতিরিক্ত উপার্জনের জন্য একটি স্পอนসর্ড বাটন রাখা হলো
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("🌟 Sponsor / Special Offer", url=EXTRA_AD_LINK_1))
    
    bot.reply_to(message, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def search_book(message):
    chat_id = message.chat.id
    book_query = message.text.strip()
    wait_msg = bot.reply_to(message, "🔍 Searching for the book, please wait...")

    try:
        formatted_query = f'"{book_query}" pdfdrive.com'
        found_url = None
        book_title = book_query
        book_snippet = "Complete the ad steps below to unlock your book."
        
        with DDGS() as ddgs:
            results = list(ddgs.text(formatted_query, max_results=1))
            if results:
                found_url = results[0].get('href')
                book_title = results[0].get('title', book_query)
                book_snippet = results[0].get('body', 'Complete the ad steps below to unlock your book.')

        if not found_url:
            import urllib.parse
            encoded_query = urllib.parse.quote(book_query)
            found_url = f"https://www.pdfdrive.com/search?q={encoded_query}"

        book_storage[chat_id] = found_url
        user_steps[chat_id] = 1

        # ১ম স্টেপের বাটন এবং সাথে একটি অতিরিক্ত স্পন্সরড/অ্যাড বাটন
        markup = InlineKeyboardMarkup(row_width=1)
        btn_ad1 = InlineKeyboardButton("📺 Watch Ad 1 of 3 (Required)", url=MONETAG_AD_LINK)
        btn_extra = InlineKeyboardButton("🔥 Bonus Offer (Extra Ad)", url=EXTRA_AD_LINK_2)
        btn_next = InlineKeyboardButton("➡️ Next Step (After Watching Ad)", callback_data="next_step_2")
        
        markup.add(btn_ad1, btn_extra, btn_next)

        reply_text = (
            f"📖 <b>Book:</b> {book_title}\n\n"
            f"📝 <b>Details:</b> {book_snippet}\n\n"
            f"⚠️ <b>Rule:</b> You must watch 3 required ads to unlock the download link.\n"
            f"👉 Click 'Watch Ad 1', view it, close the tab, then click 'Next Step'."
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
        bot.edit_message_text("❌ An error occurred while searching. Please try again later.", chat_id=chat_id, message_id=wait_msg.message_id)


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
            call.message.text.split("⚠️")[0] + "⚠️ <b>Progress:</b> Step 2 ready.\n👉 Click 'Watch Ad 2', view it, then click 'Next Step'.",
            chat_id=chat_id,
            message_id=message_id,
            parse_mode='HTML',
            reply_markup=markup
        )

    elif call.data == "next_step_3":
        user_steps[chat_id] = 3
        markup = InlineKeyboardMarkup(row_width=1)
        btn_ad3 = InlineKeyboardButton("📺 Watch Ad 3 of 3 (Required)", url=MONETAG_AD_LINK)
        btn_finish = InlineKeyboardButton("🔓 Unlock Download Link (Final)", callback_data="unlock_link")
        markup.add(btn_ad3, btn_finish)
        
        bot.edit_message_text(
            call.message.text.split("⚠️")[0] + "⚠️ <b>Progress:</b> Step 3 ready.\n👉 Click 'Watch Ad 3', view it, then click 'Unlock Download Link'.",
            chat_id=chat_id,
            message_id=message_id,
            parse_mode='HTML',
            reply_markup=markup
        )

    elif call.data == "unlock_link":
        final_url = book_storage.get(chat_id, "https://www.pdfdrive.com")
        
        markup = InlineKeyboardMarkup(row_width=1)
        btn_download = InlineKeyboardButton("📥 Download Book Now", url=final_url)
        btn_extra_download = InlineKeyboardButton("🌟 Support Us (Extra Ad)", url=EXTRA_AD_LINK_1)
        markup.add(btn_download, btn_extra_download)
        
        success_text = (
            "🎉 <b>Congratulations!</b>\n\n"
            "All 3 required steps completed successfully. Your book download link is now unlocked!\n\n"
            "👇 Click the button below to get your book:"
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
    print("Bot with Multi-Step Unlock & Extra Ads is running...")
    bot.infinity_polling()
        
