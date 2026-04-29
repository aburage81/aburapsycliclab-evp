
import feedparser
from deep_translator import GoogleTranslator
import datetime
from datetime import timedelta, timezone
import json
import re
import os
import time
from functools import lru_cache

# --- 1. Reddit RSS用ヘッダー付きパース ---
def parse_with_headers(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/rss+xml'
    }
    # feedparserは内部でrequestsのようなヘッダー送信が難しいため、
    # 実際にはUser-Agentを偽装して取得を試みます
    return feedparser.parse(url, agent=headers['User-Agent'])

# --- 2. 翻訳キャッシュとレート制限対策 ---
translator = GoogleTranslator(source='auto', target='ja')

@lru_cache(maxsize=500)
def safe_translate(text):
    if not text: return ""
    try:
        # 翻訳前に少し待機してGoogleの機嫌を伺う
        time.sleep(1.2) 
        return translator.translate(text)
    except Exception as e:
        print(f"⚠️ 翻訳エラー: {e} -> 原文を使用します")
        return text

def get_sources():
    base_url = "https://news.google.com/rss/search?q={query}&hl={hl}&gl={gl}&ceid={ceid}"
    FORUM_Q = "(site:4channel.org/x/ OR site:abovetopsecret.com) (EVP OR Poltergeist OR NHI OR 'Mandela Effect')"
    sources = [
        "https://www.reddit.com/r/EVP/new/.rss",
        "https://www.reddit.com/r/MandelaEffect/new/.rss",
        "https://www.reddit.com/r/Paranormal/new/.rss",
        "https://boards.4channel.org/x/index.rss",
        base_url.format(query=FORUM_Q, hl="en", gl="US", ceid="US:en"),
        base_url.format(query="심령 OR '유체 이탈' OR '오브'", hl="ko", gl="KR", ceid="KR:ko"),
        base_url.format(query="靈異 OR '曼德拉效應'", hl="zh-TW", gl="TW", ceid="TW:zh-Hant"),
        base_url.format(query="心霊 OR 幽体離脱 OR 呪物", hl="ja", gl="JP", ceid="JP:ja")
    ]
    return sources

def generate_tags(text):
    tags = []
    low_text = text.lower()
    keywords = {
        "#Audio": ["音声", "録音", "声", "evp", "voice"],
        "#Object": ["人形", "ドール", "doll", "呪物", "object"],
        "#Physical": ["ポルターガイスト", "物理", "poltergeist"],
        "#Orb": ["オーブ", "orb", "光球"],
        "#NHI": ["nhi", "非人類", "intelligence"],
        "#Mandela": ["マンデラ", "mandela", "記憶"],
        "#OBE": ["離脱", "obe", "幽体"],
        "#Psy": ["超能力", "esp", "psy"]
    }
    for tag, keys in keywords.items():
        if any(k in low_text for k in keys):
            tags.append(tag)
    return " ".join(tags) if tags else "#Paranormal"

def crawl():
    jst = timezone(timedelta(hours=9), 'JST')
    now_str = datetime.datetime.now(jst).strftime("%Y-%m-%d %H:%M")
    
    # 絶対パスの取得
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    html_path = os.path.join(repo_root, "index.html")

    new_posts = []
    print(f"📡 スキャン開始 (JST: {now_str})")
    
    for url in get_sources():
        print(f"🔍 巡回中: {url}")
        try:
            feed = parse_with_headers(url)
            if not feed.entries:
                print(f"   -> 取得数 0 (ブロックまたは更新なし)")
                continue
                
            for entry in feed.entries[:5]: # 翻訳制限回避のため件数を絞る
                title = entry.get('title', '')
                link = entry.get('link', '')
                if not title or not link: continue
                
                # 翻訳
                translated = safe_translate(title)
                tags = generate_tags(translated + title)
                
                new_posts.append({
                    "date": now_str,
                    "source": "Global Node",
                    "text": f"{tags} {translated}",
                    "url": link
                })
        except Exception as e:
            print(f"❌ エラー: {url} -> {e}")

    if not os.path.exists(html_path):
        print(f"❌ ファイル未発見: {html_path}")
        return

    # --- HTML更新ロジック (replace方式で堅牢化) ---
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 記事データの置換
    posts_match = re.search(r'const posts = (\[[\s\S]*?\]);', content)
    if posts_match:
        old_posts = json.loads(posts_match.group(1))
        existing_urls = {p['url'] for p in old_posts}
        
        unique_new = [p for p in new_posts if p['url'] not in existing_urls]
        final_posts = (unique_new + old_posts)[:200]
        
        json_str = json.dumps(final_posts, ensure_ascii=False, indent=4)
        content = content.replace(posts_match.group(0), f'const posts = {json_str};')

    # 更新時刻の置換
    content = re.sub(r'const lastUpdated = ".*?";', f'const lastUpdated = "{now_str}";', content)
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"✅ 更新成功: {len(unique_new)}件の新信号をキャッチ")

if __name__ == "__main__":
    crawl()
