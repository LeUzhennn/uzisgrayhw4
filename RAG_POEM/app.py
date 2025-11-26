import streamlit as st
import random
import hashlib
from datetime import date
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

RAW_THERAPY_DOCS = [
    {"topic": "感情", "text": "在感情裡沒有永遠完美的答案，只有當下最真誠的選擇。與其反覆猜測對方，不如先問問自己真正想要的是什麼。"},
    {"topic": "感情", "text": "如果一段關係讓你常常感到不安，不一定是你不夠好，而是彼此的步調與期待不同。適度溝通，比悶在心裡更有力量。"},
    {"topic": "學業", "text": "成績好壞並不能定義你的全部價值。把注意力放在每天多理解一點、多踏實一點，進步就正在發生。"},
    {"topic": "學業", "text": "讀書不是要證明你比別人強，而是讓未來的自己有更多選擇。當你感到累了，先休息，再出發也來得及。"},
    {"topic": "事業", "text": "工作上的挫折，不代表你不適合這條路，而是提醒你：需要改變做事方式、調整節奏，或是學會說不。"},
    {"topic": "事業", "text": "職場有時像是一場長跑，不必每一步都衝刺。先穩住自己的節奏，才能在關鍵時刻有力氣加速。"},
    {"topic": "健康", "text": "身體的不舒服，往往是心在抗議。當你總是勉強自己撐下去，也記得給自己一個真正放鬆的時間。"},
    {"topic": "健康", "text": "睡眠、飲食與運動，是最樸實也最有效的自我照顧。從多喝一杯水、多睡十分鐘開始，都是向自己的身體道謝。"},
    {"topic": "綜合", "text": "人生不會永遠順風順水，但也不會永遠下雨。當你覺得走不動的時候，就先學著好好陪自己走一段路。"},
    {"topic": "綜合", "text": "你不必成為別人口中的完美樣子才值得被愛。能誠實面對自己的脆弱，本身就是一種勇敢。"},
    {"topic": "綜合", "text": "有時候我們太在意別人的眼光，反而忘記自己真正想成為怎樣的人。暫時放下比較，看看自己的腳印，也很漂亮。"},
    {"topic": "事業", "text": "當你對未來感到迷惘時，不一定要立刻找到答案。先從完成一件小小的事開始，行動本身就是一種方向。"},
    {"topic": "學業", "text": "如果你覺得自己總是比別人慢一點，也沒關係。重要的是你没有停下來，而是在用自己的速度往前走。"},
    {"topic": "感情", "text": "真正適合你的關係，不會要你時時刻刻表現完美，而是讓你能安心做自己，偶爾軟弱也沒關係。"},
]

# --- 核心功能 ---

@st.cache_resource
def build_therapy_index():
    texts = [d["text"] for d in RAW_THERAPY_DOCS]
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(texts)
    return RAW_THERAPY_DOCS, vectorizer, matrix

def retrieve_therapy(question: str, topic: str, top_k: int = 2):
    docs, vectorizer, matrix = build_therapy_index()
    q_vec = vectorizer.transform([question])
    sims = cosine_similarity(q_vec, matrix)[0]
    topic_bonus = np.array([0.1 if d["topic"] == topic else 0.0 for d in docs])
    sims += topic_bonus
    idx = sims.argsort()[::-1]
    selected = [docs[i]["text"] for i in idx[:top_k] if sims[i] > 0]
    return selected

def get_seed(name: str, topic: str, style: str, today: date) -> int:
    base = f"{name}-{topic}-{style}-{today.isoformat()}"
    h = hashlib.md5(base.encode("utf-8")).hexdigest()
    return int(h, 16)

def generate_fortune(name: str, topic: str, style: str):
    today = date.today()
    seed = get_seed(name, topic, style, today)
    random.seed(seed)

    luck_score = random.choices([1, 2, 3, 4, 5], weights=[1, 2, 3, 2, 1], k=1)[0]
    luck = LUCK_LEVELS[luck_score]
    advice_topic = ADVICE_BY_TOPIC.get(topic, ADVICE_BY_TOPIC["綜合"])
    short_advice = advice_topic[luck_score]

    if style.startswith("東方"):
        opening = random.choice(OPENING_LINES)
        if luck_score >= 4:
            middle, ending = random.choice(MIDDLE_LINES_GOOD), random.choice(ENDING_LINES_GOOD)
        elif luck_score == 3:
            middle, ending = random.choice(MIDDLE_LINES_NEUTRAL), random.choice(ENDING_LINES_NEUTRAL)
        else:
            middle, ending = random.choice(MIDDLE_LINES_BAD), random.choice(ENDING_LINES_BAD)
        
        poem = f"{opening}\n{middle}\n{ending}"
        stick_no = random.randint(1, 100)

        explanations = {
            5: "此籤多主順勢而上，表示近期整體氣勢不錯，只要保持腳踏實地與穩健，就有機會迎來好結果。",
            4: "此籤多主順勢而上，表示近期整體氣勢不錯，只要保持腳踏實地與穩健，就有機會迎來好結果。",
            3: "此籤意在提醒：目前情勢大致平穩，不必過度擔心，但仍需留心細節，穩中求進。",
            2: "此籤略帶考驗，適合先調整心態與腳步，多觀察、多準備，暫時不宜躁進。",
            1: "此籤帶有警示意味，提醒你近期行事要多留意風險，能退一步時就不要逞強，先保護好自己。",
        }
        
        return {
            "style": "東方籤詩", "title": f"第 {stick_no} 號籤 ({luck})",
            "main_text": poem, "explanation": explanations[luck_score],
            "short_advice": short_advice, "topic": topic, "date": today,
        }
    else: # 西方占卜
        archetype = random.choice(ARCHETYPES)
        if luck_score >= 4:
            keyword, message = random.choice(KEYWORDS_GOOD), random.choice(WEST_MESSAGES_GOOD)
        elif luck_score == 3:
            keyword, message = random.choice(KEYWORDS_NEUTRAL), random.choice(WEST_MESSAGES_NEUTRAL)
        else:
            keyword, message = random.choice(KEYWORDS_BAD), random.choice(WEST_MESSAGES_BAD)

        main_text = f"【牌面主題】\n{archetype}\n\n【今日關鍵字】\n{keyword}\n\n【牌面訊息】\n{message}"
        explanation = f"這張牌代表的主題大致與「{keyword}」有關。它提醒你留意當下的情緒與選擇，因為這會直接影響到後續的發展。"

        return {
            "style": "西方占卜", "title": f"{archetype} ({luck})",
            "main_text": main_text, "explanation": explanation,
            "short_advice": short_advice, "topic": topic, "date": today,
        }

# --- 介面 ---

st.title("線上籤詩與心靈指引")
st.write("遇到煩惱或猶豫不決時，請在此誠心問卜，尋求一些方向。")

# Function to reset results
def reset_results():
    st.session_state.fortune_result = None
    st.session_state.therapy_result = None

# Initialize session state
if 'fortune_result' not in st.session_state:
    st.session_state.fortune_result = None
if 'therapy_result' not in st.session_state:
    st.session_state.therapy_result = None

# Input widgets in the sidebar
with st.sidebar:
    st.header("請告訴我你的問題")
    name = st.text_input("你的名字或暱稱：", value="小明", on_change=reset_results)
    topic = st.selectbox("你想問哪一方面？", ["感情", "學業", "事業", "健康", "綜合"], on_change=reset_results)
    style = st.radio("選擇問卜風格：", ["東方籤詩", "西方占卜"], horizontal=True, on_change=reset_results)
    question = st.text_area("請描述你目前想問的具體問題：", value="最近對未來有點迷惘，不知道自己適不適合現在這條路。", height=150, on_change=reset_results)
    
    submit_button = st.button("🧧 點我抽籤", use_container_width=True)

# Main logic for button click and result generation
if submit_button:
    if not name.strip() or not question.strip():
        st.warning("請務必填寫你的名字及問題。")
        reset_results()
    else:
        st.session_state.fortune_result = generate_fortune(name.strip(), topic, style)
        st.session_state.therapy_result = retrieve_therapy(question.strip(), topic)

# Display results if available
if st.session_state.fortune_result:
    fortune = st.session_state.fortune_result
    
    col_fortune, col_therapy = st.columns([2, 1])

    with col_fortune:
        st.header("給你的指引")
        st.subheader(f"✨ {fortune['style']} | {fortune['title']}")
        st.caption(f"日期：{fortune['date'].isoformat()} | 類別：{fortune['topic']}")
        
        with st.expander("詳細內容", expanded=True):
            st.markdown(f"##### **📜 內容**")
            st.markdown(f"```text\n{fortune['main_text']}\n```")
            st.markdown("##### **🤔 解說**")
            st.write(fortune["explanation"])
            st.markdown("##### **💡 簡短建議**")
            st.write(fortune["short_advice"])

    with col_therapy:
        st.header("💖 額外的心靈小語")
        therapies = st.session_state.therapy_result

        if not therapies:
            st.info("沒有找到完全匹配的心靈小語，但請相信，願意面對困惑的你已經很勇敢了。")
        else:
            for i, t in enumerate(therapies, start=1):
                st.success(f"**💬 小語 {i}**\n\n{t}")
else:
    st.info("填寫側邊欄的問題後，點擊按鈕獲取你的專屬指引。")