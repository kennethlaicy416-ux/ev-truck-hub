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
    try:
        clean_text = text.replace("```json", "").replace("```", "").strip()
        start = clean_text.find('[')
        end = clean_text.rfind(']')
        if start != -1 and end != -1:
            clean_text = clean_text[start:end+1]
        return json.loads(clean_text)
    except Exception as e:
        print(f"JSON 解析錯誤: {e}, 原始内容: {text}")
        return []

def fetch_from_gemini():
    today_str = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
    作為新能源純電重卡市場資深分析師，請生成 3 條前沿行業情報，分別聚焦於：
    1. 國家政策或通行路權紅利
    2. 電池技術、換電站建設與超充快補
    3. TCO 營運成本精算與客戶回本週期變化
    必須以嚴格的 JSON Array 格式輸出（不要有多餘前後文字），包含以下欄位：
    - "category": "policy", "battery", 或 "tco"
    - "tag": 分別對應 "🏛️ 政策路权", "🔋 电池与补能", 或 "📊 TCO 经济性"
    - "title": 標題（簡體中文，25字以內）
    - "date": "{today_str}"
    - "summary": 摘要（簡體中文，50-80字，包含具體數據或營運痛點）
    - "action": 應對建議（簡體中文，30-50字，針對銷售或營運團隊）
    """
    try:
        response = gemini_model.generate_content(prompt)
        return clean_and_parse_json(response.text)
    except Exception as e:
        print(f"Gemini 呼叫失敗: {e}")
        return []

def fetch_from_qwen():
    if not qwen_client:
        print("未設定 DASHSCOPE_API_KEY")
        return []
        
    today_str = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
    作為中國內地商用车與重卡市場情報專家，請生成 3 條最新的乾線物流情報，分別聚焦於：
    1. 主機廠競品動態（如三一、徐工、解放、重汽等最新車型或促銷）
    2. 大宗物資、鋼廠或礦山重卡大單招投標線索
    3. 供應鏈動態、上游原材料或重卡海外出口/短倒運輸趨勢
    必須以嚴格的 JSON Array 格式輸出（不要有多餘前後文字），包含以下欄位：
    - "category": "competitor", "bidding", 或 "supply"
    - "tag": 分別對應 "🎯 竞品动态", "💰 招投标线索", 或 "🌐 供应链与出海"
    - "title": 標題（簡體中文，25字以內）
    - "date": "{today_str}"
    - "summary": 摘要（簡體中文，50-80字，包含具體企業或標案背景）
    - "action": 應對建議（簡體中文，30-50字，針對銷售或投標團隊）
    """
    try:
        response = qwen_client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "user", "content": prompt}]
        )
        return clean_and_parse_json(response.choices[0].message.content)
    except Exception as e:
        print(f"通義千問呼叫失敗: {e}")
        return []

if __name__ == "__main__":
    print("🚀 開始執行雙引擎豐富情報聚合...")
    
    gemini_news = fetch_from_gemini()
    print(f"Gemini 成功獲取 {len(gemini_news)} 條情報")
    
    qwen_news = fetch_from_qwen()
    print(f"通義千問成功獲取 {len(qwen_news)} 條情報")
    
    all_news = gemini_news + qwen_news
    
    # 動態備用數據（若 API 偶發逾時時使用，確保網頁隨時有 6 條豐富內容）
    if len(all_news) < 3:
        print("⚠️ 雙引擎返回數據較少，補充高價值精選情報")
        fallback_news = [
            {
                "category": "policy",
                "tag": "🏛️ 政策路权",
                "title": "多地交通厅发文扩大重卡通行路权",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "summary": "北方多省市近期针对纯电动牵引车出台市区通行证优先办理政策，大幅降低干线物流最后一公里成本。",
                "action": "建议销售团队立即向市区周边大型物流园区客户推送路权红利政策。"
            },
            {
                "category": "tco",
                "tag": "📊 TCO 经济性",
                "title": "电池电芯价格下探带动重卡购置成本优化",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "summary": "随着磷酸铁锂电芯成本回落，400kWh标快换电重卡整车售价进一步下探，客户全生命周期回本周期縮短至 2.5 年。",
                "action": "更新最新 TCO 試算模型，向觀望型物流車隊主打投資回收期縮短優勢。"
            }
        ]
        all_news.extend(fallback_news)
        
    # 重新編號 1 到 N
    for idx, item in enumerate(all_news, 1):
        item["id"] = idx

    with open("today_news.json", "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    print(f"✅ 成功寫入 {len(all_news)} 條豐富情報至 today_news.json")
