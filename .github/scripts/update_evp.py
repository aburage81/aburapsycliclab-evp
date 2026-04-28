import feedparser
from deep_translator import GoogleTranslator
import datetime
import json
import re
import os
import time

# キーワード設定（霊、声、録音、対話）
KEYWORDS = "EVP+OR+Ghost+Voice+OR+Spirit+Box+OR+心霊+OR+霊の声+OR+심령+OR+목소리"

def get_sources():
    base_url = "https://news.google.com/rss/search?q={query}&hl={hl}&gl={gl}&ceid={ceid}"
    return [
        "https://www.reddit.com/r/EVP/new/.rss",
        "https://www.reddit.com/r/SpiritBox/new/.rss",
        base_url.format(query=KEYWORDS, hl="ja", gl="JP", ceid="JP:ja"),
        base_url.format(query=KEYWORDS, hl="ko", gl="KR", ceid="KR:ko"),
        base_url.format(query=KEYWORDS, hl="en", gl="US", ceid="US:en")
    ]

translator = GoogleTranslator(source='auto', target='ja')

def crawl():
    new_posts = []
    print("📡 世界の信号をスキャン中...")
    for url in get_sources():
        feed = feedparser.parse(url)
        for entry in feed.entries[:8]:
            try:
                time.sleep(0.5) # 負荷軽減
                text = translator.translate(entry.title)
                new_posts.append({
                    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "source": "Global Observation",
                    "text": text,
                    "url": entry.link
                })
            except: continue

    if not os.path.exists("index.html"): return

    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'const posts = (\[.*?\]);', content, flags=re.DOTALL)
    old_posts = json.loads(match.group(1)) if match else []
    
    urls = {p['url'] for p in old_posts}
    final_posts = ([p for p in new_posts if p['url'] not in urls] + old_posts)[:200]

    json_str = json.dumps(final_posts, ensure_ascii=False, indent=4)
    new_content = re.sub(r'const posts = \[.*?\];', f'const posts = {json_str};', content, flags=re.DOTALL)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ 更新成功: 現在 {len(final_posts)} 件")

if __name__ == "__main__":
    crawl()


