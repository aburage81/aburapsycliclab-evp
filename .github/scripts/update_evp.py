
import feedparser
from deep_translator import GoogleTranslator
import datetime
from datetime import timedelta, timezone
import json
import re
import os
import time

# ==================== 設定 ====================
MAX_PER_SOURCE = 6
MAX_TOTAL = 250
SLEEP_TIME = 1.8

translator = GoogleTranslator(source='auto', target='ja')

def safe_translate(text):
    if not text or len(text.strip()) < 2:
        return text
    try:
        time.sleep(SLEEP_TIME)
        return translator.translate(text)
    except Exception as e:
        print(f"翻訳スキップ: {e}")
        return text

def get_sources():
    return [
        "https://www.reddit.com/r/EVP/new/.rss",
        "https://www.reddit.com/r/Paranormal/new/.rss",
        "https://www.reddit.com/r/Ghosts/new/.rss",
        "https://www.reddit.com/r/MandelaEffect/new/.rss",
        "https://boards.4channel.org/x/index.rss",
        "https://news.google.com/rss/search?q=EVP+OR+心霊+OR+幽霊&hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=心霊+OR+EVP&hl=ja&gl=JP&ceid=JP:ja",
    ]

def generate_tags(text):
    low = text.lower()
    tags = []
    if any(k in low for k in ["evp", "voice", "electronic voice", "録音", "声"]): tags.append("#Audio")
    if any(k in low for k in ["orb", "オーブ", "光球"]): tags.append("#Orb")
    if any(k in low for k in ["mandela", "マンデラ"]): tags.append("#Mandela")
    if any(k in low for k in ["nhi", "非人類", "uap"]): tags.append("#NHI")
    return " ".join(tags) if tags else "#Paranormal"

def crawl():
    jst = timezone(timedelta(hours=9), 'JST')
    now_str = datetime.datetime.now(jst).strftime("%Y-%m-%d %H:%M")
    
    print(f"🌍 update_evp.py 実行開始 - {now_str}")
    print(f"作業ディレクトリ: {os.getcwd()}")
    
    html_path = "index.html"

    if not os.path.exists(html_path):
        print(f"❌ index.html が見つかりません")
        exit(1)

    new_posts = []

    for url in get_sources():
        print(f"🔍 取得中: {url}")
        try:
            feed = feedparser.parse(url, request_headers={'User-Agent': 'Mozilla/5.0 (ParanormalBot)'})
            for entry in feed.entries[:MAX_PER_SOURCE]:
                title = entry.get('title', '').strip()
                link = entry.get('link', '')
                if not title or not link:
                    continue

                translated = safe_translate(title)
                tags = generate_tags(translated + " " + title)

                new_posts.append({
                    "date": now_str,
                    "source": "Global Node",
                    "text": f"{tags} {translated}",
                    "url": link,
                    "media": []
                })
        except Exception as e:
            print(f"   ⚠️ エラー: {e}")

    # HTML更新
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    posts_match = re.search(r'const posts = (\[[\s\S]*?\]);', content, re.DOTALL)
    if posts_match:
        old_posts = json.loads(posts_match.group(1))
        existing = {p.get('url') for p in old_posts if p.get('url')}
        
        unique_new = [p for p in new_posts if p['url'] not in existing]
        final_posts = unique_new + old_posts
        final_posts = final_posts[:MAX_TOTAL]

        json_str = json.dumps(final_posts, ensure_ascii=False, indent=4)
        content = content.replace(posts_match.group(0), f'const posts = {json_str};')
        print(f"✅ 新着 {len(unique_new)}件追加（合計 {len(final_posts)}件）")
    else:
        print("❌ posts配列が見つかりません")

    # 更新時刻
    content = re.sub(r'const lastUpdated = ".*?";', f'const lastUpdated = "{now_str}";', content)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("🎉 update_evp.py 完了")

if __name__ == "__main__":
    crawl()
