import streamlit as st
import random
import hashlib
from datetime import date
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests

# --- Hugging Face API 設定 ---
# 我們將使用 Mistral-7B 模型
API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"

try:
    # 從 Streamlit secrets 讀取 API 金鑰
    hf_token = st.secrets["HF_API_KEY"]
    headers = {"Authorization": f"Bearer {hf_token}", "Content-Type": "application/json"}
    API_KEY_CONFIGURED = True
except (KeyError, AttributeError):
    API_KEY_CONFIGURED = False

st.set_page_config(page_title="線上籤詩與心靈指引", page_icon="🏮", layout="wide")

# --- 素材庫 ---

OPENING_LINES = [
    "雲開月出照前途,", "風起潮生天欲曉,", "柳暗花明春又生,",
    "微雨初晴江山秀,", "行舟順水無風浪,", "高山流水逢知音,",
    "殘燈未滅夜方深,", "霜重露寒草木靜,",
]
MIDDLE_LINES_GOOD = [
    "一線光明穿雲霧,", "好風相送上青霄,", "貴人暗處相扶持,",
    "十年耕耘今可收,", "時來運轉皆如意,",
]
MIDDLE_LINES_NEUTRAL = [
    "且當守拙待時機,", "靜看潮起與潮落,", "進退之間宜審思,",
    "莫與人爭一時快,", "心安處處是家園,",
]
MIDDLE_LINES_BAD = [
    "風雨連綿路多岐,", "平地忽起暗波生,", "前程雖有小荊棘,",
    "是非纏繞宜退一步,", "行事若急多招憂,",
]
ENDING_LINES_GOOD = [
    "把握良機福自臨。", "耕深力量結佳果。", "但行好事福常隨。",
    "莫失眼前好時光。", "從此門庭添喜氣。",
]
ENDING_LINES_NEUTRAL = [
    "隨緣處世自安然。", "多思幾步少是非。", "心存正直路自寬。",
    "凡事不急慢慢來。", "看淡得失心自寧。",
]
ENDING_LINES_BAD = [
    "須防言行惹是非。", "暫避鋒芒可無憂。", "稍安勿躁待雲開。",
    "謹慎謀劃免後悔。", "退一步時海闊天。",
]
LUCK_LEVELS = {5: "大吉", 4: "中吉", 3: "小吉", 2: "平", 1: "凶"}

ARCHETYPES = [
    "The Sun | 太陽: 光明與信心", "The Moon | 月亮: 直覺與不安",
    "The Star | 星星: 希望與療癒", "The Hermit | 隱者: 獨處與思考",
    "The Fool | 愚者: 勇氣與冒險", "The Tower | 高塔: 突變與重來",
    "The Lovers | 戀人: 選擇與連結", "The Chariot | 戰車: 意志與前進",
]

TAROT_IMAGES = {
    "The Sun": "https://upload.wikimedia.org/wikipedia/commons/1/17/RWS_Tarot_19_Sun.jpg",
    "The Moon": "https://upload.wikimedia.org/wikipedia/commons/7/7f/RWS_Tarot_18_Moon.jpg",
    "The Star": "https://upload.wikimedia.org/wikipedia/commons/d/db/RWS_Tarot_17_Star.jpg",
    "The Hermit": "https://upload.wikimedia.org/wikipedia/commons/4/4d/RWS_Tarot_09_Hermit.jpg",
    "The Fool": "https://upload.wikimedia.org/wikipedia/commons/9/90/RWS_Tarot_00_Fool.jpg",
    "The Tower": "https://upload.wikimedia.org/wikipedia/commons/5/53/RWS_Tarot_16_Tower.jpg",
    "The Lovers": "https://upload.wikimedia.org/wikipedia/commons/d/de/RWS_Tarot_06_Lovers.jpg",
    "The Chariot": "https://upload.wikimedia.org/wikipedia/commons/9/9b/RWS_Tarot_07_Chariot.jpg",
}
KEYWORDS_GOOD = ["成長、突破、自信", "機會、支持、貴人", "穩定、平衡、順利", "靈感、創意、靈活"]
KEYWORDS_NEUTRAL = ["等待、觀察、調整", "暫停、整理、盤點", "學習、修正、準備"]
KEYWORDS_BAD = ["壓力、考驗、碰撞", "誤會、拖延、混亂", "放下、轉向、重啟"]
WEST_MESSAGES_GOOD = [
    "今天的能量偏向正向與成長，你會發現一些原本卡住的地方開始鬆動。",
    "宇宙正悄悄替你排好路線，只要踏出一步，就能看見更多可能。",
    "你過去的努力正在累積成看得見的成果，請允許自己多一點自信。",
]
WEST_MESSAGES_NEUTRAL = [
    "目前處在一個需要『慢下來』的階段，適合重新檢視你的目標與步調。",
    "外在看起來沒什麼變化，但內在正在醞釀新的方向，不必急著下結論。",
    "這段時間可以多留意細節與資訊，你會從中發現值得調整的小地方。",
]
WEST_MESSAGES_BAD = [
    "近期可能會感到壓力或衝突增加，請記得先照顧好自己的界線與情緒。",
    "有些事情可能不如預期，但這也是重新選擇與調整方向的機會。",
    "宇宙正用比較『激烈』的方式提醒你：有些東西是時候放下了。",
]

ADVICE_BY_TOPIC = {
    "感情": {5: "感情運勢正旺，真誠相待便能開花結果。", 4: "感情有進展，多用心經營與傾聽對方。", 3: "感情平穩，可多安排相處時光增溫。", 2: "暫且順其自然，不必勉強感情發展。", 1: "感情上宜多保護自己，避免衝動決定或爭執。"},
    "學業": {5: "讀書得法又得力，持續努力必有亮眼成績。", 4: "學習狀態良好，調整作息與讀書方法更佳。", 3: "目前尚可，多檢討弱科、穩住基本功。", 2: "需要重新規劃讀書節奏，不必跟人比較。", 1: "心易散、難專注，宜先整理心情再談成績。"},
    "事業": {5: "事業新機將至，大膽把握、積極爭取。", 4: "工作有貴人相助，先做好準備再談機會。", 3: "穩紮穩打，比急著求快更重要。", 2: "暫時不宜大幅變動，多觀察形勢。", 1: "職場是非較多，發言謹慎、保護自身權益。"},
    "健康": {5: "身心狀態良好，維持運動與作息即可。", 4: "略感疲勞，適當休息與調整飲食。", 3: "注意作息與久坐，適時活動筋骨。", 2: "常感壓力，建議安排放鬆與檢查。", 1: "身體發出警訊，應重視身心健康，必要時就醫。"},
    "綜合": {5: "整體運勢昂揚，多行善、多把握機會。", 4: "大致順遂，偶有小波折不足為懼。", 3: "平穩向前，保持好心情是關鍵。", 2: "略有阻力，先調整心態再求突破。", 1: "諸事放緩腳步，先顧好自己再談其他。"},
}

# --- 核心功能 ---

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": f"Invalid response from API: {response.text}"}

def generate_fortune(name: str, topic: str, style: str):
    """
    根據使用者輸入產生東方或西方風格的指引。
    """
    # 使用名字和日期作為種子，確保每天同一個人的結果是固定的
    seed_str = f"{name}-{topic}-{date.today().isoformat()}"
    seed = int(hashlib.sha256(seed_str.encode('utf-8')).hexdigest(), 16) % (10**8)
    random.seed(seed)
    np.random.seed(seed)

    result = {
        "style": style,
        "topic": topic,
        "date": date.today(),
        "title": "",
        "main_text": "",
        "explanation": "",
        "short_advice": "",
        "image_url": None,
    }

    prompt = ""
    # 根據風格產生內容
    if style == "東方籤詩":
        # 1. 決定吉凶等級
        luck_score = (seed % 5) + 1  # 1到5的隨機數
        result["title"] = f"第{seed % 100 + 1:02d}籤 ({LUCK_LEVELS[luck_score]})"
        
        # 2. 組合籤詩
        opening = random.choice(OPENING_LINES)
        if luck_score >= 4:
            middle = random.choice(MIDDLE_LINES_GOOD)
            ending = random.choice(ENDING_LINES_GOOD)
        elif luck_score >= 3:
            middle = random.choice(MIDDLE_LINES_NEUTRAL)
            ending = random.choice(ENDING_LINES_NEUTRAL)
        else:
            middle = random.choice(MIDDLE_LINES_BAD)
            ending = random.choice(ENDING_LINES_BAD)
        
        poem = f"{opening}\n{middle}\n{ending}"
        result["main_text"] = poem

        # 3. 準備 LLM 解籤 Prompt
        prompt = (
            f"You are a wise and kind temple master interpreting a fortune stick poem. The user is asking about '{topic}'. The poem is:\n"
            f"```\n{poem}\n```\n\n"
            f"Please provide a gentle and encouraging interpretation (in Traditional Chinese) based on the poem's mood and the user's topic. Explain what the poem implies for their situation. Do not just repeat the poem. Keep the explanation concise, around 100-150 characters."
        )
        # 4. 給予簡短建議
        result["short_advice"] = ADVICE_BY_TOPIC[topic][luck_score]

    elif style == "西方占卜":
        # 1. 抽一張原型牌
        archetype_full = random.choice(ARCHETYPES)
        archetype_name = archetype_full.split(' | ')[0]
        result["title"] = f"原型卡：{archetype_full}"
        result["image_url"] = TAROT_IMAGES.get(archetype_name)

        # 2. 根據原型的情緒決定關鍵詞和訊息
        luck_score = (seed % 3) + 3 # 模擬 3,4,5 (中性偏上)
        if any(w in archetype_name.lower() for w in ["sun", "star", "lovers", "chariot"]):
            luck_score = 5
        elif any(w in archetype_name.lower() for w in ["moon", "hermit", "fool"]):
            luck_score = 3
        else: # tower
            luck_score = 1

        if luck_score >= 4:
            keywords = random.choice(KEYWORDS_GOOD)
            message = random.choice(WEST_MESSAGES_GOOD)
        elif luck_score >= 2:
            keywords = random.choice(KEYWORDS_NEUTRAL)
            message = random.choice(WEST_MESSAGES_NEUTRAL)
        else:
            keywords = random.choice(KEYWORDS_BAD)
            message = random.choice(WEST_MESSAGES_BAD)

        main_text = f"關鍵詞：{keywords}\n\n核心訊息：{message}"
        result["main_text"] = main_text
        
        # 3. 準備 LLM 綜合解釋 Prompt
        prompt = (
            f"You are an insightful spiritual guide interpreting a tarot-like archetype card. The user is asking about '{topic}'. The card is '{archetype_full}' and the core message is '{message}'.\n\n"
            f"Please synthesize these into a personal, encouraging piece of advice (in Traditional Chinese) for the user's specific situation ('{topic}'). Explain how the card's energy applies to their question. Keep it concise, around 100-150 characters."
        )
        # 4. 給予簡短建議
        result["short_advice"] = ADVICE_BY_TOPIC[topic][luck_score]

    # 執行 API 呼叫
    if prompt:
        payload = {
            "model": MODEL_ID,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200,
            "temperature": 0.7,
        }
        output = query(payload)

        if output.get("choices") and output["choices"][0].get("message"):
            result["explanation"] = output["choices"][0]["message"]["content"].strip()
        elif output.get("error"):
            error_message = output["error"].get("message", str(output["error"]))
            if 'currently loading' in str(error_message).lower():
                result["explanation"] = "解籤模型正在啟動中，請稍候幾秒再試一次。"
            else:
                result["explanation"] = f"解籤時發生錯誤: {error_message}"
        else:
            result["explanation"] = "抱歉，解籤時遇到問題，看來今日天機不可多洩。請靜心再試。"

    return result

# --- 介面 ---

st.title("線上籤詩與心靈指引")
st.write("遇到煩惱或猶豫不決時，請在此誠心問卜，尋求一些方向。")

# 檢查 API 金鑰是否已設定
if not API_KEY_CONFIGURED:
    st.error("警告：Hugging Face API 金鑰未設定！請在 Streamlit secrets 中設定 `HF_API_KEY` 以啟用 AI 生成功能。")
    st.markdown("請前往 [Hugging Face](https://huggingface.co/settings/tokens) 取得您的免費 API Token，並參考 [Streamlit Secrets Management](https://docs.streamlit.io/library/advanced-features/secrets-management) 文件進行設定。")

# Function to reset results
def reset_results():
    st.session_state.fortune_result = None

# Initialize session state
if 'fortune_result' not in st.session_state:
    st.session_state.fortune_result = None

# Input widgets in the sidebar
with st.sidebar:
    st.header("請告訴我你的問題")
    name = st.text_input("你的名字或暱稱：", value="小明", on_change=reset_results)
    topic = st.selectbox("你想問哪一方面？", ["感情", "學業", "事業", "健康", "綜合"], on_change=reset_results)
    style = st.radio("選擇問卜風格：", ["東方籤詩", "西方占卜"], horizontal=True, on_change=reset_results)
    question = st.text_area("請描述你目前想問的具體問題：", value="最近對未來有點迷惘，不知道自己適不適合現在這條路。", height=150, on_change=reset_results)
    
    submit_button = st.button("🧧 點我抽籤", use_container_width=True, disabled=not API_KEY_CONFIGURED)

# Main logic for button click and result generation
if submit_button:
    if not name.strip() or not question.strip():
        st.warning("請務必填寫你的名字及問題。")
        reset_results()
    else:
        with st.spinner("AI 正在為您生成指引..."):
            st.session_state.fortune_result = generate_fortune(name.strip(), topic, style)

# Display results if available
if st.session_state.fortune_result:
    fortune = st.session_state.fortune_result
    
    col_fortune = st.columns([1])[0]

    with col_fortune:
        st.header("給你的指引")
        st.subheader(f"✨ {fortune['style']} | {fortune['title']}")
        st.caption(f"日期：{fortune['date'].isoformat()} | 類別：{fortune['topic']}") # Caption is always displayed

        if fortune['style'] == "西方占卜":
            left_col, right_col = st.columns([1, 2]) # New sub-columns for Western style
            with left_col:
                if fortune.get("image_url"):
                    st.image(fortune["image_url"], width=250)
            with right_col:
                with st.expander("詳細內容", expanded=True):
                    st.markdown(f"##### **📜 內容**")
                    st.markdown(f"```text\n{fortune['main_text']}\n```")
                    st.markdown("##### **🤔 解說**")
                    st.write(fortune["explanation"])
                    st.markdown("##### **💡 簡短建議**")
                    st.write(fortune["short_advice"])
        else: # 東方籤詩 (Eastern style)
            with st.expander("詳細內容", expanded=True):
                st.markdown(f"##### **📜 內容**")
                st.markdown(f"```text\n{fortune['main_text']}\n```")
                st.markdown("##### **🤔 解說**")
                st.write(fortune["explanation"])
                st.markdown("##### **💡 簡短建議**")
                st.write(fortune["short_advice"])
else:
    st.info("填寫側邊欄的問題後，點擊按鈕獲取你的專屬指引。")