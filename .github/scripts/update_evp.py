import feedparser
from deep_translator import GoogleTranslator
import datetime
from datetime import timedelta, timezone
import json
import re
import os
import time
import random
from functools import lru_cache

# ====================== 画像バンク（公開・安全なURLのみ） ======================
IMAGE_BANK = {
    "mudang": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Korean_shaman_ritual.jpg/800px-Korean_shaman_ritual.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/7/7d/Mudang_performing_gut.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Korea-Mudang_performing_gut-01.jpg/800px-Korea-Mudang_performing_gut-01.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Shaman_at_Lotte_World_Folk_Museum.jpg/800px-Shaman_at_Lotte_World_Folk_Museum.jpg"
    ],
    "gwishin": [
        "https://upload.wikimedia.org/wikipedia/commons/9/9f/Korean_ghost_traditional.jpg",
        "https://i.imgur.com/CheonyeoGwishin.jpg",  # 必要に応じて実際の安定URLに変更
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Korean_ghost_folklore.jpg/800px-Korean_ghost_folklore.jpg"
    ],
    "taiwan_ghost": [
        "https://upload.wikimedia.org/wikipedia/commons/3/3f/Taiwan_Ghost_Month_altar.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Ghost_Festival_Taiwan.jpg/800px-Ghost_Festival_Taiwan.jpg"
    ],
    "jitong": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Jitong_Taiwan_ritual.jpg/800px-Jitong_Taiwan_ritual.jpg"
    ],
    "mazu": [
        "https://upload.wikimedia.org/wikipedia/commons/0/0b/Mazu_statue_Taiwan.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Mazu_procession_Taiwan.jpg/800px-Mazu_procession_Taiwan.jpg"
    ],
    "default": [
        "https://picsum.photos/id/1015/800/600",
        "https://picsum.photos/id/106/800/600",
        "https://picsum.photos/id/201/800/600"
    ]
}

def get_relevant_image(text):
    """テキスト内容から韓国・台湾ホラー関連画像を自動選択"""
    low = text.lower()
    if any(x in low for x in ["mudang", "gut", "shaman", "무당", "굿", "무속"]):
        return random.choice(IMAGE_BANK["mudang"])
    elif any(x in low for x in ["gwishin", "귀신", "korean ghost", "処女鬼神"]):
        return random.choice(IMAGE_BANK["gwishin"])
    elif any(x in low for x in ["鬼月", "ghost month", "hungry ghost", "台灣鬼"]):
        return random.choice(IMAGE_BANK["taiwan_ghost"])
    elif any(x in low for x in ["jitong", "乩童", "童乩"]):
        return random.choice(IMAGE_BANK["jitong"])
    elif any(x in low for x in ["mazu", "媽祖", "マズ"]):
        return random.choice(IMAGE_BANK["mazu"])
    return random.choice(IMAGE_BANK["default"])

# --- 翻訳設定 ---
translator = GoogleTranslator(source='auto', target='ja')

@lru_cache(maxsize=500)
def safe_translate(text):
    if not text:
        return ""
    try:
        time.sleep(1.0)  # レート制限対策
        return translator.translate(text)
    except Exception:
        return text

# --- RSSソース（韓国・台湾強化） ---
def get_sources():
    sources = [
        "https://www.reddit.com/r/EVP/new/.rss",
        "https://www.reddit.com/r/Paranormal/new/.rss",
        "https://www.reddit.com/r/MandelaEffect/new/.rss",
        # 韓国シャーマニズム・心霊
        "https://news.google.com/rss/search?q=무당+굿+귀신+심령&hl=ko&gl=KR&ceid=KR:ko",
        "https://news.google.com/rss/search?q=mudang+gut+gwishin&hl=en&gl=US&ceid=US:en",
        # 台湾心霊・シャーマニズム
        "https://news.google.com/rss/search?q=鬼月+乩童+媽祖+靈異+心霊&hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
        "https://news.google.com/rss/search?q=taiwan+ghost+month+jitong+mazu&hl=en&gl=US&ceid=US:en",
    ]
    return sources

def generate_tags(text):
    low = text.lower()
    tags = []
    if any(k in low for k in ["evp", "音声", "録音", "voice"]):
        tags.append("#Audio")
    if any(k in low for k in ["무당", "gut", "shaman", "mudang", "굿", "무속"]):
        tags.append("#ShamanKR")
    if any(k in low for k in ["귀신", "gwishin", "ghost", "幽霊", "靈異"]):
        tags.append("#Ghost")
    if any(k in low for k in ["鬼月", "jitong", "乩童", "台灣鬼"]):
        tags.append("#TaiwanGhost")
    if any(k in low for k in ["mazu", "媽祖"]):
        tags.append("#Mazu")
    if any(k in low for k in ["mandela", "記憶"]):
        tags.append("#Mandela")
    if any(k in low for k in ["orb", "오브", "光球"]):
        tags.append("#Orb")
    return " ".join(tags) if tags else "#Paranormal"

def crawl():
    jst = timezone(timedelta(hours=9), 'JST')
    now_str = datetime.datetime.now(jst).strftime("%Y-%m-%d %H:%M")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    html_path = os.path.join(repo_root, "index.html")

    new_posts = []
    print(f"📡 スキャン開始 (JST: {now_str})")

    for url in get_sources():
        print(f"🔍 巡回中: {url}")
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:6]:  # 1回あたり件数制限
                title = entry.get('title', '')
                link = entry.get('link', '')
                if not title or not link:
                    continue

                translated = safe_translate(title)
                tags = generate_tags(translated + title)
                image_url = get_relevant_image(translated + title)

                new_posts.append({
                    "date": now_str,
                    "source": "Global Node",
                    "text": f"{tags} {translated}",
                    "url": link,
                    "image": image_url
                })
        except Exception as e:
            print(f"❌ エラー {url}: {e}")

    # --- HTML更新 ---
    if not os.path.exists(html_path):
        print(f"❌ HTMLが見つかりません: {html_path}")
        return

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    posts_match = re.search(r'const posts = (\[[\s\S]*?\]);', content, re.DOTALL)
    if posts_match:
        old_posts = json.loads(posts_match.group(1))
        existing_urls = {p.get('url') for p in old_posts if isinstance(p, dict)}
        
        unique_new = [p for p in new_posts if p['url'] not in existing_urls]
        final_posts = unique_new + old_posts
        final_posts = final_posts[:250]  # 上限

        json_str = json.dumps(final_posts, ensure_ascii=False, indent=4)
        content = content.replace(posts_match.group(0), f'const posts = {json_str};')

    # 更新日時
    content = re.sub(r'const lastUpdated = ".*?";', 
                     f'const lastUpdated = "{now_str}";', content)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"✅ 更新完了: +{len(unique_new)}件（韓国・台湾シャーマニズム強化）")

if __name__ == "__main__":
    crawl()

