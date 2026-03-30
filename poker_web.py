import streamlit as st

st.set_page_config(page_title="POKER QUIZ", layout="wide")

# --- СТИЛИ (CSS) ---
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; }
    
    /* Игровой стол */
    .poker-table {
        background: radial-gradient(circle, #1a472a 0%, #071a0f 100%);
        border: 8px solid #3d2b1f;
        border-radius: 150px;
        padding: 50px;
        margin: 20px auto;
        width: 95%;
        box-shadow: inset 0 0 100px #000, 0 20px 40px rgba(0,0,0,0.8);
        text-align: center;
    }

    /* Карточка с вопросом */
    .table-card {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid #fbbf24;
        border-radius: 15px;
        padding: 25px;
        color: white;
        display: inline-block;
        min-width: 400px;
    }

    /* Место игрока */
    .player-box {
        background: #1a1a1a;
        border: 1px solid #444;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    /* Исправление видимости текста в полях */
    input {
        color: white !important;
        background-color: #262730 !important;
    }
    
    .pot-text {
        font-family: 'Arial Black', sans-serif;
        color: #fbbf24;
        font-size: 24px;
        letter-spacing: 3px;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- ИНИЦИАЛИЗАЦИЯ ДАННЫХ ---
@st.cache_resource
def init_data():
    return {
        "players": {}, 
        "bank": 0, 
        "game_started": False,
        "question": "", 
        "hint_1": "", 
        "hint_2": "", 
        "answer": "", 
        "show_answer": False, 
        "player_answers": {}
    }

data = init_data()

# --- БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.title("⚙️ Настройки")
    pwd = st.text_input("Пароль ведущего", type="password")
    is_admin = (pwd == "1234")
    
    if data["game_started"] and not is_admin:
        if "my_role" not in st.session_state: 
            st.session_state.my_role = "---"
        st.session_state.my_role = st.selectbox("Ваше имя:", ["---"] + list(data["players"].keys()))

    if is_admin and st.button("🚨 ПОЛНЫЙ СБРОС"):
        data.update({"players": {}, "bank": 0, "game_started": False, "player_answers": {}})
        st.rerun()

# --- ЛОГИКА ЭКРАНОВ ---
if not data["game_started"]:
    st.title("🃏 QUIZ POKER ROOM")
    if is_admin:
        n = st.slider("Мест за столом", 2, 6, 2)
        names = [st.text_input(f"Игрок {i+1}", key=f"setup_{i}") for i in range(n)]
        if st.button("ОТКРЫТЬ СТОЛ"):
            valid_p = {name: 1000 for name in names if name}
            data.update({
                "players": valid_p, 
                "player_answers": {n: "" for n in valid_p}, 
                "game_started": True
            })
            st.rerun()
    else:
        st.info("Ожидание крупье...")
else:
    # ПАНЕЛЬ УПРАВЛЕНИЯ (ТОЛЬКО АДМИН)
    if is_admin:
        with st.expander("🛠 УПРАВЛЕНИЕ ТУРОМ", expanded=False):
            q_in = st.text_area("Текст вопроса", value=data["question"])
            h1_in = st.text_input("Подсказка 1", value=data["hint_1"])
            h2_in = st.text_input("Подсказка 2", value=data["hint_2"])
            a_in = st.text_input("Правильный ответ", value=data["answer"])
            if st.button("РАЗДАТЬ ВОПРОС"):
                data.update({
                    "question": q_in, "hint_1": h1_in, "hint_2": h2_in, 
                    "answer": a_in, "show_answer": False, 
                    "player_answers": {n: "" for n in data["players"]}
                })
                st.rerun()
            if st.button("ОТКРЫТЬ ОТВЕТ"):
                data.update({"show_answer": True})
                st.rerun()

    # ИГРОВОЙ СТОЛ
    st.markdown(f"""
    <div class="poker-table">
        <div class="pot-text">POT</div>
        <div style="font-size: 48px; color: #fff; font-weight: bold; margin-bottom: 20px;">$ {data['bank']}</div>
        <div class="table-card">
            <div style="color: #fbbf24; font-weight: bold; margin-bottom: 10px;">ВОПРОС</div>
            <div style="font-size: 26px; font-weight: bold;">{data['question'] if data['question'] else 'Ждем вопрос...'}</div>
            <div style="margin-top: 15px; color: #aaa; font-size: 14px;">
                {data['hint_1']} | {data['hint_2']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if data["show_answer"]:
        st.success(f"### ✅ ОТВЕТ: {data['answer']}")

    # ИГРОКИ (СТОЛБЦЫ)
    p_names = list(data["players"].keys())
    if p_names:
        cols = st.columns(len(p_names))
        for i, name in enumerate(p_names):
            with cols[i]:
                # Карточка игрока
                st.markdown(f"""
                <div class="player-box">
                    <div style="color: #888; font-size: 14px;">{name}</div>
                    <div style="color: #4ade80; font-size: 24px; font-weight: bold;">{data['players'][name]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Кнопки для админа
                if is_admin:
                    bet = st.number_input("Ставка", key=f"b_{name}", step=50, label_visibility="collapsed")
                    if st.button("В БАНК", key=f"btn_{name}"):
                        data["players"][name] -= bet
                        data["bank"] += bet
                        st.rerun()
                
                # Кнопка для игрока
                elif st.session_state.get("my_role") == name:
                    ans_val = data["player_answers"].get(name, "")
                    if ans_val:
                        st.markdown(f"<div style='color:#fbbf24; text-align:center;'>Принято: <b>{ans_val}</b></div>", unsafe_allow_html=True)
                    else:
                        u_in = st.text_input("Ответ", key=f"in_{name}", label_visibility="collapsed")
                        if st.button("ОТПРАВИТЬ", key=f"send_{name}"):
                            if u_in:
                                data["player_answers"][name] = u_in
                                st.rerun()

    # МОНИТОР ОТВЕТОВ (ДЛЯ АДМИНА)
    if is_admin:
        st.divider()
        st.subheader("📝 Ответы игроков")
        for n, a in data["player_answers"].items():
            if a: st.write(f"**{n}:** {a}")
        
        winners = st.multiselect("Кто забирает банк?", p_names)
        if winners and st.button("🎉 ВЫПЛАТИТЬ"):
            share = data['bank'] // len(winners)
            for w in winners: data["players"][w] += share
            data["bank"] = 0
            st.rerun()
    else:
        st.button("🔄 ОБНОВИТЬ")
