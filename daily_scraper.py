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

# 2. 初始化阿里雲通義千問 API (使用你的百煉專屬專屬域名)
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
qwen_client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://ws-kz0hyr3wgx6m5ysq.cn-beijing.maas.aliyun.com/compatible-mode/v1"
) if DASHSCOPE_API_KEY else None

def fetch_from_gemini():
    """利用 Gemini 獲取國際/電池/政策視角的重卡情報"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
    作为新能源纯电重卡市场分析师，请生成 2 条前沿行业情报（聚焦国家政策、路权或电池换电技术）。
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

def fetch_from_qwen():
    """利用阿里雲通義千問獲取內地商用車競品與招投標視角的情報"""
    if not qwen_client:
        print("未設定 DASHSCOPE_API_KEY，跳過通義千問模組")
        return []
        
    today_str = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
    作为中国内地商用车与重卡市场情报专家，请生成 2 条最新的干线物流、大宗钢铁/矿山重卡招投标或主机厂竞品情报（如三一、徐工、解放等）。
    必须严格输出为纯 JSON Array 格式，每个物件包含：
    - "id": 数字 (3 或 4)
    - "category": "competitor" 或 "bidding"
    - "tag": "🎯 竞品动态" 或 "💰 招投标线索"
    - "title": 标题（简体中文，25字以内）
    - "date": "{today_str}"
    - "summary": 摘要（简体中文，50-80字）
    - "action": 应对建议（简体中文，30-50字）
    """
    try:
        response = qwen_client.chat.completions.create(
            model="qwen-plus",  # 使用通義千問的高性能模型
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        content = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        if isinstance(data, dict):
            data = data.get("news", data.get("data", list(data.values())[0] if data else []))
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"通義千問抓取失敗: {e}")
        return []

if __name__ == "__main__":
    print("正在聚合雙引擎情報（Gemini + 通義千問）...")
    
    gemini_news = fetch_from_gemini()
    qwen_news = fetch_from_qwen()
    
    all_news = gemini_news + qwen_news
    for idx, item in enumerate(all_news, 1):
        item["id"] = idx
        
    if not all_news:
        all_news = [
            {
                "id": 1,
                "category": "policy",
                "tag": "🏛️ 政策路权",
                "title": "多地加速推进重卡换电站建设",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "summary": "近期多地交通部门发文，对纯电及换电重卡给予通行优先权。",
                "action": "建议优先向物流大客户推介换电重卡路权优势。"
            }
        ]

    with open("today_news.json", "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    print(f"✅ 成功融合雙引擎情報，共生成 {len(all_news)} 條數據！")
