import feedparser
from deep_translator import GoogleTranslator
import datetime
import json
import re
import random
import os

SOURCES = [
    "https://www.reddit.com/r/EVP/new/.rss",
    "https://www.reddit.com/r/Paranormal/new/.rss"
]
translator = GoogleTranslator(source='en', target='ja')

def crawl():
    all_posts = []
    print("Fetching feeds...")
    for url in SOURCES:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            try:
                ja_text = translator.translate(entry.title)
                all_posts.append({
                    "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "source": "Reddit Observation",
                    "text": f"【自動要約】{ja_text}",
                    "url": entry.link,
                    "lat": random.uniform(-10, 50),
                    "lng": random.uniform(-100, 130)
                })
            except Exception as e:
                print(f"Skipping entry: {e}")
                continue

    if not os.path.exists("index.html"):
        print("Error: index.html not found!")
        return

    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 置換ターゲットをより確実に
    json_str = json.dumps(all_posts, ensure_ascii=False, indent=4)
    # const posts = []; を探し出し、新しいデータで上書きする
    pattern = r'const posts = \[.*?\];'
    replacement = f'const posts = {json_str};'
    
    if re.search(pattern, content, flags=re.DOTALL):
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Successfully updated with {len(all_posts)} items.")
    else:
        print("Error: Could not find 'const posts = [];' in index.html")

if __name__ == "__main__":
    crawl()
