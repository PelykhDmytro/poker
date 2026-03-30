import streamlit as st

st.set_page_config(page_title="Интеллектуальная Игра", layout="wide")

# Инициализация состояния
if 'poker_data' not in st.session_state:
    st.session_state.poker_data = {
        "players": {}, "bank": 0, "game_started": False,
        "question": "", "hint_1": "", "hint_2": "", "answer": "", 
        "show_answer": False, "player_answers": {}
    }

st.sidebar.header("🔑 Панель Ведущего")
password = st.sidebar.text_input("Введите пароль", type="password")
is_admin = (password == "1234")

st.title("🧠 Интеллектуальное Табло")

# --- НАСТРОЙКА ИГРЫ ---
if not st.session_state.poker_data["game_started"]:
    if is_admin:
        st.subheader("Настройка участников")
        num_players = st.slider("Количество игроков", 2, 10, 4)
        start_chips = st.number_input("Стартовый стек", value=1000, step=100)
        player_names = [st.text_input(f"Имя {i+1}", value=f"Игрок {i+1}", key=f"n_{i}") for i in range(num_players)]
        if st.button("🚀 НАЧАТЬ ИГРУ"):
            st.session_state.poker_data.update({
                "players": {n: start_chips for n in player_names},
                "player_answers": {n: "" for n in player_names},
                "game_started": True
            })
            st.rerun()
    else:
        st.info("Ждем Ведущего...")

# --- ИГРОВОЙ ПРОЦЕСС ---
else:
    # ПАНЕЛЬ УПРАВЛЕНИЯ (Админ)
    if is_admin:
        with st.expander("📝 УПРАВЛЕНИЕ ТУРОМ", expanded=True):
            q = st.text_area("Текст вопроса", value=st.session_state.poker_data["question"], key="q_in")
            h1 = st.text_input("Подсказка №1", value=st.session_state.poker_data["hint_1"], key="h1_in")
            h2 = st.text_input("Подсказка №2", value=st.session_state.poker_data["hint_2"], key="h2_in")
            ans = st.text_input("ПРАВИЛЬНЫЙ ОТВЕТ", value=st.session_state.poker_data["answer"], key="ans_in")
            
            c1, c2 = st.columns(2)
            if c1.button("📢 ОБНОВИТЬ ВОПРОС"):
                st.session_state.poker_data.update({
                    "question": q, "hint_1": h1, "hint_2": h2, "answer": ans, 
                    "show_answer": False, "player_answers": {n: "" for n in st.session_state.poker_data["players"]}
                })
                st.rerun()
            if c2.button("👁️ ПОКАЗАТЬ ОТВЕТ ВСЕМ"):
                st.session_state.poker_data.update({"answer": ans, "show_answer": True})
                st.rerun()

        # ТАБЛИЦА ОТВЕТОВ ИГРОКОВ (Видит только Админ)
        st.subheader("📩 Ответы игроков")
        ans_cols = st.columns(len(st.session_state.poker_data["players"]))
        for i, (name, p_ans) in enumerate(st.session_state.poker_data["player_answers"].items()):
            ans_cols[i].markdown(f"**{name}:**\n{p_ans if p_ans else '---'}")

    # ВИЗУАЛИЗАЦИЯ ВОПРОСА (Все)
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

    if st.session_state.poker_data["show_answer"]:
        st.success(f"### ✅ ПРАВИЛЬНЫЙ ОТВЕТ: {st.session_state.poker_data['answer']}")

    st.info(f"## 💰 В БАНКЕ: {st.session_state.poker_data['bank']}")
    
    # СЕТКА ИГРОКОВ
    players = st.session_state.poker_data["players"]
    cols = st.columns(min(len(players), 4)) 
    for i, (name, stack) in enumerate(players.items()):
        with cols[i % 4]:
            st.markdown(f"### {name}")
            st.metric("Фишки", stack)
            
            if is_admin:
                bet = st.number_input("Ставка", min_value=0, max_value=stack, key=f"bet_{name}")
                if st.button(f"В банк", key=f"btn_{name}"):
                    st.session_state.poker_data["players"][name] -= bet
                    st.session_state.poker_data["bank"] += bet
                    st.rerun()
            else:
                # ПОЛЕ ДЛЯ ОТВЕТА ИГРОКА (Видит игрок)
                p_ans = st.text_input("Ваш ответ", key=f"input_{name}")
                if st.button("Отправить", key=f"send_{name}"):
                    st.session_state.poker_data["player_answers"][name] = p_ans
                    st.toast("Ответ отправлен ведущему!")

    # РАЗДАЧА БАНКА (Админ)
    if is_admin:
        st.divider()
        winners = st.multiselect("Кто ответил верно?", list(players.keys()))
        if winners and st.button("РАЗДЕЛИТЬ БАНК 🎉"):
            split = st.session_state.poker_data['bank'] // len(winners)
            for w in winners: st.session_state.poker_data["players"][w] += split
            st.session_state.poker_data["bank"] = 0
            # Очистка полей для нового раунда
            st.session_state.poker_data.update({
                "question": "", "hint_1": "", "hint_2": "", "answer": "", 
                "show_answer": False, "player_answers": {n: "" for n in players}
            })
            st.rerun()
        
        if st.sidebar.button("🔄 Полный сброс"):
            st.session_state.clear()
            st.rerun()
