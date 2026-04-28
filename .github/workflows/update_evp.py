import feedparser
from deep_translator import GoogleTranslator
import datetime
import json
import re

SOURCES = [
    "https://www.reddit.com/r/EVP/new/.rss",
    "https://www.reddit.com/r/Paranormal/new/.rss",
    "https://www.reddit.com/r/ghosts/new/.rss"
]
translator = GoogleTranslator(source='en', target='ja')

def crawl():
    all_posts = []
    print("情報収集を開始します...")
    
    for url in SOURCES:
        feed = feedparser.parse(url)
        for entry in feed.entries[:8]: # 各ソースから上位8件
            try:
                # 翻訳
                ja_text = translator.translate(entry.title)
                all_posts.append({
                    "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "source": "Global Network",
                    "text": f"【自動翻訳】{ja_text}",
                    "url": entry.link
                })
            except:
                continue

    # index.html の書き換え
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    json_str = json.dumps(all_posts, ensure_ascii=False, indent=4)
    # // --- DATA START --- と // --- DATA END --- の間を置換
    pattern = r'// --- DATA START ---\s+const posts = \[.*?\];\s+// --- DATA END ---'
    replacement = f'// --- DATA START ---\n        const posts = {json_str};\n        // --- DATA END ---'
    
    if re.search(pattern, content, flags=re.DOTALL):
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"アーカイブ更新完了: {len(all_posts)}件")
    else:
        print("エラー: 置換マーカーが見つかりません。")

if __name__ == "__main__":
    crawl()
