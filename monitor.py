import requests
import re
import os
import time
from playwright.sync_api import sync_playwright

# --- 配置區 ---
webhook_raw = os.environ.get("DISCORD_WEBHOOK", "")
DISCORD_WEBHOOK_URLS = [url.strip() for url in webhook_raw.split(",") if url.strip()]

# 定義要檢查的分類與 Category 4 的黑名單
CATEGORIES = [3, 4]
CAT4_BLACKLIST = ["3", "46", "65"]  # 這些編號的公告會被略過

def send_to_discord(title, link, text_content):
    if not DISCORD_WEBHOOK_URLS:
        print("⚠️ 未設定 Discord Webhook")
        return

    if len(text_content) > 3000:
        text_content = text_content[:3000] + "\n\n...(內容過長)"

    payload = {
        "username": "FFXIV 光之工具人",
        "embeds": [{
            "title": title,
            "url": link,
            "description": text_content,
            "color": 3447003,
            "footer": {"text": f"發送時間: {time.strftime('%Y-%m-%d %H:%M:%S')}"}
        }]
    }

    for url in DISCORD_WEBHOOK_URLS:
        requests.post(url, json=payload)

def run_scraper():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for cat in CATEGORIES:
            try:
                url = f"https://www.ffxiv.com.tw/web/news/news_list.aspx?category={cat}"
                print(f"正在檢查分類 {cat}: {url}")
                page.goto(url, timeout=60000)
                page.wait_for_selector(".news_list .item")

                # 抓取第一則公告
                first_item = page.query_selector(".news_list .item")
                news_id = first_item.query_selector(".news_id").inner_text().strip()

                # 針對 Category 4 的黑名單檢查
                if cat == 4 and news_id in CAT4_BLACKLIST:
                    print(f"⏩ 略過 Category 4 的黑名單編號: {news_id}")
                    continue

                title = first_item.query_selector(".title a").inner_text().strip()
                link = "https://www.ffxiv.com.tw" + first_item.query_selector(".title a").get_attribute("href")

                # 檢查更新 (每個分類獨立檔案)
                record_file = f"last_news_id_{cat}.txt"
                if os.path.exists(record_file):
                    with open(record_file, "r", encoding="utf-8") as f:
                        if f.read().strip() == news_id:
                            print(f"😴 分類 {cat} 沒有新公告。")
                            continue

                # 進入內文抓取 .article
                page.goto(link, timeout=60000)
                page.wait_for_selector(".article")
                article_text = page.query_selector(".article").inner_text().strip()
                formatted_text = re.sub(r'\n{3,}', '\n\n', article_text)

                # 發送通知
                send_to_discord(f"{title}", link, formatted_text)

                # 更新紀錄 (存 ID 比存標題更準確)
                with open(record_file, "w", encoding="utf-8") as f:
                    f.write(news_id)

            except Exception as e:
                print(f"分類 {cat} 執行出錯: {e}")

        browser.close()

if __name__ == "__main__":
    run_scraper()
