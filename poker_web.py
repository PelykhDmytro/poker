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
        "hint_2": "",
        "answer": "",
        "show_answer": False
    }

# --- ПРОВЕРКА ПАРОЛЯ ---
st.sidebar.header("🔑 Панель Ведущего")
password = st.sidebar.text_input("Введите пароль", type="password")
is_admin = (password == "1234")

st.title("🧠 Интеллектуальное Табло")

# --- ЭКРАН НАСТРОЙКИ ---
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
    # --- БЛОК РЕДАКТИРОВАНИЯ (только админ) ---
    if is_admin:
        with st.expander("📝 УПРАВЛЕНИЕ ВОПРОСОМ", expanded=True):
            q = st.text_area("Текст вопроса", value=st.session_state.poker_data["question"])
            h1 = st.text_input("Подсказка №1", value=st.session_state.poker_data["hint_1"])
            h2 = st.text_input("Подсказка №2", value=st.session_state.poker_data["hint_2"])
            ans = st.text_input("ПРАВИЛЬНЫЙ ОТВЕТ", value=st.session_state.poker_data["answer"])
            
            c1, c2 = st.columns(2)
            if c1.button("📢 ОБНОВИТЬ ВОПРОС"):
                st.session_state.poker_data.update({"question": q, "hint_1": h1, "hint_2": h2, "answer": ans, "show_answer": False})
                st.rerun()
            if c2.button("👁️ ПОКАЗАТЬ ОТВЕТ ВСЕМ"):
                st.session_state.poker_data["show_answer"] = True
                st.rerun()

    # --- ВИЗУАЛИЗАЦИЯ ДЛЯ ВСЕХ ---
    st.markdown(f"""
    <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border: 2px solid #0e1117; margin-bottom:20px; color:#0e1117">
        <h2 style="text-align:center;">❓ Вопрос</h2>
        <p style="font-size:24px; text-align:center;">{st.session_state.poker_data['question'] if st.session_state.poker_data['question'] else 'Ожидайте вопрос...'}</p>
        <div style="display: flex; justify-content: space-around; margin-top:10px;">
            <div style="text-align:center;"><b>💡 Подсказка 1:</b><br>{st.session_state.poker_data['hint_1']}</div>
            <div style="text-align:center;"><b>💡 Подсказка 2:</b><br>{st.session_state.poker_data['hint_2']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Поле ответа (появляется только после нажатия кнопки админом)
    if st.session_state.poker_data["show_answer"]:
        st.success(f"### ✅ ПРАВИЛЬНЫЙ ОТВЕТ: {st.session_state.poker_data['answer']}")

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
                    st.session_state.poker_data["players"][name] -= bet
                    st.session_state.poker_data["bank"] += bet
                    st.rerun()

    # --- РАЗДАЧА БАНКА ---
    if is_admin:
        st.divider()
        winners = st.multiselect("Кто ответил верно?", list(players.keys()))
        if winners:
            split = st.session_state.poker_data['bank'] // len(winners)
            if st.button(f"РАЗДЕЛИТЬ ПО {split} 🎉"):
                for w in winners:
                    st.session_state.poker_data["players"][w] += split
                st.session_state.poker_data["bank"] = 0
                st.rerun()
        
        if st.sidebar.button("🔄 Сбросить игру"):
            st.session_state.poker_data = {"players": {}, "bank": 0, "game_started": False, "question": "", "hint_1": "", "hint_2": "", "answer": "", "show_answer": False}
            st.rerun()
