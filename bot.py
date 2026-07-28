import requests
from bs4 import BeautifulSoup
import telebot

# ----------------- Configuration -----------------
BOT_TOKEN = "8829414299:AAGK_J9MbIAwojhf7qd07j5tkkXCl9Ye75M"
SHRINKME_API_KEY = "99a01d01c2d2fd176a7afbe341b227023b06ee44"

bot = telebot.TeleBot(BOT_TOKEN)

# 1. Function to shorten URL using ShrinkMe.io
def shorten_url(original_url):
    try:
        api_url = f"https://shrinkme.io/api?api={SHRINKME_API_KEY}&url={original_url}"
        response = requests.get(api_url)
        data = response.json()
        if data.get("status") == "success":
            return data.get("shortenedUrl")
        else:
            return original_url
    except Exception as e:
        print(f"Error shortening URL: {e}")
        return original_url

# 2. Function to search and scrape PDFDrive
def search_pdfdrive(query):
    # PDFDrive-এ সার্চ করার লিংক
    url = f"https://www.pdfdrive.com/search?q={query}"
    # ওয়েবসাইটের কাছে নিজেদের সাধারণ ব্রাউজার হিসেবে পরিচয় দেওয়া
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # PDFDrive-এর প্রথম রেজাল্টটি খোঁজা
        first_result = soup.find('div', class_='file-left')
        
        if first_result:
            link_tag = first_result.find('a')
            img_tag = first_result.find('img')
            
            if link_tag and img_tag:
                book_link = "https://www.pdfdrive.com" + link_tag.get('href', '')
                image_url = img_tag.get('src', '')
                title = img_tag.get('title', '') or img_tag.get('alt', 'Unknown Title')
                
                return {
                    "title": title.strip(),
                    "image": image_url,
                    "link": book_link
                }
    except Exception as e:
        print(f"Error searching PDFDrive: {e}")
        
    return None

# 3. /start Command Handler (ইংরেজিতে সুন্দরভাবে বোঝানো)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "📚 *Welcome to Free Book PDF Bot!*\n\n"
        "Here you can easily find and download your favorite books in PDF format for free.\n\n"
        "👇 *How to use:*\n"
        "Simply type the **Book Name** or the **Book Name with its Author** and send it to me.\n\n"
        "💡 *Example:* `Rich Dad Poor Dad` or `Hamlet William Shakespeare`\n\n"
        "I will fetch the book's cover image and provide you with a direct download link. Happy Reading!"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# 4. Message Handler for Book Searching
@bot.message_handler(func=lambda message: True)
def handle_search(message):
    query = message.text.strip()
    # ইউজারকে জানানো হচ্ছে যে বট কাজ করছে
    msg = bot.reply_to(message, "🔍 *Searching PDFDrive for your book...*\nPlease wait a moment.", parse_mode="Markdown")
    
    book = search_pdfdrive(query)
    
    if book:
        # লিংক শর্ট করা হচ্ছে ইনকামের জন্য
        short_link = shorten_url(book["link"])
        
        caption = (
            f"📖 *Title:* {book['title']}\n\n"
            f"📥 *Download PDF Here:*\n{short_link}\n\n"
            f"_(Click the link, skip the ad, and download your book from PDFDrive)_"
        )
        
        # ছবি থাকলে ছবির সাথে ক্যাপশন পাঠানো
        if book["image"] and book["image"].startswith("http"):
            try:
                bot.send_photo(message.chat.id, book["image"], caption=caption, parse_mode="Markdown")
                bot.delete_message(message.chat.id, msg.message_id) # 'Searching...' মেসেজ ডিলিট করা
            except Exception:
                bot.edit_message_text(caption, message.chat.id, msg.message_id, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            bot.edit_message_text(caption, message.chat.id, msg.message_id, parse_mode="Markdown", disable_web_page_preview=True)
    else:
        error_msg = (
            "❌ *Sorry, no book found with that name on PDFDrive.*\n\n"
            "Please check the spelling and try again, or try searching with just the book's main title."
        )
        bot.edit_message_text(error_msg, message.chat.id, msg.message_id, parse_mode="Markdown")

# 5. Start Polling
if __name__ == "__main__":
    print("Free Book PDF Bot is running...")
    bot.infinity_polling()
      
