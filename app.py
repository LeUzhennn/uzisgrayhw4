import streamlit as st
import random
import hashlib
from datetime import date
import base64

# --- Page Configuration ---
st.set_page_config(
    page_title="線上靈籤・每日指引",
    page_icon="🏮",
    layout="centered"
)

# --- Styling and Assets ---
def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://www.transparenttextures.com/patterns/traditional-chinese.png");
             background-attachment: fixed;
             background-size: cover;
         }}
         .main-container {{
             background-color: rgba(255, 255, 255, 0.85);
             padding: 2rem;
             border-radius: 10px;
         }}
         .fortune-container {{
             background-color: #fdf5e6;
             border: 2px solid #d2b48c;
             border-radius: 15px;
             padding: 2rem;
             margin-top: 2rem;
             font-family: 'KaiTi', 'STKaiti', 'serif';
             box-shadow: 0 4px 8px rgba(0,0,0,0.1);
             text-align: center;
         }}
         h1, h3 {{
             text-align: center;
             font-family: 'KaiTi', 'STKaiti', 'serif';
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url()

# --- Data Libraries ---
OPENING_LINES = [
    "雲開月出照前途,", "風起潮生天欲曉,", "柳暗花明春又生,",
    "微雨初晴江山秀,", "行舟順水無風浪,", "高山流水逢知音,",
    "殘燈未滅夜方深,", "霜重露寒草木靜,"
]
MIDDLE_LINES_GOOD = ["一線光明穿雲霧,", "好風相送上青霄,", "貴人暗處相扶持,", "十年耕耘今可收,", "時來運轉皆如意,"]
MIDDLE_LINES_NEUTRAL = ["且當守拙待時機,", "靜看潮起與潮落,", "進退之間宜審思,", "莫與人爭一時快,", "心安處處是家園,"]
MIDDLE_LINES_BAD = ["風雨連綿路多岐,", "平地忽起暗波生,", "前程雖有小荊棘,", "是非纏繞宜退一步,", "行事若急多招憂,"]
ENDING_LINES_GOOD = ["把握良機福自臨。", "耕深力量結佳果。", "但行好事福常隨。", "莫失眼前好時光。", "從此門庭添喜氣。"]
ENDING_LINES_NEUTRAL = ["隨緣處世自安然。", "多思幾步少是非。", "心存正直路自寬。", "凡事不急慢慢來。", "看淡得失心自寧。"]
ENDING_LINES_BAD = ["須防言行惹是非。", "暫避鋒芒可無憂。", "稍安勿躁待雲開。", "謹慎謀劃免後悔。", "退一步時海闊天。"]
LUCK_LEVELS = {5: "大吉", 4: "中吉", 3: "小吉", 2: "平", 1: "凶"}
ARCHETYPES = [
    "The Sun | 太陽: 光明與信心", "The Moon | 月亮: 直覺與不安", "The Star | 星星: 希望與療癒",
    "The Hermit | 隱者: 獨處與思考", "The Fool | 愚者: 勇氣與冒險", "The Tower | 高塔: 突變與重來",
    "The Lovers | 戀人: 選擇與連結", "The Chariot | 戰車: 意志與前進"
]
TAROT_IMAGES = {
    "The Sun | 太陽: 光明與信心": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/RWS_Tarot_19_Sun.jpg/800px-RWS_Tarot_19_Sun.jpg",
    "The Moon | 月亮: 直覺與不安": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/The_Moon%2C_Waite-Smith_Tarot_Deck%2C_Yale_University.jpg/800px-The_Moon%2C_Waite-Smith_Tarot_Deck%2C_Yale_University.jpg",
    "The Star | 星星: 希望與療癒": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/db/RWS_Tarot_17_Star.jpg/800px-RWS_Tarot_17_Star.jpg",
    "The Hermit | 隱者: 獨處與思考": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/RWS_Tarot_09_Hermit.jpg/800px-RWS_Tarot_09_Hermit.jpg",
    "The Fool | 愚者: 勇氣與冒險": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/RWS_Tarot_00_Fool.jpg/800px-RWS_Tarot_00_Fool.jpg",
    "The Tower | 高塔: 突變與重來": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/RWS_Tarot_16_Tower.jpg/800px-RWS_Tarot_16_Tower.jpg",
    "The Lovers | 戀人: 選擇與連結": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/RWS_Tarot_06_Lovers.jpg/800px-RWS_Tarot_06_Lovers.jpg",
    "The Chariot | 戰車: 意志與前進": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/RWS_Tarot_07_Chariot.jpg/800px-RWS_Tarot_07_Chariot.jpg"
}
KEYWORDS_GOOD = ["成長、突破、自信", "機會、支持、貴人", "穩定、平衡、順利", "靈感、創意、靈活"]
KEYWORDS_NEUTRAL = ["等待、觀察、調整", "暫停、整理、盤點", "學習、修正、準備"]
KEYWORDS_BAD = ["壓力、考驗、碰撞", "誤會、拖延、混亂", "放下、轉向、重啟"]
WEST_MESSAGES_GOOD = [
    "今天的能量偏向正向與成長，你會發現一些原本卡住的地方開始鬆動。",
    "宇宙正悄悄替你排好路線，只要踏出下一步，就能看見更多可能。",
    "你過去的努力正在累積成看得見的成果，請允許自己多一點自信。"
]
WEST_MESSAGES_NEUTRAL = [
    "目前處在一個需要『慢下來』的階段，適合重新檢視你的目標與步調。",
    "外在看起來沒什麼變化，但內在正在醞釀新的方向，不必急著下結論。",
    "這段時間可以多留意細節與資訊，你會從中發現值得調整的小地方。"
]
WEST_MESSAGES_BAD = [
    "近期可能會感到壓力或衝突增加，請記得先照顧好自己的界線與情緒。",
    "有些事情可能不如預期，但這也是重新選擇與調整方向的機會。",
    "宇宙正用比較『激烈』的方式提醒你：有些東西是時候放下了。"
]
ADVICE_BY_TOPIC = {
    "感情": {5: "感情運勢正旺，真誠相待便能開花結果。", 4: "感情有進展，多用心經營與傾聽對方。", 3: "感情平穩，可多安排相處時光增溫。", 2: "暫且順其自然，不必勉強感情發展。", 1: "感情上宜多保護自己，避免衝動決定或爭執。"},
    "學業": {5: "讀書得法又得力，持續努力必有亮眼成績。", 4: "學習狀態良好，調整作息與讀書方法更佳。", 3: "目前尚可，多檢討弱科、穩住基本功。", 2: "需要重新規劃讀書節奏，不必跟人比較。", 1: "心易散、難專注，宜先整理心情再談成績。"},
    "事業": {5: "事業新機將至，大膽把握、積極爭取。", 4: "工作有貴人相助，先做好準備再談機會。", 3: "穩紮穩打，比急著求快更重要。", 2: "暫時不宜大幅變動，多觀察形勢。", 1: "職場是非較多，發言謹慎、保護自身權益。"},
    "健康": {5: "身心狀態良好，維持運動與作息即可。", 4: "略感疲勞，適當休息與調整飲食。", 3: "注意作息與久坐，適時活動筋骨。", 2: "常感壓力，建議安排放鬆與檢查。", 1: "身體發出警訊，應重視身心健康，必要時就醫。"},
    "綜合": {5: "整體運勢昂揚，多行善、多把握機會。", 4: "大致順遂，偶有小波折不足為懼。", 3: "平穩向前，保持好心情是關鍵。", 2: "略有阻力，先調整心態再求突破。", 1: "諸事放緩腳步，先顧好自己再談其他。"}
}

# --- Core Logic ---
def get_seed(name: str, topic: str, style: str, today: date) -> int:
    base = f"{name}-{topic}-{style}-{today.isoformat()}"
    h = hashlib.md5(base.encode("utf-8")).hexdigest()
    return int(h, 16)

def generate_eastern_fortune(name: str, topic: str):
    today = date.today()
    seed = get_seed(name, topic, "EAST", today)
    random.seed(seed)
    stick_no = random.randint(1, 100)
    luck_score = random.choices(population=[1, 2, 3, 4, 5], weights=[1, 2, 3, 2, 1], k=1)[0]
    luck = LUCK_LEVELS[luck_score]
    opening = random.choice(OPENING_LINES)
    if luck_score >= 4:
        middle = random.choice(MIDDLE_LINES_GOOD)
        ending = random.choice(ENDING_LINES_GOOD)
        explanation = "此籤多主順勢而上，表示近期整體氣勢不錯，只要保持腳踏實地與穩健，就有機會迎來好結果。"
    elif luck_score == 3:
        middle = random.choice(MIDDLE_LINES_NEUTRAL)
        ending = random.choice(ENDING_LINES_NEUTRAL)
        explanation = "此籤意在提醒：目前情勢大致平穩，不必過度擔心，但仍需留心細節，穩中求進。"
    else:
        middle = random.choice(MIDDLE_LINES_BAD)
        ending = random.choice(ENDING_LINES_BAD)
        explanation = "此籤帶有警示意味，提醒你近期行事要多留意風險，能退一步時就不要逞強，先保護好自己。"
    poem = opening + "\n" + middle + "\n" + ending
    advice_topic = ADVICE_BY_TOPIC.get(topic, ADVICE_BY_TOPIC["綜合"])
    advice = advice_topic[luck_score]
    return {"style": "東方靈籤", "date": today, "title": f"第 {stick_no} 號・{luck}", "main_text": poem, "explanation": explanation, "advice": advice, "topic": topic}

def generate_western_fortune(name: str, topic: str):
    today = date.today()
    seed = get_seed(name, topic, "WEST", today)
    random.seed(seed)
    archetype = random.choice(ARCHETYPES)
    image_url = TAROT_IMAGES.get(archetype)
    luck_score = random.choices(population=[1, 2, 3, 4, 5], weights=[1, 2, 3, 2, 1], k=1)[0]
    luck = LUCK_LEVELS[luck_score]
    if luck_score >= 4:
        keyword = random.choice(KEYWORDS_GOOD)
        message = random.choice(WEST_MESSAGES_GOOD)
    elif luck_score == 3:
        keyword = random.choice(KEYWORDS_NEUTRAL)
        message = random.choice(WEST_MESSAGES_NEUTRAL)
    else:
        keyword = random.choice(KEYWORDS_BAD)
        message = random.choice(WEST_MESSAGES_BAD)
    advice_topic = ADVICE_BY_TOPIC.get(topic, ADVICE_BY_TOPIC["綜合"])
    advice = advice_topic[luck_score]
    explanation = f"這張牌代表的主題大致與「{keyword}」有關。它提醒你留意當下的情緒與選擇，因為這會直接影響到後續的發展。"
    main_text = f"**牌面主題**：{archetype.split(':')[0]}\n\n**今日關鍵字**：{keyword}\n\n**牌面訊息**：{message}"
    return {"style": "西方神諭", "date": today, "title": f"{archetype.split('|')[0].strip()}・{luck}", "main_text": main_text, "explanation": explanation, "advice": advice, "topic": topic, "image_url": image_url}

# --- UI Layout ---
st.title("線上靈籤・每日指引")
st.write("心誠則靈，請寫下你的名字，選擇所問之事與占卜風格。")

with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("你的名字或暱稱:", value="小明")
        topic = st.selectbox("你想問哪一方面?", ["感情", "學業", "事業", "健康", "綜合"])
    
    with col2:
        style = st.radio(
            "選擇占卜風格:",
            ["東方靈籤 (詩詞)", "西方神諭 (牌卡)"],
            horizontal=False,
        )

    if st.button("虔誠問卜 🙏"):
        if not name.strip():
            st.warning("請先輸入你的名字或暱稱。")
        else:
            if style.startswith("東方"):
                fortune = generate_eastern_fortune(name.strip(), topic)
            else:
                fortune = generate_western_fortune(name.strip(), topic)
            
            with st.container():
                st.markdown('<div class="fortune-container">', unsafe_allow_html=True)

                if fortune.get("image_url"):
                    st.image(fortune["image_url"], width=250)

                st.markdown(f"### {fortune['style']}・{fortune['title']}")
                st.caption(f"問卜者: {name.strip()} | 日期: {fortune['date'].isoformat()} | 所問之事: {fortune['topic']}")
                st.divider()
                
                if fortune['style'] == '東方靈籤':
                     st.markdown(f"<div style='text-align: left;'><h4>籤詩</h4><pre><code>{fortune['main_text']}</code></pre></div>", unsafe_allow_html=True)
                else:
                     st.markdown(f"<div style='text-align: left;'><h4>神諭牌卡</h4><p>{fortune['main_text'].replace('n', '<br>')}</p></div>", unsafe_allow_html=True)

                st.markdown("<div style='text-align: left;'><h4>💡 解說</h4></div>", unsafe_allow_html=True)
                st.write(fortune["explanation"])
                
                st.markdown("<div style='text-align: left;'><h4>✍️ 指引</h4></div>", unsafe_allow_html=True)
                st.write(fortune["advice"])
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.info("同名同日同問之事，所得之籤不變。每日運勢不同，請明日再來。")
