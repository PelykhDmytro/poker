import streamlit as st

st.set_page_config(page_title="Интеллектуальная Игра", layout="wide")

# 1. Глобальная память (общая для всех)
@st.cache_resource
def get_common_data():
    return {
        "players": {}, "bank": 0, "game_started": False,
        "question": "", "hint_1": "", "hint_2": "", "answer": "", 
        "show_answer": False, "player_answers": {}
    }

common_data = get_common_data()

# 2. Личная память браузера (чтобы не пропадало окно ввода)
if "my_name" not in st.session_state:
    st.session_state.my_name = "---"

# --- БОКОВАЯ ПАНЕЛЬ ---
st.sidebar.header("⚙️ Вход")
password = st.sidebar.text_input("Пароль Ведущего", type="password")
is_admin = (password == "1234")

# Если игра запущена и это не админ, даем выбрать имя ОДИН РАЗ
if common_data["game_started"] and not is_admin:
    st.session_state.my_name = st.sidebar.selectbox(
        "Кто вы?", 
        ["---"] + list(common_data["players"].keys()),
        index=0 if st.session_state.my_name == "---" else list(common_data["players"].keys()).index(st.session_state.my_name) + 1
    )

st.title("🧠 Интеллектуальное Табло")

if not common_data["game_started"]:
    if is_admin:
        st.subheader("Настройка участников")
        num_players = st.slider("Количество игроков", 2, 10, 2)
        player_names = [st.text_input(f"Имя {i+1}", key=f"n_{i}") for i in range(num_players)]
        if st.button("🚀 НАЧАТЬ ИГРУ"):
            names_dict = {n: 1000 for n in player_names if n}
            common_data.update({
                "players": names_dict,
                "player_answers": {n: "" for n in names_dict},
                "game_started": True
            })
            st.rerun()
    else:
        st.info("Ждем Ведущего...")
        st.button("🔄 Проверить запуск")

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
        for name, p_ans in common_data["player_answers"].items():
            st.write(f"**{name}:** {p_ans if p_ans else '⏳ ждем...'}")

    # ТАБЛО (ВИДЯТ ВСЕ)
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

    # --- СЕТКА ИГРОКОВ ---
    players = common_data["players"]
    cols = st.columns(len(players))
    for i, (name, stack) in enumerate(players.items()):
        with cols[i]:
            st.metric(name, stack)
            
            if is_admin:
                bet = st.number_input("Ставка", key=f"bet_{name}", step=10)
                if st.button(f"В банк", key=f"btn_{name}"):
                    common_data["players"][name] -= bet
                    common_data["bank"] += bet
                    st.rerun()
            
            # ЛОГИКА ДЛЯ ИГРОКА:
            elif st.session_state.my_role == name:
                current_answer = common_data["player_answers"].get(name, "")
                
                if current_answer != "":
                    # Если ответ уже есть — просто показываем его без возможности правки
                    st.success(f"**Ваш ответ принят:**\n\n{current_answer}")
                    st.caption("Ожидайте следующий вопрос")
                else:
                    # Если ответа еще нет — показываем поле ввода
                    ans_val = st.text_input("Ваш ответ", key=f"input_{name}")
                    if st.button("ОТПРАВИТЬ", key=f"send_{name}"):
                        if ans_val.strip() != "":
                            common_data["player_answers"][name] = ans_val
                            st.toast("Ответ зафиксирован!")
                            st.rerun()
                        else:
                            st.warning("Введите хоть что-нибудь")
            
            # Сверяем имя из ЛИЧНОЙ памяти браузера
            elif st.session_state.my_name == name:
                user_input = st.text_input("Ваш ответ", key=f"input_field_{name}")
                if st.button("ОТПРАВИТЬ", key=f"send_btn_{name}"):
                    common_data["player_answers"][name] = user_input
                    st.toast("Отправлено!")
                    st.rerun()

    st.info(f"💰 БАНК: {common_data['bank']}")
    if not is_admin:
        st.button("🔄 Обновить табло", key="refresh_user")

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
