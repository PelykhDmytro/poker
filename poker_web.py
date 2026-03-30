import streamlit as st

st.set_page_config(page_title="POKER QUIZ NIGHT", layout="wide")

# --- UI DESIGN (STYLING) ---
st.markdown("""
<style>
    /* Основной фон всей страницы */
    .stApp {
        background-color: #121212;
    }

    /* Игровой стол */
    .poker-table {
        background: radial-gradient(circle, #1a4a2e 0%, #0d2b1a 100%);
        border: 10px solid #3d2b1f;
        border-radius: 100px;
        padding: 40px;
        margin-bottom: 30px;
        box-shadow: inset 0 0 50px #000, 0 15px 30px rgba(0,0,0,0.7);
        text-align: center;
    }

    /* Карточка вопроса на столе */
    .question-box {
        background: rgba(0,0,0,0.6);
        border: 2px solid #fbbf24;
        border-radius: 20px;
        padding: 20px;
        color: #fff;
    }

    /* Карточки игроков (как на скриншоте) */
    .player-seat {
        background: rgba(20, 20, 20, 0.9);
        border: 1px solid #444;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        margin-bottom: 10px;
    }
    .player-name {
        color: #fff;
        font-size: 16px;
        font-weight: bold;
        border-bottom: 1px solid #333;
        padding-bottom: 5px;
    }
    .player-chips {
        color: #10b981;
        font-size: 22px;
        font-weight: 800;
        margin-top: 5px;
    }

    /* Стилизация ввода (чтобы текст был виден) */
    input {
        background-color: #222 !important;
        color: white !important;
        border: 1px solid #444 !important;
    }
    
    /* Золотой банк */
    .pot-label {
        font-size: 24px;
        color: #fbbf24;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Фиксация текста кнопок */
    .stButton>button {
        border-radius: 5px;
        background-color: #3d2b1f;
        color: #fbbf24;
        border: 1px solid #fbbf24;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGIC ---
@st.cache_resource
def get_common_data():
    return {
        "players": {}, "bank": 0, "game_started": False,
        "question": "", "hint_1": "", "hint_2": "", "answer": "", 
        "show_answer": False, "player_answers": {}
    }

common_data = get_common_data()

if "my_role" not in st.session_state:
    st.session_state.my_role = "---"

# --- SIDEBAR ---
with st.sidebar:
    st.title("🃏 Лобби")
    admin_pwd = st.text_input("Пароль", type="password")
    is_admin = (admin_pwd == "1234")
    
    if common_data["game_started"] and not is_admin:
        st.session_state.my_role = st.selectbox(
            "Ваше место за столом:", 
            ["---"] + list(common_data["players"].keys()),
            index=0 if st.session_state.my_role not in common_data["players"] else list(common_data["players"].keys()).index(st.session_state.my_role) + 1
        )
    
    if is_admin:
        if st.button("🚨 ЗАВЕРШИТЬ СЕССИЮ"):
            common_data.update({"players": {}, "bank": 0, "game_started": False, "player_answers": {}})
            st.rerun()

# --- MAIN SCREEN ---
if not common_data["game_started"]:
    st.title("🎲 POKER QUIZ NIGHT")
    if is_admin:
        num = st.slider("Количество игроков", 2, 6, 4)
        names = [st.text_input(f"Игрок {i+1}", key=f"p_{i}") for i in range(num)]
        if st.button("ОТКРЫТЬ СТОЛ"):
            v_names = {n: 1000 for n in names if n}
            common_data.update({"players": v_names, "player_answers": {n: "" for n in v_names}, "game_started": True})
            st.rerun()
    else:
        st.info("Ожидание открытия стола ведущим...")
else:
    # --- ВЕДУЩИЙ ---
    if is_admin:
        with st.expander("💼 ПАНЕЛЬ КРУПЬЕ", expanded=False):
            q_in = st.text_input("Вопрос", value=common_data["question"])
            h1_in = st.text_input("Подсказка 1", value=common_data["hint_1"])
            h2_in = st.text_input("Подсказка 2", value=common_data["hint_2"])
            ans_in = st.text_input("Ответ", value=common_data["answer"])
            if st.button("РАЗДАТЬ КАРТЫ (ОБНОВИТЬ)"):
                common_data.update({"question": q_in, "hint_1": h1_in, "hint_2": h2_in, "answer": ans_in, "show_answer": False, "player_answers": {n: "" for n in common_data["players"]}})
                st.rerun()
            if st.button("ВСКРЫТЬСЯ (ПОКАЗАТЬ ОТВЕТ)"):
                common_data.update({"show_answer": True})
                st.rerun()

    # --- ИГРОВОЙ СТОЛ ---
    st.markdown(f"""
    <div class="poker-table">
        <div class="pot-label">POT</div>
        <div style="font-size: 45px; color: #fff; font-weight: bold; margin-bottom: 20px;">$ {common_data['bank']}</div>
        
        <div class="question-box">
            <h2 style="color: #fbbf24; margin-top:0;">ВОПРОС НА КОНУ:</h2>
            <p style="font-size: 28px; line-height: 1.2;">{common_data['question'] if common_data['question'] else 'Тасуем колоду...'}</p>
            <div style="display: flex; justify-content: center; gap: 40px; color: #94a3b8; font-style: italic;">
                <span>{common_data['hint_1']}</span>
                <span>{common_data['hint_2']}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if common_data["show_answer"]:
        st.warning(f"### ✅ ПРАВИЛЬНЫЙ ОТВЕТ: {common_data['answer']}")

    # --- МЕСТА ИГРОКОВ ---
    players = common_data["players"]
    cols = st.columns(len(players))
    
    for i, (name, stack) in enumerate(players.items()):
        with cols[i]:
            # Визуализация места
            st.markdown(f"""
            <div class="player-seat">
                <div class="player-name">{name}</div>
                <div class="player-chips">{stack}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Действия
            if is_admin:
                bet = st.number_input("Ставка", key=f"b_{name}", step=50, label_visibility="collapsed")
                if st.button("В БАНК", key=f"btn_{name}"):
                    common_data["players"][name] -= bet
                    common_data["bank"] += bet
                    st.rerun()
            
            elif st.session_state.my_role == name:
                ans = common_data["player_answers"].get(name, "")
                if ans:
                    st.markdown(f"<div style='color: #fbbf24; text-align:center;'>Ваш ответ:<br><b>{ans}</b></div>", unsafe_allow_html=True)
                else:
                    u_in = st.text_input("Ответ", key=f"in_{name}", label_visibility="collapsed")
                    if st.button("CALL", key=f"snd_{name}"):
                        if u_in:
                            common_data["player_answers"][name] = u_in
                            st.rerun()

    # --- МОНИТОР ВЕДУЩЕГО ---
    if is_admin:
        st.divider()
        st.subheader("🔔 Карты игроков")
        for name, ans in common_data["player_answers"].items():
            if ans:
                st.markdown(f"<div style='background:#222; padding:10px; border-radius:5px; margin-bottom:5px;'><b style='color:#fbbf24'>{name}:</b> <span style='font-size:24px; color:#fff'>{ans}</span></div>", unsafe_allow_html=True)

        winners = st.multiselect("Кто забирает банк?", list(players.keys()))
        if winners and st.button("🎉 ВЫПЛАТИТЬ ВЫИГРЫШ"):
            split = common_data['bank'] // len(winners)
            for w in winners: common_data["players"][w] += split
            common_data["bank"] = 0
            st.rerun()
    else:
        if st.button("🔄 ОБНОВИТЬ СТОЛ"):
            st.rerun()
