import feedparser
from deep_translator import GoogleTranslator
import datetime
import json
import re

# RedditのRSS
FEED_URL = "https://www.reddit.com/r/EVP/new/.rss"
translator = GoogleTranslator(source='en', target='ja')

def run():
    feed = feedparser.parse(FEED_URL)
    new_data = []
    
    for entry in feed.entries[:12]: # 最新12件
        try:
            # 翻訳
            ja_text = translator.translate(entry.title)
            # 地名が含まれていれば適当な座標を振る（デモ用）
            lat, lng = 20.0, 0.0
            if "London" in entry.title: lat, lng = 51.5, -0.1
            if "Japan" in entry.title: lat, lng = 35.6, 139.7
            
            new_data.append({
                "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "source": "Reddit (r/EVP)",
                "text": f"【自動翻訳】{ja_text}",
                "url": entry.link,
                "lat": lat, "lng": lng
            })
        except: continue

    # HTMLの書き換え
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    json_data = json.dumps(new_data, ensure_ascii=False)
    new_html = re.sub(r'const posts = \[.*?\];', f'const posts = {json_data};', html, flags=re.DOTALL)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_html)

if __name__ == "__main__":
    run()
