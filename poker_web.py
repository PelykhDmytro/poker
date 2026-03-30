import streamlit as st

st.set_page_config(page_title="POKER QUIZ", layout="wide")

# --- ГЛОБАЛЬНЫЕ СТИЛИ (CSS) ---
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; }
    
    /* Игровой стол */
    .poker-table {
        background: radial-gradient(circle, #1a472a 0%, #071a0f 100%);
        border: 8px solid #3d2b1f;
        border-radius: 150px;
        padding: 50px;
        margin: 20px auto;
        width: 95%;
        box-shadow: inset 0 0 100px #000, 0 20px 40px rgba(0,0,0,0.8);
        text-align: center;
    }

    /* Карточка с вопросом */
    .table-card {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid #fbbf24;
        border-radius: 15px;
        padding: 25px;
        color: white;
        display: inline-block;
        min-width: 400px;
    }

    /* Место игрока */
    .player-box {
        background: #1a1a1a;
        border: 1px solid #444;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        margin-bottom: 10px;
    }
    
    /* Текст в инпутах - теперь точно белый на темном */
    input {
        color: white !important;
        background-color: #262730 !important;
    }
    
    .pot-text {
        font-family: 'Arial Black', sans-serif;
        color: #fbbf24;
        font-size: 24px;
        letter-spacing: 3px;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- ЛОГИКА ДАННЫХ ---
@st.cache_resource
def init_data():
    return {
        "players": {}, "bank": 0, "game_started": False,
        "question": "", "hint_1": "", "hint_2": "", "answer": "", 
        "show_answer": False, "player_answers": {}
    }

data = init_data()

# --- ПАНЕЛЬ ВХОДА (SIDEBAR) ---
with st.sidebar:
    st.title("⚙️ Настройки")
    pwd = st.text_input("Пароль ведущего", type="password")
    is_admin = (pwd == "1234")
    
    if data["game_started"] and not is_admin:
        if "my_role" not in st.session_state: st.session_state.my_role = "---"
        st.session_state.my_role = st.selectbox("Ваше имя за столом:", ["---"] + list(data["players"].keys()))

    if is_admin and st.button("🚨 СБРОСИТЬ ВСЁ"):
        data.update({"players": {}, "bank": 0, "game_started": False, "player_answers": {}})
        st.rerun()

# --- ОСНОВНОЙ КОНТЕНТ ---
if not data["game_started"]:
    st.title("🃏 QUIZ POKER ROOM")
    if is_admin:
        n = st.slider("Количество мест", 2, 8, 2)
        names = [st.text_input(f"Игрок {i+1}", key=f"s_{i}") for i in range(n)]
        if st.button("ОТКРЫТЬ СТОЛ"):
            valid = {n: 1000 for n in names if n}
            data.update({"players": valid, "player_answers": {n: "" for n in valid}, "game_started": True})
            st.rerun()
    else:
        st.info("Стол еще не открыт. Ожидайте крупье...")
else:
    # ИНТЕРФЕЙС ВЕДУЩЕГО (УПРАВЛЕНИЕ)
    if is_admin:
        with st.expander("🛠 УПРАВЛЕНИЕ ТУРОМ", expanded=False):
            q_val = st.text_area("Вопрос", value=data["question"])
            h1_val = st.text_input("Подсказка 1", value=data["hint_1"])
            h2_val = st.text_input("Подсказка 2", value=data["hint_2"])
            ans_val = st.text_input("Верный ответ", value=data["answer"])
            if st.button("ОБНОВИТЬ ВОПРОС НА СТОЛЕ"):
                data.update({"question": q_val, "hint_1": h1_val, "hint_2": h2_val, "answer": ans_val, "show_answer": False, "player_answers": {n: "" for n in data["players"]}})
                st.rerun()
            if st.button("ПОКАЗАТЬ ОТВЕТ ВСЕМ"):
                data.update({"show_answer": True})
                st.rerun()

    # ВИЗУАЛИЗАЦИЯ СТОЛА
    st.markdown(f"""
    <div class="poker-table">
        <div class="pot-text">POT</div>
        <div style="font-size: 48px; color: #fff; font-weight: bold; margin-bottom: 20px;">$ {data['bank']}</div>
        <div class="table-card">
            <div style="color: #fbbf24; font-weight: bold; margin-bottom: 10px;">QUESTION</div>
            <div style="font-size: 28px; font-weight: bold; line-height: 1.2;">{data['question'] if data['question'] else 'Waiting for host...'}</div>
            <div style="margin-top: 15px; color: #aaa; font-size: 14px;">
                HINT 1: {data['hint_1']} | HINT 2: {data['hint_2']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if data["show_answer"]:
        st.success(f"### ✅ ПРАВИЛЬНЫЙ ОТВЕТ: {data['answer']}")

    # ОТОБРАЖЕНИЕ ИГРОКОВ
    cols = st.columns(len(
