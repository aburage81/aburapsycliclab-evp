import feedparser
from deep_translator import GoogleTranslator
import datetime
import json
import re
import os

# 検索キーワード（多言語対応）
# 霊の声、録音、対話、スピリットボックスなど
KEYWORDS = [
    "EVP", "Electronic Voice Phenomena", "Spirit Box", "Ghost Box", "Ghost Voice",
    "Paranormal Audio", "ITC", "Instrumental Transcommunication",
    "電子音声現象", "スピリットボックス", "ゴーストボイス", "霊の声", "心霊録音",
    "심령 현상", "고스트 보이스", "EVP 녹음", "영혼의 목소리",
    "靈異聲音", "電子語音現象", "鬼魂語音"
]

def get_sources():
    # 各国のGoogle News RSSとRedditを統合
    base_url = "https://news.google.com/rss/search?q={query}&hl={hl}&gl={gl}&ceid={ceid}"
    queries = "+OR+".join(KEYWORDS[:8]) # 主要キーワードで構成
    sources = [
        "https://www.reddit.com/r/EVP/new/.rss",
        "https://www.reddit.com/r/SpiritBox/new/.rss",
        base_url.format(query=queries, hl="ja", gl="JP", ceid="JP:ja"), # 日本
        base_url.format(query=queries, hl="ko", gl="KR", ceid="KR:ko"), # 韓国
        base_url.format(query=queries, hl="en", gl="US", ceid="US:en"), # 米国
        base_url.format(query=queries, hl="zh-TW", gl="TW", ceid="TW:zh-Hant") # 台湾
    ]
    return sources

# 翻訳機の設定（自動検知 → 日本語）
translator = GoogleTranslator(source='auto', target='ja')

def crawl():
    new_posts = []
    print("📡 全言語・全周波数をスキャン中...")
    
    for url in get_sources():
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            try:
                # どんな言語の記事も日本語に変換
                translated_title = translator.translate(entry.title)
                
                new_posts.append({
                    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "source": "Global Observation Network",
                    "text": translated_title,
                    "url": entry.link
                })
            except:
                continue

    if not os.path.exists("index.html"): return

    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 蓄積ロジック
    current_json_match = re.search(r'const posts = (\[.*?\]);', content, flags=re.DOTALL)
    old_posts = json.loads(current_json_match.group(1)) if current_json_match else []

    # 重複排除とマージ
    existing_urls = {p['url'] for p in old_posts}
    combined_posts = [p for p in new_posts if p['url'] not in existing_urls] + old_posts
    
    # 最大200件で古いものをカット
    final_posts = combined_posts[:200]

    json_str = json.dumps(final_posts, ensure_ascii=False, indent=4)
    new_content = re.sub(r'const posts = \[.*?\];', f'const posts = {json_str};', content, flags=re.DOTALL)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ 記録完了。総アーカイブ数: {len(final_posts)}")

if __name__ == "__main__":
    crawl()
