import streamlit as st

st.set_page_config(page_title="Интеллектуальная Игра", layout="wide")

# 1. ОБЩАЯ ПАМЯТЬ
@st.cache_resource
def get_common_data():
    return {
        "players": {}, 
        "bank": 0, 
        "bets_in_round": {},  
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

if "my_role" not in st.session_state:
    st.session_state.my_role = "---"

# --- БОКОВАЯ ПАНЕЛЬ ---
st.sidebar.header("⚙️ Вход")
admin_pwd = st.sidebar.text_input("Пароль Ведущего", type="password")
is_admin = (admin_pwd == "1234")

if is_admin:
    st.sidebar.divider()
    if st.sidebar.button("🚨 ПОЛНЫЙ СБРОС ИГРЫ"):
        common_data.update({
            "players": {}, "bank": 0, "bets_in_round": {}, "game_started": False, 
            "player_answers": {}, "show_all_answers": False,
            "question": "", "hint_1": "", "hint_2": "", "answer": "", "show_answer": False
        })
        st.rerun()

if common_data["game_started"]:
    current_players = list(common_data["players"].keys())
    st.session_state.my_role = st.sidebar.selectbox(
        "Кто вы?", 
        ["---", "Зритель"] + current_players,
        index=0
    )

st.title("🧠 Интеллектуальное Табло")

# --- ЭКРАН ПОДГОТОВКИ ---
if not common_data["game_started"]:
    if is_admin:
        st.subheader("Настройка участников")
        num_players = st.slider("Количество игроков", 2, 10, 2)
        p_names = []
        for i in range(num_players):
            name = st.text_input(f"Имя {i+1}", key=f"setup_n_{i}").strip()
            if name: p_names.append(name)
        
        if st.button("🚀 НАЧАТЬ ИГРУ"):
            if len(p_names) < 2:
                st.error("Введите хотя бы 2 имени!")
            else:
                names_dict = {n: 1000 for n in p_names}
                common_data.update({
                    "players": names_dict,
                    "bets_in_round": {n: 0 for n in names_dict},
                    "player_answers": {n: "" for n in names_dict},
                    "game_started": True
                })
                st.rerun()
    else:
        st.info("Ждем, пока Ведущий настроит игру...")
        if st.button("🔄 Проверить готовность"): st.rerun()

# --- ИГРОВОЙ ПРОЦЕСС ---
else:
    # 1. ПАНЕЛЬ ВЕДУЩЕГО
    if is_admin:
        with st.expander("📝 УПРАВЛЕНИЕ ВОПРОСОМ", expanded=True):
            q = st.text_area("Вопрос", value=common_data["question"])
            h1 = st.text_input("Подсказка 1", value=common_data["hint_1"])
            h2 = st.text_input("Подсказка 2", value=common_data["hint_2"])
            ans = st.text_input("Правильный ответ", value=common_data["answer"])
            
            c1, c2, c3, c4 = st.columns(4)
            if c1.button("📢 НОВЫЙ ВОПРОС"):
                common_data.update({
                    "question": q, "hint_1": h1, "hint_2": h2, "answer": ans, 
                    "show_answer": False, "show_all_answers": False, 
                    "player_answers": {n: "" for n in common_data["players"]},
                    "bets_in_round": {n: 0 for n in common_data["players"]}
                })
                st.rerun()
            if c2.button("💡 ОБНОВИТЬ ИНФО"):
                common_data.update({"question": q, "hint_1": h1, "hint_2": h2, "answer": ans})
                st.rerun()
            if c3.button("👁️ ВСКРЫТЬ ОТВЕТЫ"): 
                common_data["show_all_answers"] = True
                st.rerun()
            if c4.button("✅ ПОКАЗАТЬ ОТВЕТ"):
                common_data["show_answer"] = True
                st.rerun()

    # 2. ЦЕНТРАЛЬНОЕ ТАБЛО (ВИДЯТ ВСЕ)
    st.markdown(f"""
    <div style="background-color:#262730; padding:20px; border-radius:10px; border: 1px solid #464b5d; margin-bottom:20px; color:white">
        <h2 style="text-align:center; color:#FF4B4B;">❓ ВОПРОС</h2>
        <p style="font-size:24px; text-align:center;">{common_data['question'] if common_data['question'] else 'Ожидание вопроса...'}</p>
        <hr>
        <div style="display: flex; justify-content: space-around;">
            <div><b>Подсказка 1:</b> {common_data['hint_1']}</div>
            <div><b>Подсказка 2:</b> {common_data['hint_2']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. ОТВЕТЫ ИГРОКОВ (ВИДИТ ВЕДУЩИЙ ВСЕГДА, ИГРОКИ - ПОСЛЕ ВСКРЫТИЯ)
    if is_admin or common_data["show_all_answers"]:
        st.subheader("📩 Поступившие ответы:")
        ans_cols = st.columns(4)
        for idx, (name, p_ans) in enumerate(common_data["player_answers"].items()):
            with ans_cols[idx % 4]:
                if p_ans:
                    st.success(f"**{name}**:\n\n {p_ans}")
                else:
                    st.warning(f"**{name}**:\n\n ⏳ Думает...")

    if common_data["show_answer"]:
        st.success(f"### ✅ ПРАВИЛЬНЫЙ ОТВЕТ: {common_data['answer']}")

    st.divider()
    st.info(f"## 💰 В БАНКЕ: {common_data['bank']}")
    
    # 4. СЕТКА ИГРОКОВ (СТАВКИ И ВВОД)
    players = common_data["players"]
    cols = st.columns(len(players))
    
    for i, (name, stack) in enumerate(players.items()):
        with cols[i]:
            cur_bet = common_data["bets_in_round"].get(name, 0)
            st.metric(name, f"{stack}", delta=f"Ставка: {cur_bet}" if cur_bet > 0 else None)
            
            # Если это вкладка данного игрока - даем поле ввода
            if st.session_state.my_role == name:
                if common_data["player_answers"].get(name) == "":
                    val = st.text_input("Ваш ответ", key=f"input_{name}")
                    if st.button("ОТПРАВИТЬ", key=f"send_{name}"):
                        common_data["player_answers"][name] = val
                        st.rerun()
                else:
                    st.write("✅ Ответ отправлен")

            # Если это админ - даем управление ставками
            if is_admin:
                bet = st.number_input("Ставка", key=f"bet_{name}", step=10, min_value=0)
                if st.button(f"В банк", key=f"btn_{name}"):
                    if stack >= bet:
                        common_data["players"][name] -= bet
                        common_data["bank"] += bet
                        common_data["bets_in_round"][name] += bet
                        st.rerun()
                    else:
                        st.error("Мало фишек!")

    # 5. РАЗДАЧА (ТОЛЬКО АДМИН)
    if is_admin and common_data["bank"] > 0:
        st.divider()
        winners = st.multiselect("Победители:", list(players.keys()))
        if winners and st.button("РАЗДЕЛИТЬ БАНК (ALL-IN LOGIC)"):
            # Логика Side Pot
            round_bets = common_data["bets_in_round"].copy()
            orig_bets = common_data["bets_in_round"].copy()
            
            sorted_winners = sorted(winners, key=lambda x: orig_bets.get(x, 0))
            
            for winner in sorted_winners:
                w_limit = orig_bets.get(winner, 0)
                if w_limit <= 0: continue
                
                pot_level = 0
                for p in round_bets:
                    take = min(round_bets[p], w_limit)
                    pot_level += take
                    round_bets[p] -= take
                
                # Кто из победителей претендует на этот кусок (те, у кого ставка >= текущей)
                eligible = [w for w in winners if orig_bets[w] >= w_limit]
                share = pot_level // len(eligible)
                for el in eligible:
                    common_data["players"][el] += share
            
            common_data["bank"] = 0
            common_data["bets_in_round"] = {n: 0 for n in players}
            st.rerun()

if not is_admin:
    st.button("🔄 Обновить экран")
