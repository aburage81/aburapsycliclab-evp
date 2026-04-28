import feedparser
from deep_translator import GoogleTranslator
import datetime
import json
import re
import os
import time

# キーワード強化：orb(オーブ)とnhi(非人類知性)を追加
KEYWORDS = (
    "EVP OR 'Spirit Box' OR ITC OR 'Ghost Voice' OR "
    "Poltergeist OR 'Haunted Doll' OR 'Cursed Object' OR "
    "orb OR nhi OR 'Non-Human Intelligence' OR "
    "電子音声現象 OR ポルターガイスト OR 呪物 OR オーブ OR 非人類知性 OR "
    "심령 OR 폴터가이스트 OR 오브 OR '비인류 지성' OR "
    "靈異聲音 OR 跑馬燈現象 OR 光球 OR '非人類知性'"
)

def get_sources():
    base_url = "https://news.google.com/rss/search?q={query}&hl={hl}&gl={gl}&ceid={ceid}"
    regions = [
        {"hl": "ja", "gl": "JP", "ceid": "JP:ja"},
        {"hl": "ko", "gl": "KR", "ceid": "KR:ko"},
        {"hl": "zh-TW", "gl": "TW", "ceid": "TW:zh-Hant"},
        {"hl": "en", "gl": "US", "ceid": "US:en"},
        {"hl": "ru", "gl": "RU", "ceid": "RU:ru"},
        {"hl": "en", "gl": "GB", "ceid": "GB:en"}
    ]
    sources = [
        "https://www.reddit.com/r/EVP/new/.rss",
        "https://www.reddit.com/r/Paranormal/new/.rss",
        "https://www.reddit.com/r/UFOs/new/.rss" # NHI関連でUFOサブレを追加
    ]
    for r in regions:
        sources.append(base_url.format(query=KEYWORDS, **r))
    return sources

translator = GoogleTranslator(source='auto', target='ja')

def generate_tags(text):
    """内容から自動でタグを生成する"""
    tags = []
    # カテゴリ・現象
    if any(x in text.lower() for x in ["音声", "録音", "声", "evp", "voice", "audio"]): tags.append("#Audio")
    if any(x in text.lower() for x in ["人形", "ドール", "doll", "呪物", "object", "cursed"]): tags.append("#Object")
    if any(x in text.lower() for x in ["ポルターガイスト", "物理", "poltergeist"]): tags.append("#Physical")
    if any(x in text.lower() for x in ["オーブ", "orb", "光球"]): tags.append("#Orb")
    if any(x in text.lower() for x in ["nhi", "非人類", "intelligence", "uap", "ufo"]): tags.append("#NHI")
    if any(x in text.lower() for x in ["研究", "検証", "research", "lab"]): tags.append("#Research")
    
    return " ".join(tags) if tags else "#Paranormal"

def crawl():
    new_posts = []
    print("📡 脂心霊パラノーマルBOT 広域スキャン開始...")
    for url in get_sources():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                try:
                    time.sleep(0.3)
                    translated_text = translator.translate(entry.title)
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
    print(f"✅ 更新成功。現在 {len(final_posts)} 件をアーカイブ。")

if __name__ == "__main__":
    crawl()
  
