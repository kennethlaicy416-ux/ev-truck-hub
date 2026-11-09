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
        print("JSON 解析錯誤:", e)
        return []

def fetch_from_gemini():
    today_str = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
    作為新能源純電重卡市場資深分析師，請生成 3 條前沿行業情報，分別聚焦於國家政策路權、電池換電技術與 TCO 營運成本精算。
    必須以嚴格的 JSON Array 格式輸出，不要有多餘前後文字，包含欄位:
    - "category": "policy", "battery", 或 "tco"
    - "tag": "政策路权", "电池与补能", 或 "TCO 经济性"
    - "title": 標題（簡體中文，25字以內）
    - "date": "{today_str}"
    - "summary": 摘要（簡體中文，50-80字）
    - "action": 應對建議（簡體中文，30-50字）
    """
    try:
        response = gemini_model.generate_content(prompt)
        return clean_and_parse_json(response.text)
    except Exception as e:
        print("Gemini 呼叫失敗:", e)
        return []

def fetch_from_qwen():
    if not qwen_client:
        print("未設定 DASHSCOPE_API_KEY")
        return []
        
    today_str = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
    作為中國內地商用车與重卡市場情報專家，請生成 3 條最新情報，分別聚焦於主機廠競品動態、大宗招投標線索、以及供應鏈與海外出口。
    必須以嚴格的 JSON Array 格式輸出，不要有多餘前後文字，包含欄位:
    - "category": "competitor", "bidding", 或 "supply"
    - "tag": "竞品动态", "招投标线索", 或 "供应链与出海"
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
        return clean_and_parse_json(response.choices[0].message.content)
    except Exception as e:
        print("通義千問呼叫失敗:", e)
        return []

if __name__ == "__main__":
    print("開始執行雙引擎情報聚合...")
    
    gemini_news = fetch_from_gemini()
    print("Gemini 獲取數量:", len(gemini_news))
    
    qwen_news = fetch_from_qwen()
    print("通義千問獲取數量:", len(qwen_news))
    
    all_news = gemini_news + qwen_news
    
    if len(all_news) < 3:
        print("使用備用多維度情報數據庫")
        fallback_news = [
            {
                "category": "policy",
                "tag": "政策路权",
                "title": "多地交通厅发文扩大重卡通行路权",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "summary": "北方多省市近期针对纯电动牵引车出台市区通行证优先办理政策，大幅降低干线物流最后一公里成本。",
                "action": "建议销售团队立即向市区周边大型物流园区客户推送路权红利政策。"
            },
            {
                "category": "tco",
                "tag": "TCO 经济性",
                "title": "400kWh 换电重卡全生命周期回本周期测算",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "summary": "随着电池电芯成本回落，配合换电站 5 分钟补能模式，年行驶 15 万公里的纯电重卡 TCO 较柴油车节省达 35%。",
                "action": "立即更新最新 TCO 试算表，针对高频干线物流车队主打 2.5 年回本优势。"
            },
            {
                "category": "competitor",
                "tag": "竞品动态",
                "title": "三一重工发布新一代大电量换电重卡",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "summary": "竞品推出针对重载矿山场景的 600kWh 超大电量换电车型，主打全天候高强度连续施工作业。",
                "action": "针对标案客戶，需強調我方車型在三电系统熱管理與自重上的對比優勢。"
            }
        ]
        titles = set(i["title"] for i in all_news)
        for item in fallback_news:
            if item["title"] not in titles:
                all_news.append(item)
                
    for idx, item in enumerate(all_news, 1):
        item["id"] = idx

    with open("today_news.json", "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    print("成功寫入 today_news.json，總計:", len(all_news), "條情報")
