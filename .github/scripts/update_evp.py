import feedparser
from deep_translator import GoogleTranslator
import datetime
import json
import re
import os

SOURCES = [
    "https://www.reddit.com/r/EVP/new/.rss",
    "https://www.reddit.com/r/Paranormal/new/.rss",
    "https://www.reddit.com/r/ghosts/new/.rss"
]
translator = GoogleTranslator(source='en', target='ja')

def crawl():
    all_posts = []
    print("📡 受信開始...")
    for url in SOURCES:
        feed = feedparser.parse(url)
        for entry in feed.entries[:8]:
            try:
                ja_text = translator.translate(entry.title)
                all_posts.append({
                    "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "source": "Reddit Observation",
                    "text": f"【自動翻訳】{ja_text}",
                    "url": entry.link
                })
            except:
                continue

    if not os.path.exists("index.html"): return

    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    json_str = json.dumps(all_posts, ensure_ascii=False, indent=4)
    pattern = r'const posts = \[.*?\];'
    replacement = f'const posts = {json_str};'
    
    if re.search(pattern, content, flags=re.DOTALL):
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("✅ データ流し込み成功")

if __name__ == "__main__":
    crawl()
