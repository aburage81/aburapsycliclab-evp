import feedparser
from deep_translator import GoogleTranslator
import datetime
import json
import re
import os

# 収集ソース（世界中のEVP/怪異コミュニティ）
SOURCES = [
    "https://www.reddit.com/r/EVP/new/.rss",
    "https://www.reddit.com/r/Paranormal/new/.rss",
    "https://www.reddit.com/r/ghosts/new/.rss"
]
translator = GoogleTranslator(source='en', target='ja')

def crawl():
    all_posts = []
    print("📡 電子の海から信号を受信中...")
    
    for url in SOURCES:
        feed = feedparser.parse(url)
        # 各ソースから最新5件を取得
        for entry in feed.entries[:5]:
            try:
                # 翻訳（Redditのタイトルを日本語化）
                ja_text = translator.translate(entry.title)
                all_posts.append({
                    "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "source": "Reddit Global Observation",
                    "text": f"【自動要約】{ja_text}",
                    "url": entry.link
                })
            except Exception as e:
                print(f"Skipping entry due to error: {e}")
                continue

    if not all_posts:
        print("❌ 信号を受信できませんでした。")
        return

    # index.html の読み込み
    if not os.path.exists("index.html"):
        print("❌ index.html が見当たりません。")
        return

    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 記事データをJSON化
    json_str = json.dumps(all_posts, ensure_ascii=False, indent=4)
    
    # 正規表現で 'const posts = [];' を探し出し、中身を書き換える
    # 改行やスペースがあっても対応できるように [.*?\] を使用
    pattern = r'const posts = \[.*?\];'
    replacement = f'const posts = {json_str};'
    
    if re.search(pattern, content, flags=re.DOTALL):
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ アーカイブ更新成功: {len(all_posts)}件の信号を記録しました。")
    else:
        print("❌ HTML内に 'const posts = [];' が見つかりませんでした。")

if __name__ == "__main__":
    crawl()
