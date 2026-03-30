import streamlit as st

st.set_page_config(page_title="Интеллектуальная Игра", layout="wide")

# 1. ОБЩАЯ ПАМЯТЬ
@st.cache_resource
def get_common_data():
    return {
        "players": {}, "bank": 0, "game_started": False,
        "question": "", "hint_1": "", "hint_2": "", "answer": "", 
        "show_answer": False, "player_answers": {}
    }

common_data = get_common_data()

# 2. ИНИЦИАЛИЗАЦИЯ ЛИЧНОЙ ПАМЯТИ (Защита от ошибок AttributeError)
if "my_role" not in st.session_state:
    st.session_state.my_role = "---"

# --- БОКОВАЯ ПАНЕЛЬ ---
st.sidebar.header("⚙️ Вход")
admin_pwd = st.sidebar.text_input("Пароль Ведущего", type="password")
is_admin = (admin_pwd == "1234")

if common_data["game_started"] and not is_admin:
    st.session_state.my_role = st.sidebar.selectbox(
        "Выберите ваше имя:", 
        ["---"] + list(common_data["players"].keys()),
        index=0 if st.session_state.my_role not in common_data["players"] else list(common_data["players"].keys()).index(st.session_state.my_role) + 1
    )

st.title("🧠 Интеллектуальное Табло")

# Кнопка обновления для игроков (всегда видна, если игра идет)
if common_data["game_started"] and not is_admin:
    if st.button("🔄 ОБНОВИТЬ ТАБЛО"):
        st.rerun()

if not common_data["game_started"]:
    if is_admin:
        st.subheader("Настройка участников")
        num_players = st.slider("Количество игроков", 2, 10, 2)
        p_names = [st.text_input(f"Имя {i+1}", key=f"n_{i}") for i in range(num_players)]
        if st.button("🚀 НАЧАТЬ ИГРУ"):
            names_dict = {n: 1000 for n in p_names if n}
            common_data.update({
                "players": names_dict,
                "player_answers": {n: "" for n in names_dict},
                "game_started": True
            })
            st.rerun()
    else:
        st.info("Ждем Ведущего...")

else:
    # --- ПАНЕЛЬ ВЕДУЩЕГО ---
    if is_admin:
        with st.expander("📝 УПРАВЛЕНИЕ ТУРОМ", expanded=True):
            q = st.text_area("Текст вопроса", value=common_data["question"])
            h1 = st.text_input("Подсказка №1", value=common_data["hint_1"])
            h2 = st.text_input("Подсказка №2", value=common_data["hint_2"])
            ans = st.text_input("ПРАВИЛЬНЫЙ ОТВЕТ", value=common_data["answer"])
            
            c1, c2, c3 = st.columns(3)
            if c1.button("📢 НОВЫЙ ВОПРОС"):
                common_data.update({
                    "question": q, "hint_1": h1, "hint_2": h2, "answer": ans, 
                    "show_answer": False, 
                    "player_answers": {n: "" for n in common_data["players"]} # Очистка ответов
                })
                st.rerun()
            if c2.button("💡 ОБНОВИТЬ ПОДСКАЗКИ"):
                common_data.update({"question": q, "hint_1": h1, "hint_2": h2, "answer": ans})
                st.rerun()
            if c3.button("👁️ ПОКАЗАТЬ ОТВЕТ"):
                common_data.update({"answer": ans, "show_answer": True})
                st.rerun()

        st.subheader("📩 Ответы игроков")
        # Создаем контейнер с крупным текстом
        for name, p_ans in common_data["player_answers"].items():
            if p_ans:
                # Крупный текст для уже пришедших ответов
                st.markdown(f"""
                    <div style="background-color: #e1f5fe; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #0288d1;">
                        <span style="font-size: 22px; font-weight: bold; color: #01579b;">{name}:</span> 
                        <span style="font-size: 26px; color: #000;">{p_ans}</span>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Текст для тех, кто еще думает
                st.markdown(f"<span style='font-size: 20px; color: gray;'>{name}: ⏳ ждем...</span>", unsafe_allow_html=True)

    # --- ТАБЛО ---
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

    if common_data["show_answer"]:
        st.success(f"### ✅ ОТВЕТ: {common_data['answer']}")

    st.info(f"## 💰 В БАНКЕ: {common_data['bank']}")
    
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
            
            # Логика для конкретного игрока
            elif st.session_state.get("my_role") == name:
                # Проверяем, есть ли уже ответ в базе
                saved_ans = common_data["player_answers"].get(name, "")
                
                if saved_ans != "":
                    # ЗАМОРОЗКА: Если ответ есть, просто показываем его
                    st.success(f"**Ваш ответ:**\n\n{saved_ans}")
                else:
                    # Если ответа нет, показываем ввод
                    val = st.text_input("Ваш ответ", key=f"input_{name}")
                    if st.button("ОТПРАВИТЬ", key=f"send_{name}"):
                        if val.strip():
                            common_data["player_answers"][name] = val
                            st.rerun()

    # --- РАЗДАЧА БАНКА ---
    if is_admin:
        st.divider()
        winners = st.multiselect("Кто победил?", list(players.keys()))
        if winners and st.button("РАЗДЕЛИТЬ БАНК 🎉"):
            split = common_data['bank'] // len(winners)
            for w in winners: common_data["players"][w] += split
            common_data["bank"] = 0
            common_data.update({"question": "", "hint_1": "", "hint_2": "", "answer": "", "show_answer": False, "player_answers": {n: "" for n in players}})
            st.rerun()
        
        if st.sidebar.button("🔄 СБРОС ВСЕГО"):
            common_data.update({"players": {}, "bank": 0, "game_started": False, "player_answers": {}})
            st.rerun()
