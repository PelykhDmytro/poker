import streamlit as st

st.set_page_config(page_title="POKER QUIZ", layout="wide")

# --- УЛУЧШЕННЫЕ СТИЛИ (CSS) ДЛЯ ЧИТАЕМОСТИ ---
st.markdown("""
<style>
    /* Основной фон приложения */
    .stApp { background-color: #0a0a0a; }
    
    /* ФИКС ШРИФТОВ: Принудительно делаем текст в инпутах белым */
    input, textarea, select, .stSelectbox div {
        color: white !important;
        background-color: #262730 !important;
        -webkit-text-fill-color: white !important;
    }

    /* Цвет меток (Label) над полями */
    label p {
        color: #fbbf24 !important;
        font-weight: bold !important;
    }

    /* Игровой стол */
    .poker-table {
        background: radial-gradient(circle, #1a472a 0%, #071a0f 100%);
        border: 8px solid #3d2b1f;
        border-radius: 150px;
        padding: 40px;
        margin: 20px auto;
        width: 90%;
        box-shadow: inset 0 0 80px #000, 0 15px 30px rgba(0,0,0,0.7);
        text-align: center;
    }

    /* Карточка с вопросом в центре */
    .table-card {
        background: rgba(0, 0, 0, 0.7);
        border: 2px solid #fbbf24;
        border-radius: 15px;
        padding: 20px;
        color: white;
        display: inline-block;
        min-width: 350px;
        box-shadow: 0 0 20px rgba(251, 191, 36, 0.2);
    }

    /* Бокс игрока */
    .player-box {
        background: #1e1e1e;
        border: 1px solid #444;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5);
    }

    .pot-text {
        font-family: 'Arial Black', sans-serif;
        color: #fbbf24;
        font-size: 22px;
        letter-spacing: 2px;
    }
</style>
""", unsafe_allow_html=True)

# --- ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ ---
@st.cache_resource
def get_state():
    return {
        "players": {}, "bank": 0, "game_started": False,
        "question": "", "hint_1": "", "hint_2": "", "answer": "", 
        "show_answer": False, "player_answers": {}
    }

data = get_state()

# --- SIDEBAR (НАСТРОЙКИ) ---
with st.sidebar:
    st.title("⚙️ SETUP")
    pwd = st.text_input("Пароль", type="password")
    is_admin = (pwd == "1234")
    
    if data["game_started"] and not is_admin:
        if "my_role" not in st.session_state: st.session_state.my_role = "---"
        st.session_state.my_role = st.selectbox("Кто вы?", ["---"] + list(data["players"].keys()))

    if is_admin and st.button("🚨 СБРОСИТЬ ИГРУ"):
        data.update({"players": {}, "bank": 0, "game_started": False, "player_answers": {}})
        st.rerun()

# --- ГЛАВНЫЙ ЭКРАН ---
if not data["game_started"]:
    st.title("🃏 QUIZ POKER")
    if is_admin:
        n = st.slider("Сколько игроков?", 2, 6, 2)
        names = [st.text_input(f"Игрок {i+1}", key=f"init_{i}") for i in range(n)]
        if st.button("НАЧАТЬ ИГРУ"):
            valid = {name: 1000 for name in names if name}
            data.update({"players": valid, "player_answers": {n: "" for n in valid}, "game_started": True})
            st.rerun()
    else:
        st.info("Ожидайте, пока крупье откроет стол...")

else:
    # ИНТЕРФЕЙС ВЕДУЩЕГО
    if is_admin:
        with st.expander("🛠 УПРАВЛЕНИЕ ВОПРОСОМ", expanded=False):
            q_val = st.text_area("Текст вопроса", value=data["question"])
            h1_val = st.text_input("Подсказка 1", value=data["hint_1"])
            h2_val = st.text_input("Подсказка 2", value=data["hint_2"])
            a_val = st.text_input("Верный ответ", value=data["answer"])
            
            c1, c2 = st.columns(2)
            if c1.button("ОБНОВИТЬ НА СТОЛЕ"):
                data.update({
                    "question": q_val, "hint_1": h1_val, "hint_2": h2_val, 
                    "answer": a_val, "show_answer": False, 
                    "player_answers": {n: "" for n in data["players"]}
                })
                st.rerun()
            if c2.button("ПОКАЗАТЬ ОТВЕТ"):
                data.update({"show_answer": True})
                st.rerun()

    # СТОЛ
    st.markdown(f"""
    <div class="poker-table">
        <div class="pot-text">POT</div>
        <div style="font-size: 42px; color: #fff; font-weight: bold; margin-bottom: 15px;">$ {data['bank']}</div>
        <div class="table-card">
            <div style="color: #fbbf24; font-size: 14px; margin-bottom: 5px;">BOARD</div>
            <div style="font-size: 24px; font-weight: bold;">{data['question'] if data['question'] else 'Waiting...'}</div>
            <div style="margin-top: 10px; color: #888; font-size: 13px;">
                {f"H1: {data['hint_1']}" if data['hint_1'] else ""} | {f"H2: {data['hint_2']}" if data['hint_2'] else ""}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if data["show_answer"]:
        st.success(f"✅ ПРАВИЛЬНЫЙ ОТВЕТ: {data['answer']}")

    # ИГРОКИ
    p_names = list(data["players"].keys())
    cols = st.columns(len(p_names))
    
    for i, name in enumerate(p_names):
        with cols[i]:
            st.markdown(f"""
            <div class="player-box">
                <div style="color: #aaa; font-size: 14px;">{name}</div>
                <div style="color: #4ade80; font-size: 24px; font-weight: bold;">{data['players'][name]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if is_admin:
                bet = st.number_input("Ставка", key=f"bet_{name}", step=50, label_visibility="collapsed")
                if st.button("BET", key=f"btn_{name}"):
                    data["players"][name] -= bet
                    data["bank"] += bet
                    st.rerun()
            
            elif st.session_state.get("my_role") == name:
                ans = data["player_answers"].get(name, "")
                if ans:
                    st.info(f"Твой ответ: {ans}")
                else:
                    u_in = st.text_input("Ваш ответ", key=f"in_{name}", label_visibility="collapsed")
                    if st.button("ОТПРАВИТЬ", key=f"snd_{name}"):
                        data["player_answers"][name] = u_in
                        st.rerun()

    # ОТВЕТЫ (ДЛЯ АДМИНА)
    if is_admin:
        st.divider()
        st.subheader("📝 Монитор ответов")
        for n, a in data["player_answers"].items():
            if a: st.write(f"**{n}:** {a}")
        
        winners = st.multiselect("Выберите победителей:", p_names)
        if winners and st.button("🎉 РАЗДЕЛИТЬ БАНК"):
            share = data['bank'] // len(winners)
            for w in winners: data["players"][w] += share
            data["bank"] = 0
            st.rerun()
    else:
        st.button("🔄 ОБНОВИТЬ СТОЛ")
