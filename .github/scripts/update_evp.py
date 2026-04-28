import feedparser
from deep_translator import GoogleTranslator
import datetime
import json
import re
import os
import time

# 検索ワード：アジア圏と言語を重視
KEYWORDS = "EVP+OR+Ghost+Voice+OR+Spirit+Box+OR+心霊+OR+霊の声+OR+심령+OR+고스트+보이스+OR+靈異聲音"

def get_sources():
    base_url = "https://news.google.com/rss/search?q={query}&hl={hl}&gl={gl}&ceid={ceid}"
    return [
        "https://www.reddit.com/r/EVP/new/.rss",
        "https://www.reddit.com/r/SpiritBox/new/.rss",
        base_url.format(query=KEYWORDS, hl="ja", gl="JP", ceid="JP:ja"), # 日本
        base_url.format(query=KEYWORDS, hl="ko", gl="KR", ceid="KR:ko"), # 韓国
        base_url.format(query=KEYWORDS, hl="zh-TW", gl="TW", ceid="TW:zh-Hant"), # 台湾
        base_url.format(query=KEYWORDS, hl="en", gl="US", ceid="US:en") # 欧米
    ]

translator = GoogleTranslator(source='auto', target='ja')

def crawl():
    new_posts = []
    print("📡 スキャン開始...")
    for url in get_sources():
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            try:
                time.sleep(0.5) 
                text = translator.translate(entry.title)
                new_posts.append({
                    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "source": "Global Node",
                    "text": text,
                    "url": entry.link
                })
            except: continue

    if not os.path.exists("index.html"): return
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 蓄積の核心部分：今のデータを消さずに合体させる
    match = re.search(r'const posts = (\[.*?\]);', content, flags=re.DOTALL)
    old_posts = json.loads(match.group(1)) if match else []
    
    urls = {p['url'] for p in old_posts}
    # 新しいものを上に、重複は捨てて最大200件
    final_posts = ([p for p in new_posts if p['url'] not in urls] + old_posts)[:200]

    json_str = json.dumps(final_posts, ensure_ascii=False, indent=4)
    new_content = re.sub(r'const posts = \[.*?\];', f'const posts = {json_str};', content, flags=re.DOTALL)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ 更新成功。総件数: {len(final_posts)}")

if __name__ == "__main__":
    crawl()
