import feedparser
from deep_translator import GoogleTranslator
import datetime
from datetime import timedelta, timezone
import json
import re
import os
import time
from functools import lru_cache

# ==================== 設定 ====================
MAX_PER_SOURCE = 8          # 1ソースあたりの取得上限（高頻度対応）
MAX_TOTAL_POSTS = 250       # HTML保持上限
SLEEP_BETWEEN = 1.5         # 翻訳時の待機秒（ブロック対策）

translator = GoogleTranslator(source='auto', target='ja')

@lru_cache(maxsize=800)
def safe_translate(text):
    if not text or len(text) < 3: return text
    try:
        time.sleep(SLEEP_BETWEEN)
        return translator.translate(text)
    except:
        return text

def get_sources():
    return [
        # === Reddit（高活性）===
        "https://www.reddit.com/r/EVP/new/.rss",
        "https://www.reddit.com/r/Paranormal/new/.rss",
        "https://www.reddit.com/r/Ghosts/new/.rss",
        "https://www.reddit.com/r/GhostAdventures/new/.rss",
        "https://www.reddit.com/r/MandelaEffect/new/.rss",
        "https://www.reddit.com/r/HighStrangeness/new/.rss",
        
        # === 国際フォーラム・その他 ===
        "https://boards.4channel.org/x/index.rss",           # /x/ Paranormal
        "https://www.abovetopsecret.com/rss.php",           # AboveTopSecret
        
        # === YouTube Paranormal（RSS対応）===
        # 人気EVP/心霊チャンネル（必要に応じて追加）
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC-CkanqtNAoCmIWkyG4nmlQ",  # Ghost Hunters公式例
        # 他のチャンネルは channel_id を調べて追加可能
        
        # === 多言語Google News ===
        "https://news.google.com/rss/search?q=EVP+OR+Electronic+Voice+Phenomena+OR+心霊+OR+幽霊+OR+靈異&hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=心霊+OR+EVP+OR+幽体離脱&hl=ja&gl=JP&ceid=JP:ja",
        "https://news.google.com/rss/search?q=심령+OR+EVP&hl=ko&gl=KR&ceid=KR:ko",
        "https://news.google.com/rss/search?q=靈異+OR+曼德拉效應&hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
    ]

def generate_tags(text):
    low = text.lower()
    tags = []
    if any(k in low for k in ["evp", "voice", "録音", "声", "electronic voice"]): tags.append("#Audio")
    if any(k in low for k in ["orb", "オーブ", "光球"]): tags.append("#Orb")
    if any(k in low for k in ["mandela", "マンデラ"]): tags.append("#Mandela")
    if any(k in low for k in ["nhi", "uap", "非人類"]): tags.append("#NHI")
    if any(k in low for k in ["obe", "離脱", "幽体"]): tags.append("#OBE")
    if any(k in low for k in ["poltergeist", "物理", "ポルター"]): tags.append("#Physical")
    return " ".join(tags) if tags else "#Paranormal"

def crawl():
    jst = timezone(timedelta(hours=9), 'JST')
    now_str = datetime.datetime.now(jst).strftime("%Y-%m-%d %H:%M")
    
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")

    new_posts = []
    print(f"🌍 世界中高頻度スキャン開始 - {now_str}")

    for url in get_sources():
        print(f"🔍 {url}")
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:MAX_PER_SOURCE]:
                title = entry.get('title', '')
                link = entry.get('link', '')
                if not title or not link: continue

                translated = safe_translate(title)
                tags = generate_tags(translated + title)

                new_posts.append({
                    "date": now_str,
                    "source": "Global Node",
                    "text": f"{tags} {translated}",
                    "url": link,
                    "media": []   # 将来：YouTubeはvideo、音声はaudioに拡張可能
                })
        except Exception as e:
            print(f"   ⚠️ エラー: {e}")

    # === HTML更新 ===
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    posts_match = re.search(r'const posts = (\[[\s\S]*?\]);', content, re.DOTALL)
    if posts_match:
        old_posts = json.loads(posts_match.group(1))
        existing_urls = {p.get('url') for p in old_posts if p.get('url')}
        
        unique_new = [p for p in new_posts if p['url'] not in existing_urls]
        final_posts = unique_new + old_posts
        final_posts = final_posts[:MAX_TOTAL_POSTS]

        json_str = json.dumps(final_posts, ensure_ascii=False, indent=4)
        content = content.replace(posts_match.group(0), f'const posts = {json_str};')

    content = re.sub(r'const lastUpdated = ".*?";', 
                     f'const lastUpdated = "{now_str}";', content)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"✅ 世界中更新完了: +{len(unique_new)}件（合計 {len(final_posts)}件）")

if __name__ == "__main__":
    crawl()


