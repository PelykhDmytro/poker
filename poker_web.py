import streamlit as st

st.set_page_config(page_title="Интеллектуальная Игра", layout="wide")

# Глобальный объект памяти
@st.cache_resource
def get_common_data():
    return {
        "players": {}, "bank": 0, "game_started": False,
        "question": "", "hint_1": "", "hint_2": "", "answer": "", 
        "show_answer": False, "player_answers": {}
    }

common_data = get_common_data()

# --- БОКОВАЯ ПАНЕЛЬ ---
st.sidebar.header("⚙️ Вход")
password = st.sidebar.text_input("Пароль Ведущего", type="password")
is_admin = (password == "1234")

current_user = None
if common_data["game_started"] and not is_admin:
    current_user = st.sidebar.selectbox("Кто вы?", ["---"] + list(common_data["players"].keys()))

st.title("🧠 Интеллектуальное Табло")

if not common_data["game_started"]:
    if is_admin:
        st.subheader("Настройка участников")
        num_players = st.slider("Количество игроков", 2, 10, 2)
        start_chips = st.number_input("Стартовый стек", value=1000, step=100)
        player_names = [st.text_input(f"Имя {i+1}", key=f"n_{i}") for i in range(num_players)]
        if st.button("🚀 НАЧАТЬ ИГРУ"):
            names_dict = {n: start_chips for n in player_names if n}
            common_data.update({
                "players": names_dict,
                "player_answers": {n: "" for n in names_dict},
                "game_started": True
            })
            st.rerun()
    else:
        st.info("Ждем Ведущего...")
        if st.button("🔄 Проверить запуск"): st.rerun()

else:
    # ИНТЕРФЕЙС ВЕДУЩЕГО
    if is_admin:
        with st.expander("📝 УПРАВЛЕНИЕ ТУРОМ", expanded=True):
            q = st.text_area("Текст вопроса", value=common_data["question"])
            h1 = st.text_input("Подсказка №1", value=common_data["hint_1"])
            h2 = st.text_input("Подсказка №2", value=common_data["hint_2"])
            ans = st.text_input("ПРАВИЛЬНЫЙ ОТВЕТ", value=common_data["answer"])
            
            c1, c2, c3 = st.columns(3)
            if c1.button("📢 НОВЫЙ ВОПРОС"):
                common_data.update({"question": q, "hint_1": h1, "hint_2": h2, "answer": ans, "show_answer": False, "player_answers": {n: "" for n in common_data["players"]}})
                st.rerun()
            if c2.button("💡 ОБНОВИТЬ ПОДСКАЗКИ"):
                common_data.update({"question": q, "hint_1": h1, "hint_2": h2, "answer": ans})
                st.rerun()
            if c3.button("👁️ ПОКАЗАТЬ ОТВЕТ"):
                common_data.update({"answer": ans, "show_answer": True})
                st.rerun()

        st.subheader("📩 Ответы игроков")
        # Выводим ответы в виде списка
        for name, p_ans in common_data["player_answers"].items():
            st.write(f"**{name}:** {p_ans if p_ans else '⏳ ждем...'}")

    # ТАБЛО
    st.markdown(f"""
    <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border: 2px solid #0e1117; margin-bottom:20px; color:#0e1117">
        <h2 style="text-align:center;">❓ Вопрос</h2>
        <p style="font-size:24px; text-align:center;">{common_data['question'] if common_data['question'] else 'Ожидайте...'}</p>
        <div style="display: flex; justify-content: space-around;">
            <div><b>💡 Подсказка 1:</b> {common_data['hint_1']}</div>
            <div><b>💡 Подсказка 2:</b> {common_data['hint_2']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if common_data["show_answer"]:
        st.success(f"### ✅ ОТВЕТ: {common_data['answer']}")

    # ИГРОКИ
    players = common_data["players"]
    cols = st.columns(len(players))
    for i, (name, stack) in enumerate(players.items()):
        with cols[i]:
            st.metric(name, stack)
            if is_admin:
                bet = st.number_input("Ставка", key=f"b_{name}", step=10)
                if st.button("В банк", key=f"btn_{name}"):
                    common_data["players"][name] -= bet
                    common_data["bank"] += bet
                    st.rerun()
            elif current_user == name:
                # МЕХАНИЗМ ОТПРАВКИ
                user_input = st.text_input("Ваш ответ", key=f"in_{name}")
                if st.button("ОТПРАВИТЬ", key=f"send_{name}"):
                    common_data["player_answers"][name] = user_input
                    st.toast("Отправлено!")
                    st.rerun()

    st.info(f"💰 БАНК: {common_data['bank']}")

    if is_admin:
        st.divider()
        winners = st.multiselect("Победители", list(players.keys()))
        if winners and st.button("РАЗДЕЛИТЬ 🎉"):
            win = common_data['bank'] // len(winners)
            for w in winners: common_data["players"][w] += win
            common_data["bank"] = 0
            common_data.update({"question": "", "hint_1": "", "hint_2": "", "answer": "", "show_answer": False, "player_answers": {n: "" for n in players}})
            st.rerun()
        if st.sidebar.button("🔄 Сброс"):
            common_data.update({"players": {}, "bank": 0, "game_started": False, "question": "", "hint_1": "", "hint_2": "", "answer": "", "show_answer": False, "player_answers": {}})
            st.rerun()
    else:
        st.button("🔄 Обновить табло")
