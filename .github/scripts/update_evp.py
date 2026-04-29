import feedparser
from deep_translator import GoogleTranslator
import datetime
import json
import re
import os
import time

# キーワード強化：OBE, ESP, Psy, 超能力、体外離脱などのバリエーション
KEYWORDS = (
    "EVP OR 'Spirit Box' OR ITC OR 'Ghost Voice' OR "
    "Poltergeist OR 'Haunted Doll' OR 'Cursed Object' OR "
    "orb OR nhi OR 'Mandela Effect' OR "
    "OBE OR 'Out of Body Experience' OR ESP OR 'Extra Sensory Perception' OR Psy OR Psychokinesis OR "
    "電子音声現象 OR ポルターガイスト OR 呪物 OR オーブ OR 非人類知性 OR マンデラエフェクト OR "
    "体外離脱 OR 幽体離脱 OR 超能力 OR 超感覚的知覚 OR 念力 OR "
    "심령 OR '유체 이탈' OR '초능력' OR 'ESP' OR "
    "靈異聲音 OR '出體経験' OR '超能力' OR '曼德拉效應' OR "
    "Внетелесный опыт OR Телепатия OR Психокинез OR Полтергейст"
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
        "https://www.reddit.com/r/MandelaEffect/new/.rss",
        "https://www.reddit.com/r/OutOBodies/new/.rss", # OBE専門
        "https://www.reddit.com/r/psi/new/.rss"           # Psy/超能力専門
    ]
    for r in regions:
        sources.append(base_url.format(query=KEYWORDS, **r))
    return sources

translator = GoogleTranslator(source='auto', target='ja')

def generate_tags(text):
    """内容から自動でタグを生成する（OBE/ESP/Psyの追加）"""
    tags = []
    low_text = text.lower()
    
    # カテゴリ・現象
    if any(x in low_text for x in ["音声", "録音", "声", "evp", "voice", "audio"]): tags.append("#Audio")
    if any(x in low_text for x in ["人形", "ドール", "doll", "呪物", "object", "cursed"]): tags.append("#Object")
    if any(x in low_text for x in ["ポルターガイスト", "物理", "poltergeist"]): tags.append("#Physical")
    if any(x in low_text for x in ["オーブ", "orb", "光球"]): tags.append("#Orb")
    if any(x in low_text for x in ["nhi", "非人類", "intelligence", "uap", "ufo"]): tags.append("#NHI")
    if any(x in low_text for x in ["マンデラ", "mandela", "記憶", "memory"]): tags.append("#Mandela")
    
    # OBE / ESP / Psy タグ
    if any(x in low_text for x in ["離脱", "obe", "out of body", "体外", "幽体"]): tags.append("#OBE")
    if any(x in low_text for x in ["超能力", "esp", "psy", "念力", "テレパシー", "感覚"]): tags.append("#Psy")
    
    if any(x in low_text for x in ["研究", "検証", "research", "lab", "超心理"]): tags.append("#Research")
    
    return " ".join(tags) if tags else "#Paranormal"

def crawl():
    new_posts = []
    print("📡 脂心霊パラノーマルBOT 超感覚・体外離脱を含む全方位スキャン開始...")
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
    print(f"✅ 更新成功。全 {len(final_posts)} 件をアーカイブ中。")

if __name__ == "__main__":
    crawl()
