import streamlit as st

# Конфигурация страницы
st.set_page_config(page_title="QUIZ POKER", layout="wide", initial_sidebar_state="expanded")

# --- ДИЗАЙН (CSS) ---
st.markdown("""
<style>
    /* Главный фон */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Заголовки */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Карточка вопроса */
    .question-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #334155;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
        text-align: center;
        margin-bottom: 25px;
    }

    /* Карточки игроков */
    .player-card {
        background: #1e293b;
        padding: 15px;
        border-radius: 15px;
        border-top: 4px solid #3b82f6;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }

    /* Стили для ответов (крупно) */
    .answer-box {
        background: #0ea5e9;
        color: white;
        padding: 15px;
        border-radius: 10px;
        font-size: 28px !important;
        font-weight: bold;
        text-align: center;
        margin-top: 10px;
        box-shadow: inset 0 2px 4px 0 rgba(0,0,0,0.2);
    }

    /* Кнопки */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        transition: 0.3s;
    }
</style>
""", unsafe_allow_html=True)

# 1. ОБЩАЯ ПАМЯТЬ
@st.cache_resource
def get_common_data():
    return {
        "players": {}, "bank": 0, "game_started": False,
        "question": "", "hint_1": "", "hint_2": "", "answer": "", 
        "show_answer": False, "player_answers": {}
    }

common_data = get_common_data()

# 2. ЛИЧНАЯ ПАМЯТЬ
if "my_role" not in st.session_state:
    st.session_state.my_role = "---"

# --- БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.title("👤 Вход в игру")
    admin_pwd = st.text_input("Пароль Ведущего", type="password")
    is_admin = (admin_pwd == "1234")
    
    if common_data["game_started"] and not is_admin:
        st.session_state.my_role = st.selectbox(
            "Выберите ваше имя:", 
            ["---"] + list(common_data["players"].keys()),
            index=0 if st.session_state.my_role not in common_data["players"] else list(common_data["players"].keys()).index(st.session_state.my_role) + 1
        )
    
    st.divider()
    if is_admin:
        if st.button("🚨 СБРОСИТЬ ВСЮ ИГРУ"):
            common_data.update({"players": {}, "bank": 0, "game_started": False, "player_answers": {}})
            st.rerun()

# --- ГЛАВНЫЙ ЭКРАН ---
st.title("🧠 QUIZ POKER")

if not common_data["game_started"]:
    if is_admin:
        st.subheader("🏁 Подготовка к запуску")
        num = st.slider("Сколько человек?", 2, 8, 2)
        cols = st.columns(num)
        names = []
        for i in range(num):
            names.append(cols[i].text_input(f"Игрок {i+1}", key=f"setup_n_{i}"))
        
        if st.button("🚀 ПОЕХАЛИ!"):
            valid_names = {n: 1000 for n in names if n}
            common_data.update({
                "players": valid_names,
                "player_answers": {n: "" for n in valid_names},
                "game_started": True
            })
            st.rerun()
    else:
        st.info("🕒 Ведущий настраивает столы... Ожидайте.")
        st.button("🔄 Проверить запуск")

else:
    # ИНТЕРФЕЙС КРУПЬЕ
    if is_admin:
        with st.expander("🛠 ПАНЕЛЬ УПРАВЛЕНИЯ", expanded=True):
            q_text = st.text_area("Текст вопроса", value=common_data["question"])
            col_h1, col_h2 = st.columns(2)
            h1_text = col_h1.text_input("Подсказка 1", value=common_data["hint_1"])
            h2_text = col_h2.text_input("Подсказка 2", value=common_data["hint_2"])
            ans_text = st.text_input("Правильный ответ (скрыт)", value=common_data["answer"])
            
            b1, b2, b3 = st.columns(3)
            if b1.button("🆕 НОВЫЙ ТУР"):
                common_data.update({
                    "question": q_text, "hint_1": h1_text, "hint_2": h2_text, "answer": ans_text,
                    "show_answer": False, "player_answers": {n: "" for n in common_data["players"]}
                })
                st.rerun()
            if b2.button("💡 ДАТЬ ПОДСКАЗКУ"):
                common_data.update({"question": q_text, "hint_1": h1_text, "hint_2": h2_text, "answer": ans_text})
                st.rerun()
            if b3.button("✅ ОТКРЫТЬ ОТВЕТ"):
                common_data.update({"show_answer": True})
                st.rerun()

    # ТАБЛО (ВИДЯТ ВСЕ)
    st.markdown(f"""
    <div class="question-card">
        <h1 style='margin:0; color:#3b82f6;'>ВОПРОС</h1>
        <p style='font-size:32px; font-weight:500;'>{common_data['question'] if common_data['question'] else 'Ожидание...'}</p>
        <div style='display:flex; justify-content:center; gap:50px; border-top:1px solid #334155; padding-top:15px;'>
            <div><small style='color:#94a3b8'>ПОДСКАЗКА 1</small><br><b>{common_data['hint_1']}</b></div>
            <div><small style='color:#94a3b8'>ПОДСКАЗКА 2</small><br><b>{common_data['hint_2']}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if common_answer := common_data.get("show_answer"):
        if common_answer:
            st.success(f"### ✅ ПРАВИЛЬНЫЙ ОТВЕТ: {common_data['answer']}")

    # БАНК
    st.markdown(f"<h1 style='text-align:center; color:#fbbf24;'>💰 BANK: {common_data['bank']}</h1>", unsafe_allow_html=True)

    # ИГРОКИ
    players = common_data["players"]
    cols = st.columns(len(players))
    
    for i, (name, stack) in enumerate(players.items()):
        with cols[i]:
            # Карточка игрока
            st.markdown(f"""
            <div class="player-card">
                <h3 style='margin:0;'>{name}</h3>
                <h2 style='color:#10b981; margin:0;'>{stack}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            if is_admin:
                bet = st.number_input("Ставка", key=f"b_{name}", step=50, label_visibility="collapsed")
                if st.button("BET", key=f"btn_{name}"):
                    common_data["players"][name] -= bet
                    common_data["bank"] += bet
                    st.rerun()
            
            elif st.session_state.my_role == name:
                p_ans = common_data["player_answers"].get(name, "")
                if p_ans:
                    st.markdown(f"<div class='answer-box'>{p_ans}</div>", unsafe_allow_html=True)
                else:
                    val = st.text_input("Ваш ответ", key=f"in_{name}", label_visibility="collapsed")
                    if st.button("ОТПРАВИТЬ", key=f"snd_{name}"):
                        if val:
                            common_data["player_answers"][name] = val
                            st.rerun()

    # ОТВЕТЫ ДЛЯ ВЕДУЩЕГО (КРУПНО)
    if is_admin:
        st.divider()
        st.subheader("📢 МОНИТОР ОТВЕТОВ")
        for name, ans in common_data["player_answers"].items():
            if ans:
                st.markdown(f"""
                    <div style='background:#1e293b; padding:15px; border-radius:10px; margin-bottom:10px; border-left:10px solid #0ea5e9;'>
                        <span style='font-size:20px; color:#94a3b8;'>{name}:</span><br>
                        <span style='font-size:35px; font-weight:bold; color:white;'>{ans}</span>
                    </div>
                """, unsafe_allow_html=True)

        winners = st.multiselect("Кто забирает банк?", list(players.keys()))
        if winners and st.button("🎉 ВРУЧИТЬ ВЫИГРЫШ"):
            split = common_data['bank'] // len(winners)
            for w in winners: common_data["players"][w] += split
            common_data["bank"] = 0
            st.rerun()
    else:
        st.button("🔄 ОБНОВИТЬ ДАННЫЕ")
