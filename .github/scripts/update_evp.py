import feedparser
from deep_translator import GoogleTranslator
import datetime
import json
import re
import os
import time

# キーワード設定
KEYWORDS = [
    "EVP", "Electronic Voice Phenomena", "Spirit Box", "Ghost Box", "Ghost Voice",
    "Paranormal Audio", "ITC", "Instrumental Transcommunication",
    "電子音声現象", "スピリットボックス", "ゴーストボイス", "霊の声", "心霊録音",
    "심령 현상", "고스트 보이스", "EVP 녹음", "영혼의 목소리",
    "靈異聲音", "電子語音現象", "鬼魂語音"
]

def get_sources():
    base_url = "https://news.google.com/rss/search?q={query}&hl={hl}&gl={gl}&ceid={ceid}"
    # 検索クエリを短くしてエラーを回避
    query = "EVP+OR+Ghost+Voice+OR+霊の声"
    sources = [
        "https://www.reddit.com/r/EVP/new/.rss",
        "https://www.reddit.com/r/SpiritBox/new/.rss",
        base_url.format(query=query, hl="ja", gl="JP", ceid="JP:ja"),
        base_url.format(query=query, hl="ko", gl="KR", ceid="KR:ko"),
        base_url.format(query=query, hl="en", gl="US", ceid="US:en")
    ]
    return sources

translator = GoogleTranslator(source='auto', target='ja')

def crawl():
    new_posts = []
    print("📡 信号スキャン開始...")
    
    for url in get_sources():
        feed = feedparser.parse(url)
        for entry in feed.entries[:8]:
            try:
                # 翻訳エラー回避のための待機
                time.sleep(1) 
                translated_title = translator.translate(entry.title)
                
                new_posts.append({
                    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "source": "Global Network",
                    "text": translated_title,
                    "url": entry.link
                })
            except Exception as e:
                print(f"Skip entry: {e}")
                continue

    if not os.path.exists("index.html"):
        print("index.html not found")
        return

    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 蓄積ロジックの修正
    try:
        current_json_match = re.search(r'const posts = (\[.*?\]);', content, flags=re.DOTALL)
        old_posts = json.loads(current_json_match.group(1)) if current_json_match else []
    except:
        old_posts = []

    existing_urls = {p['url'] for p in old_posts}
    combined_posts = [p for p in new_posts if p['url'] not in existing_urls] + old_posts
    final_posts = combined_posts[:200]

    json_str = json.dumps(final_posts, ensure_ascii=False, indent=4)
    # 確実に置換するためのパターン
    new_content = re.sub(r'const posts = \[.*?\];', f'const posts = {json_str};', content, flags=re.DOTALL)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ 成功: {len(final_posts)}件保存")

if __name__ == "__main__":
    crawl()
