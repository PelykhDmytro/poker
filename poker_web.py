import streamlit as st

# Конфигурация страницы
st.set_page_config(page_title="QUIZ POKER", layout="wide")

# --- СВЕТЛЫЙ КОНТРАСТНЫЙ ДИЗАЙН ---
st.markdown("""
<style>
    /* Фон всей страницы - светло-серый для контраста */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Основной текст - всегда темно-синий/черный */
    h1, h2, h3, p, span, label {
        color: #1a1c23 !important;
    }

    /* Карточка вопроса - Белая с четкой рамкой */
    .question-card {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 15px;
        border: 2px solid #dee2e6;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    /* Текст вопроса - Очень крупный и темный */
    .question-text {
        font-size: 42px !important;
        font-weight: 800 !important;
        color: #0d6efd !important;
        margin: 20px 0;
    }

    /* Карточки игроков */
    .player-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #ced4da;
        text-align: center;
        margin-bottom: 10px;
    }

    /* Блок принятого ответа для игрока */
    .answer-box {
        background-color: #e7f1ff;
        color: #0c4128;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #b6d4fe;
        font-size: 24px !important;
        font-weight: bold;
        text-align: center;
    }

    /* Ответы для ведущего - Крупно и понятно */
    .admin-answer-item {
        background: white;
        padding: 15px;
        border-left: 8px solid #0d6efd;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- ЛОГИКА ДАННЫХ ---
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

# --- БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.header("🔐 Вход")
    admin_pwd = st.text_input("Пароль Ведущего", type="password")
    is_admin = (admin_pwd == "1234")
    
    if common_data["game_started"] and not is_admin:
        st.session_state.my_role = st.selectbox(
            "Выберите ваше имя:", 
            ["---"] + list(common_data["players"].keys()),
            index=0 if st.session_state.my_role not in common_data["players"] else list(common_data["players"].keys()).index(st.session_state.my_role) + 1
        )
    
    if is_admin:
        st.divider()
        if st.button("🚨 Сбросить игру"):
            common_data.update({"players": {}, "bank": 0, "game_started": False, "player_answers": {}})
            st.rerun()

st.title("🏆 ИНТЕЛЛЕКТУАЛЬНЫЙ ПОКЕР")

if not common_data["game_started"]:
    if is_admin:
        num = st.number_input("Количество игроков", 2, 10, 2)
        names = [st.text_input(f"Имя игрока {i+1}", key=f"setup_{i}") for i in range(num)]
        if st.button("🚀 НАЧАТЬ ИГРУ"):
            v_names = {n: 1000 for n in names if n}
            common_data.update({"players": v_names, "player_answers": {n: "" for n in v_names}, "game_started": True})
            st.rerun()
    else:
        st.info("Ждем пока ведущий создаст игру...")
        st.button("🔄 Обновить")

else:
    # --- ИНТЕРФЕЙС ВЕДУЩЕГО ---
    if is_admin:
        with st.expander("📝 УПРАВЛЕНИЕ ВОПРОСОМ", expanded=True):
            q_in = st.text_input("Текст вопроса", value=common_data["question"])
            c_h1, c_h2 = st.columns(2)
            h1_in = c_h1.text_input("Подсказка 1", value=common_data["hint_1"])
            h2_in = c_h2.text_input("Подсказка 2", value=common_data["hint_2"])
            ans_in = st.text_input("Правильный ответ", value=common_data["answer"])
            
            b1, b2, b3 = st.columns(3)
            if b1.button("📢 НОВЫЙ ТУР"):
                common_data.update({
                    "question": q_in, "hint_1": h1_in, "hint_2": h2_in, "answer": ans_in,
                    "show_answer": False, "player_answers": {n: "" for n in common_data["players"]}
                })
                st.rerun()
            if b2.button("💡 ОБНОВИТЬ ДАННЫЕ"):
                common_data.update({"question": q_in, "hint_1": h1_in, "hint_2": h2_in, "answer": ans_in})
                st.rerun()
            if b3.button("👁️ ПОКАЗАТЬ ОТВЕТ"):
                common_data.update({"show_answer": True})
                st.rerun()

    # --- ТАБЛО (ВИДЯТ ВСЕ) ---
    st.markdown(f"""
    <div class="question-card">
        <div style="color: #6c757d; font-weight: bold; letter-spacing: 2px;">ТЕКУЩИЙ ВОПРОС</div>
        <div class="question-text">{common_data['question'] if common_data['question'] else 'Ожидание вопроса...'}</div>
        <div style="display: flex; justify-content: space-around; margin-top: 20px; border-top: 1px solid #eee; padding-top: 20px;">
            <div style="font-size: 18px;">💡 <b>Подсказка 1:</b> {common_data['hint_1']}</div>
            <div style="font-size: 18px;">💡 <b>Подсказка 2:</b> {common_data['hint_2']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if common_data["show_answer"]:
        st.success(f"### ✅ ПРАВИЛЬНЫЙ ОТВЕТ: {common_data['answer']}")

    # --- БАНК ---
    st.markdown(f"<h1 style='text-align:center; color:#dc3545; font-size: 50px;'>💰 БАНК: {common_data['bank']}</h1>", unsafe_allow_html=True)

    # --- ИГРОКИ ---
    players = common_data["players"]
    cols = st.columns(len(players))
    
    for i, (name, stack) in enumerate(players.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="player-card">
                <div style="font-size: 20px; font-weight: bold;">{name}</div>
                <div style="font-size: 32px; color: #198754; font-weight: 800;">{stack}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if is_admin:
                bet = st.number_input("Bet", key=f"b_{name}", step=50, label_visibility="collapsed")
                if st.button("В БАНК", key=f"btn_{name}"):
                    common_data["players"][name] -= bet
                    common_data["bank"] += bet
                    st.rerun()
            
            elif st.session_state.my_role == name:
                ans = common_data["player_answers"].get(name, "")
                if ans:
                    st.markdown(f"<div class='answer-box'>{ans}</div>", unsafe_allow_html=True)
                else:
                    u_input = st.text_input("Ваш ответ", key=f"in_{name}", label_visibility="collapsed")
                    if st.button("ОТПРАВИТЬ", key=f"snd_{name}"):
                        if u_input:
                            common_data["player_answers"][name] = u_input
                            st.rerun()

    # --- ОТВЕТЫ ДЛЯ ВЕДУЩЕГО ---
    if is_admin:
        st.divider()
        st.subheader("📊 Ответы игроков в реальном времени")
        for name, ans in common_data["player_answers"].items():
            if ans:
                st.markdown(f"""
                <div class="admin-answer-item">
                    <span style="color: #6c757d;">{name}:</span><br>
                    <span style="font-size: 30px; font-weight: bold;">{ans}</span>
                </div>
                """, unsafe_allow_html=True)

        winners = st.multiselect("Выберите победителей:", list(players.keys()))
        if winners and st.button("🎉 РАЗДЕЛИТЬ БАНК"):
            split = common_data['bank'] // len(winners)
            for w in winners: common_data["players"][w] += split
            common_data["bank"] = 0
            st.rerun()
    else:
        st.button("🔄 Обновить табло")
