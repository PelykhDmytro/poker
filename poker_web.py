import streamlit as st

st.set_page_config(page_title="Покерный Крупье", layout="wide")

# Инициализация состояния
if 'poker_data' not in st.session_state:
    st.session_state.poker_data = {
        "players": {},
        "bank": 0,
        "game_started": False
    }

# --- ПРОВЕРКА ПАРОЛЯ В БОКОВОЙ ПАНЕЛИ ---
st.sidebar.header("🔑 Доступ")
password = st.sidebar.text_input("Введите пароль Крупье", type="password")
is_admin = (password == "1234") # Твой пароль здесь

if not is_admin:
    st.sidebar.warning("Режим просмотра. Кнопки управления скрыты.")

st.title("🎰 Игровое Табло")

# --- ЭКРАН НАСТРОЙКИ (только для админа) ---
if not st.session_state.poker_data["game_started"]:
    if is_admin:
        st.subheader("Настройка участников")
        num_players = st.slider("Количество игроков", 2, 10, 4)
        start_chips = st.number_input("Стартовый стек", value=1000, step=100)
        
        player_names = []
        name_cols = st.columns(2)
        for i in range(num_players):
            with name_cols[i % 2]:
                name = st.text_input(f"Имя игрока {i+1}", value=f"Игрок {i+1}", key=f"name_input_{i}")
                player_names.append(name)
        
        if st.button("🚀 НАЧАТЬ ИГРУ"):
            st.session_state.poker_data["players"] = {name: start_chips for name in player_names}
            st.session_state.poker_data["game_started"] = True
            st.rerun()
    else:
        st.info("Ждем, пока Крупье настроит игру...")

# --- ИГРОВОЙ ЭКРАН ---
else:
    st.info(f"## ОБЩИЙ БАНК: {st.session_state.poker_data['bank']}")

    players = st.session_state.poker_data["players"]
    cols = st.columns(min(len(players), 4)) 

    for i, (name, stack) in enumerate(players.items()):
        with cols[i % 4]:
            st.markdown(f"### {name}")
            st.metric("Фишки", stack)
            
            # Кнопки управления показываются ТОЛЬКО админу
            if is_admin:
                bet = st.number_input("Ставка", min_value=0, max_value=stack, key=f"bet_{name}", step=10)
                if st.button(f"В банк 📥", key=f"btn_{name}"):
                    if bet > 0:
                        st.session_state.poker_data["players"][name] -= bet
                        st.session_state.poker_data["bank"] += bet
                        st.rerun()

    if is_admin:
        st.divider()
        st.subheader("🏆 Завершение раздачи")
        win_col1, win_col2 = st.columns([2, 1])
        with win_col1:
            winner = st.selectbox("Кто выиграл?", list(players.keys()))
        with win_col2:
            if st.button("ОТДАТЬ ВЕСЬ БАНК"):
                st.session_state.poker_data["players"][winner] += st.session_state.poker_data["bank"]
                st.session_state.poker_data["bank"] = 0
                st.rerun()

        if st.sidebar.button("🔄 Сбросить и сменить имена"):
            st.session_state.poker_data["game_started"] = False
            st.rerun()
