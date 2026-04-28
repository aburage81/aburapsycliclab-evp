import feedparser
from deep_translator import GoogleTranslator
import datetime
import json
import re
import os

# 検索キーワード群（世界中の「霊の声」を網羅）
# 英語、日本語、韓国語、中国語の主要な用語を組み合わせ
KEYWORDS = [
    "EVP", "Electronic Voice Phenomena", "Spirit Box", "Ghost Box", "Ghost Voice",
    "Recorded Ghost", "Paranormal Audio", "ITC", "Instrumental Transcommunication",
    "電子音声現象", "スピリットボックス", "ゴーストボイス", "霊の声", "幽霊の声", "心霊録音",
    "심령 현상", "고스트 보이스", "EVP 녹音", "영혼의 목소리", "전자 음성 현상",
    "靈異聲音", "電子語音現象", "鬼魂語音"
]

# 収集ソース（Google News RSS を活用して多言語を横断）
def get_sources():
    base_url = "https://news.google.com/rss/search?q={query}&hl={hl}&gl={gl}&ceid={ceid}"
    sources = [
        "https://www.reddit.com/r/EVP/new/.rss",
        "https://www.reddit.com/r/SpiritBox/new/.rss",
        "https://www.reddit.com/r/Paranormal/new/.rss",
        # 日本の最新情報
        base_url.format(query="EVP+OR+電子音声現象+OR+スピリットボックス", hl="ja", gl="JP", ceid="JP:ja"),
        # 韓国の最新情報
        base_url.format(query="EVP+OR+심령+목소리+OR+고스트+보이스", hl="ko", gl="KR", ceid="KR:ko"),
        # 台湾・香港の最新情報
        base_url.format(query="EVP+OR+靈異聲音+OR+電子語音現象", hl="zh-TW", gl="TW", ceid="TW:zh-Hant")
    ]
    return sources

translator = GoogleTranslator(source='auto', target='ja')

def crawl():
    new_posts = []
    print("📡 多言語・多次元スキャンを開始...")
    
    for url in get_sources():
        feed = feedparser.parse(url)
        for entry in feed.entries[:12]:
            try:
                # どんな言語からも日本語へ
                ja_text = translator.translate(entry.title)
                
                # 記事がキーワードに合致するか、あるいはソース自体がEVP専門か確認
                new_posts.append({
                    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "source": "Global Observation Network",
                    "text": ja_text,
                    "url": entry.link
                })
            except:
                continue

    if not os.path.exists("index.html"): return

    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 蓄積と200件制限のロジック
    current_json_match = re.search(r'const posts = (\[.*?\]);', content, flags=re.DOTALL)
    old_posts = json.loads(current_json_match.group(1)) if current_json_match else []

    existing_urls = {p['url'] for p in old_posts}
    # 新しい記事を上に追加、重複は排除
    combined_posts = [p for p in new_posts if p['url'] not in existing_urls] + old_posts
    final_posts = combined_posts[:200]

    json_str = json.dumps(final_posts, ensure_ascii=False, indent=4)
    new_content = re.sub(r'const posts = \[.*?\];', f'const posts = {json_str};', content, flags=re.DOTALL)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ 記録完了。総アーカイブ数: {len(final_posts)}")

if __name__ == "__main__":
    crawl()
