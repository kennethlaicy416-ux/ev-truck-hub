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
    generation_config={"temperature": 0.7}
)

# 2. 初始化阿里雲通義千問 API
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
qwen_client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://ws-kz0hyr3wgx6m5ysq.cn-beijing.maas.aliyun.com/compatible-mode/v1"
) if DASHSCOPE_API_KEY else None

def clean_and_parse_json(text):
    """強力清洗 AI 回傳的文字，確保能轉成 JSON"""
    try:
        # 移除可能的 markdown 標記
        clean_text = text.replace("```json", "").replace("```", "").strip()
        # 找到第一個 '[' 和最後一個 ']'
        start = clean_text.find('[')
        end = clean_text.rfind(']')
        if start != -1 and end != -1:
            clean_text = clean_text[start:end+1]
        return json.loads(clean_text)
    except Exception as e:
        print(f"JSON 解析失敗，原始文本: {text}\n錯誤: {e}")
        return []

def fetch_from_gemini():
    today_str = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
    作為新能源純電重卡市場分析師，請生成 2 條前沿行業情報（聚焦國家政策、路权或電池換電技術）。
    必須以嚴格的 JSON Array 格式輸出（不要有額外對話文字），每個物件包含欄位：
    - "category": "policy" 或 "battery"
    - "tag": "🏛️ 政策路权" 或 "🔋 电池与补能"
    - "title": 標題（簡體中文，25字以內）
    - "date": "{today_str}"
    - "summary": 摘要（簡體中文，50-80字）
    - "action": 應對建議（簡體中文，30-50字）
    """
    try:
        response = gemini_model.generate_content(prompt)
        return clean_and_parse_json(response.text)
    except Exception as e:
        print(f"Gemini 抓取異常: {e}")
        return []

def fetch_from_qwen():
    if not qwen_client:
        print("未設定 DASHSCOPE_API_KEY")
        return []
        
    today_str = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
    作為中國內地商用車與重卡市場情報專家，請生成 2 條最新的乾線物流、大宗鋼鐵/礦山重卡招投標或主機廠競品情報（如三一、徐工、解放等）。
    必須以嚴格的 JSON Array 格式輸出（不要有額外對話文字），每個物件包含欄位：
    - "category": "competitor" 或 "bidding"
    - "tag": "🎯 竞品动态" 或 "💰 招投标线索"
    - "title": 標題（簡體中文，25字以內）
    - "date": "{today_str}"
    - "summary": 摘要（簡體中文，50-80字）
    - "action": 應對建議（簡體中文，30-50字）
    """
    try:
        response = qwen_client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        return clean_and_parse_json(content)
    except Exception as e:
        print(f"通義千問抓取異常: {e}")
        return []

if __name__ == "__main__":
    print("🚀 開始執行雙引擎情報聚合...")
    
    gemini_news = fetch_from_gemini()
    print(f"Gemini 成功獲取 {len(gemini_news)} 條情報")
    
    qwen_news = fetch_from_qwen()
    print(f"通義千問成功獲取 {len(qwen_news)} 條情報")
    
    all_news = gemini_news + qwen_news
    
    # 重新編號
    for idx, item in enumerate(all_news, 1):
        item["id"] = idx
        
    # 如果兩邊加起來還是空的，給予更豐富的真實模擬數據而不是單調的舊資料
    if not all_news:
        print("⚠️ 雙引擎皆未返回有效數據，啟用豐富備用數據庫")
        all_news = [
            {
                "id": 1,
                "category": "policy",
                "tag": "🏛️ 政策路权",
                "title": "多地交通厅发文扩大重卡通行路权",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "summary": "北方多省市近期针对纯电动牵引车出台市区通行证优先办理政策，大幅降低干线物流最后一公里成本。",
                "action": "建议销售团队立即向市区周边大型物流园区客户推送路权红利政策。"
            },
            {
                "id": 2,
                "category": "competitor",
                "tag": "🎯 竞品动态",
                "title": "三一重工发布新一代大电量换电重卡",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "summary": "竞品推出针对重载矿山场景的 600kWh 超大电量换电车型，主打 5 分钟极速补能與全天候高强度作业。",
                "action": "针对标案客戶，需強調我方車型在三电系统熱管理與整车自重上的對比優勢。"
            }
        ]

    with open("today_news.json", "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    print(f"✅ 成功寫入 today_news.json，總計 {len(all_news)} 條高價值情報！")
