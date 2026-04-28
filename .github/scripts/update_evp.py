import feedparser
from deep_translator import GoogleTranslator
import datetime
import json
import re
import os
import time

# 全世界・全領域を網羅する多言語キーワード群
# 超心理学(Parapsychology)、ITC、超常現象、霊的調査など
KEYWORDS = (
    "EVP OR 'Spirit Box' OR 'Ghost Voice' OR ITC OR 'Instrumental Transcommunication' OR "
    "Parapsychology OR Paranormal OR 'Psychical Research' OR 'Electronic Voice Phenomena' OR "
    "電子音声現象 OR 心霊研究 OR 超心理学 OR 不可解 OR スピリットボックス OR "
    "심령 OR 고스트보이스 OR 초심리학 OR '전자 음성 현상' OR "
    "靈異聲音 OR '電子語音現象' OR 超心理學 OR '鬼魂語音' OR "
    "Paranormale OR 'Voix électronique' OR 'Voz electrónica' OR 'Fenomeni voce elettronica'"
)

def get_sources():
    base_url = "https://news.google.com/rss/search?q={query}&hl={hl}&gl={gl}&ceid={ceid}"
    # 各国の主要ノード（日本、韓国、台湾、米国、フランス、ドイツ、イタリア、スペイン）
    regions = [
        {"hl": "ja", "gl": "JP", "ceid": "JP:ja"},
        {"hl": "ko", "gl": "KR", "ceid": "KR:ko"},
        {"hl": "zh-TW", "gl": "TW", "ceid": "TW:zh-Hant"},
        {"hl": "en", "gl": "US", "ceid": "US:en"},
        {"hl": "fr", "gl": "FR", "ceid": "FR:fr"},
        {"hl": "de", "gl": "DE", "ceid": "DE:de"},
        {"hl": "it", "gl": "IT", "ceid": "IT:it"},
        {"hl": "es", "gl": "ES", "ceid": "ES:es"}
    ]
    
    sources = [
        "https://www.reddit.com/r/EVP/new/.rss",
        "https://www.reddit.com/r/SpiritBox/new/.rss",
        "https://www.reddit.com/r/Paranormal/new/.rss",
        "https://www.reddit.com/r/Parapsychology/new/.rss"
    ]
    
    for r in regions:
        sources.append(base_url.format(query=KEYWORDS, **r))
    return sources

translator = GoogleTranslator(source='auto', target='ja')

def crawl():
    new_posts = []
    print("📡 全世界・全次元の周波数を広域スキャン中...")
    
    for url in get_sources():
        try:
            feed = feedparser.parse(url)
            # 各ソースから上位15件をサンプリング
            for entry in feed.entries[:15]:
                try:
                    time.sleep(0.3) 
                    text = translator.translate(entry.title)
                    new_posts.append({
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "source": "Global Network Node",
                        "text": text,
                        "url": entry.link
                    })
                except: continue
        except: continue

    if not os.path.exists("index.html"): return
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'const posts = (\[.*?\]);', content, flags=re.DOTALL)
    old_posts = json.loads(match.group(1)) if match else []
    
    urls = {p['url'] for p in old_posts}
    # 200件まで蓄積（新着優先）
    final_posts = ([p for p in new_posts if p['url'] not in urls] + old_posts)[:200]

    json_str = json.dumps(final_posts, ensure_ascii=False, indent=4)
    new_content = re.sub(r'const posts = \[.*?\];', f'const posts = {json_str};', content, flags=re.DOTALL)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ スキャン完了。現在 {len(final_posts)} 件の記録をアーカイブ。")

if __name__ == "__main__":
    crawl()
