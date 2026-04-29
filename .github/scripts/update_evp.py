import feedparser
from deep_translator import GoogleTranslator
import datetime
from datetime import timedelta, timezone
import json
import re
import os
import time

def get_sources():
    base_url = "https://news.google.com/rss/search?q={query}&hl={hl}&gl={gl}&ceid={ceid}"
    
    # ターゲットキーワード（掲示板・各国ニュース）
    FORUM_Q = "(site:4channel.org/x/ OR site:abovetopsecret.com OR site:forteantimes.com) (EVP OR Poltergeist OR 'Haunted Doll' OR OBE OR NHI OR 'Mandela Effect')"
    RU_Q = "Полтергейст OR ФЭГ OR 'Аномальные явления' OR 'ИТК'"
    KO_Q = "심령 OR '유체 이탈' OR '오브' OR '초자연적'"
    ZH_Q = "靈異 OR '曼德拉效應' OR '超常現象'"
    JA_Q = "心霊 OR 幽体離脱 OR 呪物 OR マンデラエフェクト OR 'スピリットボックス' OR '超能力'"

    sources = [
        "https://www.reddit.com/r/EVP/new/.rss",
        "https://www.reddit.com/r/MandelaEffect/new/.rss",
        "https://www.reddit.com/r/Paranormal/new/.rss",
        "https://boards.4channel.org/x/index.rss",
        base_url.format(query=FORUM_Q, hl="en", gl="US", ceid="US:en"),
        base_url.format(query=RU_Q, hl="ru", gl="RU", ceid="RU:ru"),
        base_url.format(query=KO_Q, hl="ko", gl="KR", ceid="KR:ko"),
        base_url.format(query=ZH_Q, hl="zh-TW", gl="TW", ceid="TW:zh-Hant"),
        base_url.format(query=JA_Q, hl="ja", gl="JP", ceid="JP:ja")
    ]
    return sources

translator = GoogleTranslator(source='auto', target='ja')

def generate_tags(text):
    tags = []
    low_text = text.lower()
    if any(x in low_text for x in ["音声", "録音", "声", "evp", "voice"]): tags.append("#Audio")
    if any(x in low_text for x in ["人形", "ドール", "doll", "呪物", "object"]): tags.append("#Object")
    if any(x in low_text for x in ["ポルターガイスト", "物理", "poltergeist"]): tags.append("#Physical")
    if any(x in low_text for x in ["オーブ", "orb", "光球"]): tags.append("#Orb")
    if any(x in low_text for x in ["nhi", "非人類", "intelligence"]): tags.append("#NHI")
    if any(x in low_text for x in ["マンデラ", "mandela", "記憶"]): tags.append("#Mandela")
    if any(x in low_text for x in ["離脱", "obe", "幽体"]): tags.append("#OBE")
    if any(x in low_text for x in ["超能力", "esp", "psy"]): tags.append("#Psy")
    return " ".join(tags) if tags else "#Paranormal"

def crawl():
    # --- 日本時間（JST）を生成 ---
    jst = timezone(timedelta(hours=9), 'JST')
    now = datetime.datetime.now(jst)
    now_str = now.strftime("%Y-%m-%d %H:%M")
    
    new_posts = []
    print(f"📡 20分間隔スキャン開始 (JST: {now_str})")
    
    for url in get_sources():
        try:
            feed = feedparser.parse(url)
            # 各ソースから最新数件を取得
            for entry in feed.entries[:8]:
                try:
                    time.sleep(0.5) # 負荷軽減
                    title = entry.get('title', '')
                    if not title: continue
                    
                    translated_text = translator.translate(title)
                    tags = generate_tags(translated_text + title)
                    tagged_text = f"{tags} {translated_text}"
                    
                    new_posts.append({
                        "date": now_str,
                        "source": "Global Node",
                        "text": tagged_text,
                        "url": entry.get('link', '')
                    })
                except Exception as e:
                    print(f"⚠️ 個別記事スキップ: {e}")
                    continue
        except Exception as e:
            print(f"⚠️ ソース取得エラー ({url}): {e}")
            continue

    # 実行環境のルートにある index.html を探す
    html_path = "index.html"
    if not os.path.exists(html_path):
        print(f"❌ エラー: {html_path} が見つかりません。")
        return

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 記事データの更新
    match = re.search(r'const posts = (\[.*?\]);', content, flags=re.DOTALL)
    old_posts = json.loads(match.group(1)) if match else []
    
    # URLによる重複排除
    existing_urls = {p['url'] for p in old_posts}
    unique_new_posts = []
    for p in new_posts:
        if p['url'] not in existing_urls:
            unique_new_posts.append(p)
            existing_urls.add(p['url'])
            
    # 新着を先頭にして最大200件を維持
    final_posts = (unique_new_posts + old_posts)[:200]
    
    json_str = json.dumps(final_posts, ensure_ascii=False, indent=4)
    content = re.sub(r'const posts = \[.*?\];', f'const posts = {json_str};', content, flags=re.DOTALL)
    
    # 2. 最終更新日時（lastUpdated）を日本時間に書き換え
    # index.html 内の "const lastUpdated = '...';" という記述を探して置換
    content = re.sub(r'const lastUpdated = ".*?";', f'const lastUpdated = "{now_str}";', content)
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"✅ 更新成功。時刻: {now_str} (JST)")
    print(f"📈 新規取得: {len(unique_new_posts)} 件 / 総蓄積: {len(final_posts)} 件")

if __name__ == "__main__":
    crawl()


    
