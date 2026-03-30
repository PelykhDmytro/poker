import streamlit as st

st.set_page_config(page_title="Интеллектуальная Игра", layout="wide")

# Инициализация состояния
if 'poker_data' not in st.session_state:
    st.session_state.poker_data = {
        "players": {},
        "bank": 0,
        "game_started": False,
        "question": "",
        "hint_1": "",
        "hint_2": ""
    }

# --- ПРОВЕРКА ПАРОЛЯ В БОКОВОЙ ПАНЕЛИ ---
st.sidebar.header("🔑 Панель Ведущего")
password = st.sidebar.text_input("Введите пароль", type="password")
is_admin = (password == "1234")

if not is_admin:
    st.sidebar.warning("Режим участника (только просмотр)")

st.title("🧠 Интеллектуальное Табло")

# --- ЭКРАН НАСТРОЙКИ (только для админа) ---
if not st.session_state.poker_data["game_started"]:
    if is_admin:
        st.subheader("Настройка участников")
        num_players = st.slider("Количество игроков", 2, 10, 4)
        start_chips = st.number_input("Стартовый стек", value=1000, step=100)
        
        player_names = []
        name_cols = st.columns(2)
        for i in range(num_players):
            with name_cols[i % 2]:
                name = st.text_input(f"Имя игрока {i+1}", value=f"Игрок {i+1}", key=f"name_input_{i}")
                player_names.append(name)
        
        if st.button("🚀 НАЧАТЬ ИГРУ"):
            st.session_state.poker_data["players"] = {name: start_chips for name in player_names}
            st.session_state.poker_data["game_started"] = True
            st.rerun()
    else:
        st.info("Ждем, пока Ведущий настроит игру...")

# --- ИГРОВОЙ ЭКРАН ---
else:
    # --- БЛОК ВОПРОСА И ПОДСКАЗОК ---
    st.divider()
    if is_admin:
        with st.expander("📝 РЕДАКТИРОВАТЬ ВОПРОС И ПОДСКАЗКИ", expanded=True):
            q = st.text_area("Текст вопроса", value=st.session_state.poker_data["question"])
            h1 = st.text_input("Подсказка №1", value=st.session_state.poker_data["hint_1"])
            h2 = st.text_input("Подсказка №2", value=st.session_state.poker_data["hint_2"])
            if st.button("ОБНОВИТЬ ДЛЯ ВСЕХ"):
                st.session_state.poker_data["question"] = q
                st.session_state.poker_data["hint_1"] = h1
                st.session_state.poker_data["hint_2"] = h2
                st.rerun()
    
    # Визуализация для игроков
    st.markdown(f"""
    <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border: 2px solid #0e1117; margin-bottom:20px">
        <h2 style="color:#0e1117; text-align:center;">❓ Вопрос</h2>
        <p style="font-size:24px; text-align:center;">{st.session_state.poker_data['question'] if st.session_state.poker_data['question'] else 'Ожидайте вопрос...'}</p>
        <hr>
        <div style="display: flex; justify-content: space-around;">
            <div style="text-align:center;"><b>💡 Подсказка 1:</b><br>{st.session_state.poker_data['hint_1']}</div>
            <div style="text-align:center;"><b>💡 Подсказка 2:</b><br>{st.session_state.poker_data['hint_2']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- БАНК И ИГРОКИ ---
    st.info(f"## 💰 В БАНКЕ: {st.session_state.poker_data['bank']}")

    players = st.session_state.poker_data["players"]
    cols = st.columns(min(len(players), 4)) 

    for i, (name, stack) in enumerate(players.items()):
        with cols[i % 4]:
            st.markdown(f"### {name}")
            st.metric("Фишки", stack)
            
            if is_admin:
                bet = st.number_input("Ставка", min_value=0, max_value=stack, key=f"bet_{name}", step=10)
                if st.button(f"В банк 📥", key=f"btn_{name}"):
                    if bet > 0:
                        st.session_state.poker_data["players"][name] -= bet
                        st.session_state.poker_data["bank"] += bet
                        st.rerun()

    if is_admin:
        st.divider()
        st.subheader("🏆 Раздача банка")
        winners = st.multiselect("Выберите победителей:", list(players.keys()))
        
        if winners:
            split_amount = st.session_state.poker_data['bank'] // len(winners)
            if st.button(f"РАЗДЕЛИТЬ ПО {split_amount} 🎉"):
                for w in winners:
                    st.session_state.poker_data["players"][w] += split_amount
                st.session_state.poker_data["bank"] = 0
                st.rerun()

        if st.sidebar.button("🔄 Полный сброс игры"):
            st.session_state.poker_data = {"players": {}, "bank": 0, "game_started": False, "question": "", "hint_1": "", "hint_2": ""}
            st.rerun()
