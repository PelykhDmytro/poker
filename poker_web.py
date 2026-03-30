import streamlit as st

st.set_page_config(page_title="Интеллектуальная Игра", layout="wide")

# --- ГЛОБАЛЬНАЯ ПАМЯТЬ ДЛЯ ВСЕХ ИГРОКОВ ---
@st.cache_resource
def get_common_data():
    return {
        "players": {}, "bank": 0, "game_started": False,
        "question": "", "hint_1": "", "hint_2": "", "answer": "", 
        "show_answer": False, "player_answers": {}
    }

# Подключаемся к общей памяти
common_data = get_common_data()

st.sidebar.header("🔑 Панель Ведущего")
password = st.sidebar.text_input("Введите пароль", type="password")
is_admin = (password == "1234")

st.title("🧠 Интеллектуальное Табло")

# --- НАСТРОЙКА ИГРЫ ---
if not common_data["game_started"]:
    if is_admin:
        st.subheader("Настройка участников")
        num_players = st.slider("Количество игроков", 2, 10, 2)
        start_chips = st.number_input("Стартовый стек", value=1000, step=100)
        player_names = [st.text_input(f"Имя {i+1}", value=f"Игрок {i+1}", key=f"n_{i}") for i in range(num_players)]
        if st.button("🚀 НАЧАТЬ ИГРУ"):
            common_data.update({
                "players": {n: start_chips for n in player_names},
                "player_answers": {n: "" for n in player_names},
                "game_started": True
            })
            st.rerun()
    else:
        st.info("Ждем Ведущего...")
        if st.button("🔄 Проверить запуск"): # Кнопка для ручного обновления у игроков
            st.rerun()

# --- ИГРОВОЙ ПРОЦЕСС ---
else:
    if is_admin:
        with st.expander("📝 УПРАВЛЕНИЕ ТУРОМ", expanded=True):
            q = st.text_area("Текст вопроса", value=common_data["question"], key="q_in")
            h1 = st.text_input("Подсказка №1", value=common_data["hint_1"], key="h1_in")
            h2 = st.text_input("Подсказка №2", value=common_data["hint_2"], key="h2_in")
            ans = st.text_input("ПРАВИЛЬНЫЙ ОТВЕТ", value=common_data["answer"], key="ans_in")
            
            c1, c2 = st.columns(2)
            if c1.button("📢 ОБНОВИТЬ ВОПРОС"):
                common_data.update({
                    "question": q, "hint_1": h1, "hint_2": h2, "answer": ans, 
                    "show_answer": False, "player_answers": {n: "" for n in common_data["players"]}
                })
                st.rerun()
            if c2.button("👁️ ПОКАЗАТЬ ОТВЕТ ВСЕМ"):
                common_data.update({"answer": ans, "show_answer": True})
                st.rerun()

        st.subheader("📩 Ответы игроков")
        ans_cols = st.columns(len(common_data["players"]))
        for i, (name, p_ans) in enumerate(common_data["player_answers"].items()):
            ans_cols[i].markdown(f"**{name}:**\n{p_ans if p_ans else '---'}")

    # ВИЗУАЛИЗАЦИЯ ВОПРОСА
    st.markdown(f"""
    <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border: 2px solid #0e1117; margin-bottom:20px; color:#0e1117">
        <h2 style="text-align:center;">❓ Вопрос</h2>
        <p style="font-size:24px; text-align:center;">{common_data['question'] if common_data['question'] else 'Ожидайте вопрос...'}</p>
        <div style="display: flex; justify-content: space-around; margin-top:10px;">
            <div style="text-align:center;"><b>💡 Подсказка 1:</b><br>{common_data['hint_1']}</div>
            <div style="text-align:center;"><b>💡 Подсказка 2:</b><br>{common_data['hint_2']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if common_data["show_answer"]:
        st.success(f"### ✅ ПРАВИЛЬНЫЙ ОТВЕТ: {common_data['answer']}")

    st.info(f"## 💰 В БАНКЕ: {common_data['bank']}")
    
    players = common_data["players"]
    cols = st.columns(min(len(players), 4)) 
    for i, (name, stack) in enumerate(players.items()):
        with cols[i % 4]:
            st.markdown(f"### {name}")
            st.metric("Фишки", stack)
            if is_admin:
                bet = st.number_input("Ставка", min_value=0, max_value=stack, key=f"bet_{name}")
                if st.button(f"В банк", key=f"btn_{name}"):
                    common_data["players"][name] -= bet
                    common_data["bank"] += bet
                    st.rerun()
            else:
                p_ans = st.text_input("Ваш ответ", key=f"input_{name}")
                if st.button("Отправить", key=f"send_{name}"):
                    common_data["player_answers"][name] = p_ans
                    st.toast("Ответ отправлен!")

    if is_admin:
        st.divider()
        winners = st.multiselect("Кто ответил верно?", list(players.keys()))
        if winners and st.button("РАЗДЕЛИТЬ БАНК 🎉"):
            split = common_data['bank'] // len(winners)
            for w in winners: common_data["players"][w] += split
            common_data["bank"] = 0
            common_data.update({"question": "", "hint_1": "", "hint_2": "", "answer": "", "show_answer": False, "player_answers": {n: "" for n in players}})
            st.rerun()
        
        if st.sidebar.button("🔄 Полный сброс"):
            common_data.update({"players": {}, "bank": 0, "game_started": False, "question": "", "hint_1": "", "hint_2": "", "answer": "", "show_answer": False, "player_answers": {}})
            st.rerun()
    else:
        if st.button("🔄 Обновить данные"):
            st.rerun()
