import feedparser
from deep_translator import GoogleTranslator
import datetime
import json
import re
import os
import time

# キーワード強化：呪物、ホーンテッドドール、ポルターガイスト、ロシア語・各言語対応
KEYWORDS = (
    "EVP OR 'Spirit Box' OR ITC OR 'Ghost Voice' OR "
    "Poltergeist OR 'Haunted Doll' OR 'Cursed Object' OR 'Possessed Item' OR "
    "電子音声現象 OR スピリットボックス OR ポルターガイスト OR 呪物 OR 呪いの人形 OR "
    "심령 OR 폴터가イスト OR '저주받은 인형' OR '유령 인형' OR "
    "靈異聲音 OR 跑馬燈現象 OR '鬧鬼娃娃' OR '受詛咒的物品' OR "
    "Полтергейст OR 'Проклятый объект' OR 'Одержимая кукла' OR ФЭГ"
)

def get_sources():
    base_url = "https://news.google.com/rss/search?q={query}&hl={hl}&gl={gl}&ceid={ceid}"
    # ロシア(RU)を含む、全世界の重要ノード
    regions = [
        {"hl": "ja", "gl": "JP", "ceid": "JP:ja"},
        {"hl": "ko", "gl": "KR", "ceid": "KR:ko"},
        {"hl": "zh-TW", "gl": "TW", "ceid": "TW:zh-Hant"},
        {"hl": "en", "gl": "US", "ceid": "US:en"},
        {"hl": "ru", "gl": "RU", "ceid": "RU:ru"}, # ロシア圏追加
        {"hl": "en", "gl": "GB", "ceid": "GB:en"}, # 英国（ホーンテッドドールの本場）
        {"hl": "de", "gl": "DE", "ceid": "DE:de"}
    ]
    sources = [
        "https://www.reddit.com/r/EVP/new/.rss",
        "https://www.reddit.com/r/Paranormal/new/.rss",
        "https://www.reddit.com/r/HauntedObjects/new/.rss", # 呪物専門
        "https://www.reddit.com/r/Poltergeist/new/.rss"    # ポルターガイスト専門
    ]
    for r in regions:
        sources.append(base_url.format(query=KEYWORDS, **r))
    return sources

translator = GoogleTranslator(source='auto', target='ja')

def generate_tags(text):
    """内容から自動でタグを生成する（呪物・人形・現象の追加）"""
    tags = []
    # 現象・カテゴリ
    if any(x in text for x in ["音声", "録音", "声", "EVP", "Voice", "Audio"]): tags.append("#Audio")
    if any(x in text for x in ["人形", "ドール", "Doll", "кукла"]): tags.append("#Doll")
    if any(x in text for x in ["呪物", "呪い", "Cursed", "Possessed", "物"]): tags.append("#Object")
    if any(x in text for x in ["ポルターガイスト", "物理", "Poltergeist"]): tags.append("#Physical")
    if any(x in text for x in ["研究", "超心理学", "検証", "Research", "Lab"]): tags.append("#Research")
    
    # 地域
    if any(x in text for x in ["韓国", "Korea"]): tags.append("#Korea")
    if any(x in text for x in ["ロシア", "Russia", "RU", "Полтер"]): tags.append("#Russia")
    if any(x in text for x in ["台湾", "中国", "Asia"]): tags.append("#Asia")
    
    return " ".join(tags) if tags else "#Paranormal"

def crawl():
    new_posts = []
    print("📡 呪物・物理現象を含む全領域スキャンを開始...")
    for url in get_sources():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                try:
                    time.sleep(0.3)
                    translated_text = translator.translate(entry.title)
                    tags = generate_tags(translated_text + entry.title)
                    # デザイン維持のため、テキストの先頭にタグを埋め込む
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
    print(f"✅ 更新完了。全 {len(final_posts)} 件をアーカイブ。")

if __name__ == "__main__":
    crawl()
