import streamlit as st

st.set_page_config(page_title="Интеллектуальная Игра", layout="wide")

@st.cache_resource
def get_common_data():
    return {
        "players": {}, "bank": 0, "game_started": False,
        "question": "", "hint_1": "", "hint_2": "", "answer": "", 
        "show_answer": False, "player_answers": {}
    }

common_data = get_common_data()

# --- БОКОВАЯ ПАНЕЛЬ ---
st.sidebar.header("⚙️ Вход в игру")
password = st.sidebar.text_input("Пароль Ведущего", type="password")
is_admin = (password == "1234")

# Выбор роли для игрока
current_user = None
if common_data["game_started"] and not is_admin:
    current_user = st.sidebar.selectbox("Выберите ваше имя", ["---"] + list(common_data["players"].keys()))

st.title("🧠 Интеллектуальное Табло")

if not common_data["game_started"]:
    if is_admin:
        st.subheader("Настройка участников")
        num_players = st.slider("Количество игроков", 2, 10, 2)
        start_chips = st.number_input("Стартовый стек", value=1000, step=100)
        player_names = [st.text_input(f"Имя {i+1}", value=f"Игрок {i+1}", key=f"n_{i}") for i in range(num_players)]
        if st.button("🚀 НАЧАТЬ ИГРУ"):
            common_data.update({
                "players": {n: start_chips for n in player_names if n},
                "player_answers": {n: "" for n in player_names if n},
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
            q = st.text_area("Текст вопроса", value=common_data["question"], key="q_in")
            h1 = st.text_input("Подсказка №1", value=common_data["hint_1"], key="h1_in")
            h2 = st.text_input("Подсказка №2", value=common_data["hint_2"], key="h2_in")
            ans = st.text_input("ПРАВИЛЬНЫЙ ОТВЕТ", value=common_data["answer"], key="ans_in")
            
            col1, col2, col3 = st.columns(3)
            
            if col1.button("📢 НОВЫЙ ВОПРОС (ОЧИСТИТЬ ВСЁ)"):
                common_data.update({
                    "question": q, "hint_1": h1, "hint_2": h2, "answer": ans, 
                    "show_answer": False, "player_answers": {n: "" for n in common_data["players"]}
                })
                st.rerun()

            if col2.button("💡 ОБНОВИТЬ ПОДСКАЗКИ (СОХРАНИТЬ ОТВЕТЫ)"):
                common_data.update({
                    "question": q, "hint_1": h1, "hint_2": h2, "answer": ans
                })
                st.success("Подсказки добавлены, ответы игроков сохранены!")
                st.rerun()
                
            if col3.button("👁️ ПОКАЗАТЬ ОТВЕТ ВСЕМ"):
                common_data.update({"answer": ans, "show_answer": True})
                st.rerun()

    # ТАБЛО (ВИДЯТ ВСЕ)
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
    
    # ОТОБРАЖЕНИЕ ИГРОКОВ
    players = common_data["players"]
    cols = st.columns(min(len(players), 4)) 
    for i, (name, stack) in enumerate(players.items()):
        with cols[i % 4]:
            st.markdown(f"### {name}")
            st.metric("Фишки", stack)
            
            # Если это ведущий - он видит кнопки ставок
            if is_admin:
                bet = st.number_input("Ставка", min_value=0, max_value=stack, key=f"bet_{name}")
                if st.button(f"В банк", key=f"btn_{name}"):
                    common_data["players"][name] -= bet
                    common_data["bank"] += bet
                    st.rerun()
            
            # Если это игрок И ОН ВЫБРАЛ СВОЁ ИМЯ - он видит поле для ответа
            elif current_user == name:
                p_ans = st.text_input("Ваш ответ", key=f"input_{name}")
                if st.button("Отправить", key=f"send_{name}"):
                    common_data["player_answers"][name] = p_ans
                    st.toast("Ответ отправлен!")

    # КНОПКИ ОБНОВЛЕНИЯ И СБРОСА
    st.divider()
    if is_admin:
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
        st.button("🔄 Обновить данные")
