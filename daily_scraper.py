import os
import json
from datetime import datetime
import google.generativeai as genai
from openai import OpenAI

# 1. 初始化 Google Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    generation_config={"response_mime_type": "application/json", "temperature": 0.7}
)

# 2. 初始化 DeepSeek API（可在 GitHub Secrets 設定 DEEPSEEK_API_KEY）
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
deepseek_client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
) if DEEPSEEK_API_KEY else None

def fetch_from_gemini():
    """利用 Gemini 獲取國際/綜合視角的重卡市場情報"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
    作为新能源纯电重卡市场分析师，请生成 3 条前沿行业情报（聚焦三一、徐工、宁德时代等电池、换电、政策动态）。
    必须严格输出为 JSON Array 格式，每个物件包含：
    - "id": 数字 (1 或 2)
    - "category": "policy" 或 "battery"
    - "tag": "🏛️ 政策路权" 或 "🔋 电池与补能"
    - "title": 标题（简体中文，25字以内）
    - "date": "{today_str}"
    - "summary": 摘要（简体中文，50-80字）
    - "action": 应对建议（简体中文，30-50字）
    """
    try:
        response = gemini_model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini 抓取失敗: {e}")
        return []

def fetch_from_deepseek():
    """利用 DeepSeek 獲取內地商用車競品與招投標視角的情報"""
    if not deepseek_client:
        print("未設定 DEEPSEEK_API_KEY，跳過 DeepSeek 模組")
        return []
        
    today_str = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
    作为中国内地商用车与重卡市场情报专家，请生成 3 条最新的干线物流、大宗钢铁/矿山重卡招投标或主机厂竞品情报。
    必须严格输出为纯 JSON Array 格式（不要包含 markdown 標籤），每个物件包含：
    - "id": 数字 (3 或 4)
    - "category": "competitor" 或 "bidding"
    - "tag": "🎯 竞品动态" 或 "💰 招投标线索"
    - "title": 标题（简体中文，25字以内）
    - "date": "{today_str}"
    - "summary": 摘要（简体中文，50-80字）
    - "action": 应对建议（简体中文，30-50字）
    """
    try:
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"} if False else None # 兼容處理
        )
        content = response.choices[0].message.content
        # 清理可能存在的 markdown 符號
        content = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        # 確保回傳的是 list
        if isinstance(data, dict):
            data = data.get("news", data.get("data", []))
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"DeepSeek 抓取失敗: {e}")
        return []

if __name__ == "__main__":
    print("正在聚合多模型情報（Gemini + DeepSeek）...")
    
    # 50% 比例分別獲取
    gemini_news = fetch_from_gemini()
    deepseek_news = fetch_from_deepseek()
    
    # 重新編號並合併
    all_news = gemini_news + deepseek_news
    for idx, item in enumerate(all_news, 1):
        item["id"] = idx
        
    # 如果兩邊都沒抓到，提供一組防呆預設值
    if not all_news:
        all_news = [
            {
                "id": 1,
                "category": "competitor",
                "tag": "🎯 竞品动态",
                "title": "多地加速纯电重卡生态布局",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "summary": "头部主机厂近期推出大电量牵引车，加速干线物流电动化渗透。",
                "action": "建议结合TCO模型向客户强调长续航优势。"
            }
        ]

    with open("today_news.json", "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    print(f"✅ 成功融合多模型情報，共生成 {len(all_news)} 條數據並寫入 today_news.json！")
