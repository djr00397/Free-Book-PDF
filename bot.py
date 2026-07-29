import requests
from bs4 import BeautifulSoup
import urllib.parse

def search_google_directly(query: str) -> str:
    search_query = f"{query} filetype:pdf"
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://www.google.com/search?q={encoded_query}"
    
    # Fake browser user-agent to bypass basic blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find the first search result container in Google HTML
            for g in soup.find_all('div', class_='g'):
                anchors = g.find_all('a')
                if anchors:
                    link = anchors[0]['href']
                    title = g.find('h3').text if g.find('h3') else "PDF Book"
                    
                    if link.startswith("http"):
                        return (
                            f"📖 **Book Found!**\n\n"
                            f"📌 **Title:** {title}\n\n"
                            f"🔗 **Download Link:** {link}"
                        )
            return "❌ No direct PDF link found on Google."
        else:
            return "⚠️ Google blocked the request or rate-limited. Try DuckDuckGo method instead."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
            
