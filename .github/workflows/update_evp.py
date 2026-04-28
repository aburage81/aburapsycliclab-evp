import feedparser
from deep_translator import GoogleTranslator
import datetime
import json
import re
import random

# 設定
SOURCES = ["https://www.reddit.com/r/EVP/new/.rss", "https://www.reddit.com/r/Paranormal/new/.rss"]
translator = GoogleTranslator(source='en', target='ja')

def crawl():
    all_entries = []
    for url in SOURCES:
        feed = feedparser.parse(url)
        all_entries.extend(feed.entries[:8]) # 各ソース上位8件

    processed_posts = []
    for entry in all_entries:
        try:
            # 翻訳と要約（タイトルを日本語化）
            translated_text = translator.translate(entry.title)
            
            # ランダムな座標（世界中から来ている演出、または地名抽出）
            lat = random.uniform(-40, 60)
            lng = random.uniform(-120, 140)

            processed_posts.append({
                "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "source": "Global Network (Reddit)",
                "text": f"【要約】{translated_text}",
                "url": entry.link,
                "lat": lat,
                "lng": lng
            })
        except:
            continue

    # HTML更新（マーカーの間を置換）
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    json_str = json.dumps(processed_posts, ensure_ascii=False, indent=4)
    new_content = re.sub(
        r'// --- DATA START ---\s+const posts = \[.*?\];\s+// --- DATA END ---',
        f'// --- DATA START ---\n        const posts = {json_str};\n        // --- DATA END ---',
        content, flags=re.DOTALL
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    crawl()
