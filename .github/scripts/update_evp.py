import feedparser
from deep_translator import GoogleTranslator
import datetime
import json
import re
import os
import time

# 全世界・全領域クエリ
KEYWORDS = (
    "EVP OR 'Spirit Box' OR 'Ghost Voice' OR ITC OR 'Instrumental Transcommunication' OR "
    "Parapsychology OR Paranormal OR 'Psychical Research' OR 'Electronic Voice Phenomena' OR "
    "電子音声現象 OR 心霊研究 OR 超心理学 OR 不可解 OR スピリットボックス OR "
    "심령 OR 고스트보イス OR 초심리학 OR '전자 음성 현상' OR "
    "靈異聲音 OR '電子語音現象' OR 超心理學 OR '鬼魂語音'"
)

def get_sources():
    base_url = "https://news.google.com/rss/search?q={query}&hl={hl}&gl={gl}&ceid={ceid}"
    regions = [
        {"hl": "ja", "gl": "JP", "ceid": "JP:ja"},
        {"hl": "ko", "gl": "KR", "ceid": "KR:ko"},
        {"hl": "zh-TW", "gl": "TW", "ceid": "TW:zh-Hant"},
        {"hl": "en", "gl": "US", "ceid": "US:en"},
        {"hl": "fr", "gl": "FR", "ceid": "FR:fr"},
        {"hl": "de", "gl": "DE", "ceid": "DE:de"}
    ]
    sources = [
        "https://www.reddit.com/r/EVP/new/.rss",
        "https://www.reddit.com/r/SpiritBox/new/.rss",
        "https://www.reddit.com/r/Paranormal/new/.rss"
    ]
    for r in regions:
        sources.append(base_url.format(query=KEYWORDS, **r))
    return sources

translator = GoogleTranslator(source='auto', target='ja')

def generate_tags(text):
    """内容から自動でタグを生成する"""
    tags = []
    # カテゴリ判別
    if any(x in text for x in ["音声", "録音", "声", "Voice", "Audio", "EVP", "スピリットボックス"]): tags.append("#Audio")
    if any(x in text for x in ["研究", "検証", "超心理学", "学", "Research", "Lab", "ITC"]): tags.append("#Research")
    if any(x in text for x in ["不可解", "超常", "怪異", "Paranormal", "Ghost", "幽霊"]): tags.append("#Paranormal")
    # 地域判別
    if any(x in text for x in ["韓国", "ソウル", "Korea", "심령"]): tags.append("#Korea")
    if any(x in text for x in ["台湾", "中国", "香港", "Taiwan", "China", "靈異"]): tags.append("#Asia")
    if any(x in text for x in ["日本", "東京", "Japan"]): tags.append("#Japan")
    
    return " ".join(tags) if tags else "#Unknown"

def crawl():
    new_posts = []
    print("📡 自動タグ付けモードでスキャン中...")
    
    for url in get_sources():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:12]:
                try:
                    time.sleep(0.3) 
                    translated_text = translator.translate(entry.title)
                    
                    # タグを生成してテキストの先頭に付与
                    tags = generate_tags(translated_text + entry.title)
                    tagged_text = f"{tags} {translated_text}"
                    
                    new_posts.append({
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "source": "Global Node",
                        "text": tagged_text,
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
    final_posts = ([p for p in new_posts if p['url'] not in urls] + old_posts)[:200]

    json_str = json.dumps(final_posts, ensure_ascii=False, indent=4)
    new_content = re.sub(r'const posts = \[.*?\];', f'const posts = {json_str};', content, flags=re.DOTALL)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ 完了。タグ付き記事を保存しました。")

if __name__ == "__main__":
    crawl()
  
  
