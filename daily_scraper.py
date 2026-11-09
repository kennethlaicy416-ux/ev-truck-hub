import os
import json
import time
from datetime import datetime
import google.generativeai as genai
from playwright.sync_api import sync_playwright

API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    'gemini-2.5-flash',
    generation_config={"response_mime_type": "application/json"}
)

def scrape_news():
    news_items = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            page.goto("http://www.cvworld.cn/newev/", timeout=20000)
            page.wait_for_load_state("domcontentloaded")
            links = page.locator("a").all()
            for link in links:
                text = link.inner_text().strip()
                if len(text) > 12 and any(k in text for k in ["重卡", "纯电", "换电", "新能源", "牵引车", "三一", "徐工", "解放", "重汽", "宁德"]):
                    news_items.append(text)
                if len(news_items) >= 20: break
        except Exception as e:
            print(f"抓取来源 1 异常: {e}")

        try:
            page.goto("https://www.evpartner.com/news/", timeout=20000)
            page.wait_for_load_state("domcontentloaded")
            titles = page.locator("h3, h4, .title").all()
            for t in titles:
                text = t.inner_text().strip()
                if len(text) > 10 and text not in news_items:
                    news_items.append(text)
                if len(news_items) >= 35: break
        except Exception as e:
            print(f"抓取来源 2 异常: {e}")

        browser.close()
    
    unique_news = list(dict.fromkeys(news_items))
    return "\n".join(unique_news[:25])

def analyze_with_gemini(raw_text):
    today_str = datetime.now().strftime("%Y-%m-%d")
    if not raw_text.strip():
        raw_text = "今日网站结构调整或暂无更新，请根据近期中国新能源纯电重卡行业趋势生成 4 条关键市场情报。"

    prompt = f"""
    你是一位资深的中国新能源纯电重卡市场情报分析师。请根据以下抓取到的最新行业新闻标题，筛选并提炼出 4 到 6 条最具商业价值的核心情报。
    必须输出为 JSON Array 格式，每个物件严格包含：
    - "id": 唯一数字编号
    - "category": ["policy", "competitor", "battery", "bidding"] 之一
    - "tag": ["政策路权", "竞品动态", "电池补能", "招投标线索"] 之一
    - "title": 简洁有力的情报标题（简体中文，25字以内）
    - "date": "{today_str}"
    - "summary": 核心内容摘要（简体中文，50-80字）
    - "action": 针对我们销售与市场团队的应对建议（简体中文，30-50字）

    原始新闻列表：
    {raw_text}
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini 解析失败: {e}")
        return []

if __name__ == "__main__":
    raw_news = scrape_news()
    structured_data = analyze_with_gemini(raw_news)
    if structured_data:
        with open("today_news.json", "w", encoding="utf-8") as f:
            json.dump(structured_data, f, ensure_ascii=False, indent=2)
