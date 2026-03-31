import streamlit as st

st.set_page_config(page_title="Интеллектуальная Игра", layout="wide")

# 1. ОБЩАЯ ПАМЯТЬ (Хранится на сервере для всех пользователей)
@st.cache_resource
def get_common_data():
    return {
        "players": {}, 
        "bank": 0, 
        "game_started": False,
        "question": "", 
        "hint_1": "", 
        "hint_2": "", 
        "answer": "", 
        "show_answer": False, 
        "show_all_answers": False, 
        "player_answers": {}
    }

common_data = get_common_data()

# 2. ИНИЦИАЛИЗАЦИЯ ЛИЧНОЙ ПАМЯТИ (Для каждого вкладки браузера)
if "my_role" not in st.session_state:
    st.session_state.my_role = "---"

# --- БОКОВАЯ ПАНЕЛЬ ---
st.sidebar.header("⚙️ Вход")
admin_pwd = st.sidebar.text_input("Пароль Ведущего", type="password")
is_admin = (admin_pwd == "1234")

# Кнопка аварийного сброса (Всегда доступна ведущему)
if is_admin:
    st.sidebar.divider()
    if st.sidebar.button("🚨 ПОЛНЫЙ СБРОС ИГРЫ", help="Сбросить всех игроков и очистить банк"):
        common_data.update({
            "players": {}, "bank": 0, "game_started": False, 
            "player_answers": {}, "show_all_answers": False,
            "question": "", "hint_1": "", "hint_2": "", "answer": "", "show_answer": False
        })
        st.rerun()

# Выбор имени для игрока
if common_data["game_started"] and not is_admin:
    st.session_state.my_role = st.sidebar.selectbox(
        "Выберите ваше имя:", 
        ["---"] + list(common_data["players"].keys()),
        index=0 if st.session_state.my_role not in common_data["players"] else list(common_data["players"].keys()).index(st.session_state.my_role) + 1
    )

st.title("🧠 Интеллектуальное Табло")

# --- КНОПКА ОБНОВЛЕНИЯ (Видна игрокам всегда) ---
if not is_admin:
    if st.button("🔄 ОБНОВИТЬ ТАБЛО"):
        st.rerun()

# --- ЭКРАН ПОДГОТОВКИ ---
if not common_data["game_started"]:
    if is_admin:
        st.subheader("Настройка участников")
        num_players = st.slider("Количество игроков", 2, 10, 2)
        
        # Сбор имен с фильтрацией пустых полей
        p_names = []
        for i in range(num_players):
            name = st.text_input(f"Имя {i+1}", key=f"n_{i}").strip()
            if name:
                p_names.append(name)
        
        if st.button("🚀 НАЧАТЬ ИГРУ"):
            if len(p_names) < 2:
                st.error("Введите хотя бы 2 имени участников!")
            else:
                names_dict = {n: 1000 for n in p_names}
                common_data.update({
                    "players": names_dict,
                    "player_answers": {n: "" for n in names_dict},
                    "game_started": True
                })
                st.rerun()
    else:
        st.info("Ждем, пока Ведущий настроит игру...")

# --- ИГРОВОЙ ПРОЦЕСС ---
else:
    # ПАНЕЛЬ УПРАВЛЕНИЯ ВЕДУЩЕГО
    if is_admin:
        with st.expander("📝 УПРАВЛЕНИЕ ТУРОМ", expanded=True):
            q = st.text_area("Текст вопроса", value=common_data["question"])
            h1 = st.text_input("Подсказка №1", value=common_data["hint_1"])
            h2 = st.text_input("Подсказка №2", value=common_data["hint_2"])
            ans = st.text_input("ПРАВИЛЬНЫЙ ОТВЕТ", value=common_data["answer"])
            
            c1, c2, c3, c4 = st.columns(4)
            if c1.button("📢 НОВЫЙ ВОПРОС"):
                common_data.update({
                    "question": q, "hint_1": h1, "hint_2": h2, "answer": ans, 
                    "show_answer": False, "show_all_answers": False, 
                    "player_answers": {n: "" for n in common_data["players"]}
                })
                st.rerun()
            if c2.button("💡 ПОДСКАЗКИ"):
                common_data.update({"question": q, "hint_1": h1, "hint_2": h2, "answer": ans})
                st.rerun()
            if c3.button("👁️ ВСКРЫТЬ ОТВЕТЫ"): 
                common_data["show_all_answers"] = True
                st.rerun()
            if c4.button("✅ ОТВЕТ"):
                common_data.update({"answer": ans, "show_answer": True})
                st.rerun()

        st.subheader("📩 Ответы игроков (для Ведущего)")
        for name, p_ans in common_data["player_answers"].items():
            if p_ans:
                st.write(f"**{name}:** {p_ans}")
            else:
                st.write(f"*{name}: ⏳ думает...*")

    # --- ЦЕНТРАЛЬНОЕ ТАБЛО ---
    st.markdown(f"""
    <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border: 2px solid #0e1117; margin-bottom:20px; color:#0e1117">
        <h2 style="text-align:center;">❓ Вопрос</h2>
        <p style="font-size:24px; text-align:center;">{common_data['question'] if common_data['question'] else 'Ожидайте вопрос...'}</p>
        <div style="display: flex; justify-content: space-around;">
            <div><b>💡 Подсказка 1:</b> {common_data['hint_1']}</div>
            <div><b>💡 Подсказка 2:</b> {common_data['hint_2']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Отображение всех ответов для всех (когда ведущий вскрыл их)
    if common_data["show_all_answers"]:
        st.subheader("📢 Ответы всех участников:")
        ans_cols = st.columns(min(len(common_data["players"]), 3))
        for idx, (name, p_ans) in enumerate(common_data["player_answers"].items()):
            with ans_cols[idx % len(ans_cols)]:
                st.info(f"**{name}**: {p_ans if p_ans else '---'}")

    if common_data["show_answer"]:
        st.success(f"### ✅ ПРАВИЛЬНЫЙ ОТВЕТ: {common_data['answer']}")

    st.info(f"## 💰 В БАНКЕ: {common_data['bank']}")
    
    # --- СЕТКА ИГРОКОВ ---
    players = common_data["players"]
    
    if not players:
        st.warning("⚠️ Список игроков пуст. Ведущий, нажми '🚨 ПОЛНЫЙ СБРОС ИГРЫ' слева.")
    else:
        cols = st.columns(len(players))
        for i, (name, stack) in enumerate(players.items()):
            with cols[i]:
                st.metric(name, stack)
                
                # Интерфейс Ведущего (Ставки)
                if is_admin:
                    bet = st.number_input("Ставка", key=f"bet_{name}", step=10)
                    if st.button(f"В банк", key=f"btn_{name}"):
                        common_data["players"][name] -= bet
                        common_data["bank"] += bet
                        st.rerun()
                
                # Интерфейс Игрока (Ввод ответа)
                elif st.session_state.get("my_role") == name:
                    saved_ans = common_data["player_answers"].get(name, "")
                    if saved_ans != "":
                        st.success(f"**Ваш ответ:**\n\n{saved_ans}")
                    else:
                        val = st.text_input("Ваш ответ", key=f"input_{name}")
                        if st.button("ОТПРАВИТЬ", key=f"send_{name}"):
                            if val.strip():
                                common_data["player_answers"][name] = val
                                st.rerun()

    # --- РАЗДАЧА БАНКА ---
    if is_admin and players:
        st.divider()
        winners = st.multiselect("Кто победил?", list(players.keys()))
        if winners and st.button("РАЗДЕЛИТЬ БАНК 🎉"):
            split = common_data['bank'] // len(winners)
            for w in winners: common_data["players"][w] += split
            common_data["bank"] = 0
            # Сброс раунда при делении банка
            common_data.update({
                "show_answer": False, "show_all_answers": False,
                "player_answers": {n: "" for n in players},
                "question": "", "hint_1": "", "hint_2": "", "answer": ""
            })
            st.rerun()
