import streamlit as st

st.set_page_config(page_title="QUIZ POKER", layout="wide")

# --- СВЕТЛАЯ КОНТРАСТНАЯ ТЕМА (CSS) ---
st.markdown("""
<style>
    /* Основной фон — светлый */
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    
    /* Принудительно черный текст для всех полей ввода */
    input, textarea, [data-baseweb="select"] {
        color: #000000 !important;
        background-color: #f0f2f6 !important;
        border: 1px solid #cccccc !important;
    }

    /* Метки полей (Label) */
    .stMarkdown p, label p {
        color: #000000 !important;
        font-weight: 600 !important;
    }

    /* Игровой стол (светло-зеленый) */
    .poker-table {
        background: #e8f5e9;
        border: 5px solid #2e7d32;
        border-radius: 100px;
        padding: 40px;
        margin: 20px auto;
        width: 90%;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }

    /* Карточка вопроса */
    .table-card {
        background: #ffffff;
        border: 2px solid #2e7d32;
        border-radius: 15px;
        padding: 20px;
        color: #000000;
        display: inline-block;
        min-width: 350px;
    }

    /* Бокс игрока */
    .player-box {
        background: #f8f9fa;
        border: 2px solid #dee2e6;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        margin-bottom: 10px;
    }

    .pot-text {
        color: #2e7d32;
        font-size: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- ИНИЦИАЛИЗАЦИЯ ---
@st.cache_resource
def get_state():
    return {
        "players": {}, "bank": 0, "game_started": False,
        "question": "", "hint_1": "", "hint_2": "", "answer": "", 
        "show_answer": False, "player_answers": {}
    }

data = get_state()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Настройки")
    pwd = st.text_input("Пароль администратора", type="password")
    is_admin = (pwd == "1234")
    
    if data["game_started"] and not is_admin:
        if "my_role" not in st.session_state: st.session_state.my_role = "---"
        st.session_state.my_role = st.selectbox("Выберите свое имя:", ["---"] + list(data["players"].keys()))

    if is_admin and st.button("🚨 СБРОС ИГРЫ"):
        data.update({"players": {}, "bank": 0, "game_started": False, "player_answers": {}})
        st.rerun()

# --- ЛОГИКА ЭКРАНОВ ---
if not data["game_started"]:
    st.title("🃏 ИНТЕЛЛЕКТУАЛЬНЫЙ ПОКЕР")
    if is_admin:
        n = st.slider("Количество игроков", 2, 6, 2)
        names = [st.text_input(f"Имя игрока {i+1}", key=f"n_{i}") for i in range(n)]
        if st.button("ОТКРЫТЬ СТОЛ"):
            valid = {name: 1000 for name in names if name}
            data.update({"players": valid, "player_answers": {n: "" for n in valid}, "game_started": True})
            st.rerun()
    else:
        st.info("Ожидайте начала игры ведущим...")

else:
    # ПАНЕЛЬ ВЕДУЩЕГО
    if is_admin:
        with st.expander("📝 УПРАВЛЕНИЕ ВОПРОСОМ", expanded=True):
            q = st.text_area("Вопрос", value=data["question"])
            h1 = st.text_input("Подсказка 1", value=data["hint_1"])
            h2 = st.text_input("Подсказка 2", value=data["hint_2"])
            ans = st.text_input("Правильный ответ", value=data["answer"])
            
            col1, col2 = st.columns(2)
            if col1.button("ОБНОВИТЬ ВОПРОС"):
                data.update({
                    "question": q, "hint_1": h1, "hint_2": h2, "answer": ans,
                    "show_answer": False, "player_answers": {n: "" for n in data["players"]}
                })
                st.rerun()
            if col2.button("ПОКАЗАТЬ ОТВЕТ"):
                data.update({"show_answer": True})
                st.rerun()

    # СТОЛ
    st.markdown(f"""
    <div class="poker-table">
        <div class="pot-text">БАНК (POT)</div>
        <div style="font-size: 40px; color: #2e7d32; font-weight: bold;">$ {data['bank']}</div>
        <div class="table-card">
            <div style="font-size: 22px; font-weight: bold;">{data['question'] if data['question'] else 'Ожидание вопроса...'}</div>
            <div style="margin-top: 10px; color: #666; font-size: 14px;">
                {f"Подсказка 1: {data['hint_1']}" if data['hint_1'] else ""} | {f"Подсказка 2: {data['hint_2']}" if data['hint_2'] else ""}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if data["show_answer"]:
        st.success(f"**ПРАВИЛЬНЫЙ ОТВЕТ:** {data['answer']}")

    # ИГРОКИ
    p_names = list(data["players"].keys())
    cols = st.columns(len(p_names))
    
    for i, name in enumerate(p_names):
        with cols[i]:
            st.markdown(f"""
            <div class="player-box">
                <div style="color: #666;">{name}</div>
                <div style="font-size: 22px; font-weight: bold; color: #1565c0;">{data['players'][name]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if is_admin:
                bet = st.number_input("Ставка", key=f"b_{name}", step=50, label_visibility="collapsed")
                if st.button("В БАНК", key=f"btn_{name}"):
                    data["players"][name] -= bet
                    data["bank"] += bet
                    st.rerun()
            
            elif st.session_state.get("my_role") == name:
                my_ans = data["player_answers"].get(name, "")
                if my_ans:
                    st.write(f"✅ Отправлено: **{my_ans}**")
                else:
                    u_in = st.text_input("Ваш ответ", key=f"in_{name}", label_visibility="collapsed")
                    if st.button("ОТПРАВИТЬ", key=f"snd_{name}"):
                        data["player_answers"][name] = u_in
                        st.rerun()

    # МОНИТОР ДЛЯ ВЕДУЩЕГО
    if is_admin:
        st.divider()
        st.subheader("Ответы игроков:")
        for n, a in data["player_answers"].items():
            if a: st.write(f"👤 **{n}:** {a}")
        
        winners = st.multiselect("Победители (разделят банк):", p_names)
        if winners and st.button("💰 ВРУЧИТЬ ВЫИГРЫШ"):
            share = data['bank'] // len(winners)
            for w in winners: data["players"][w] += share
            data["bank"] = 0
            st.rerun()
    else:
        st.button("🔄 ОБНОВИТЬ ТАБЛО")
