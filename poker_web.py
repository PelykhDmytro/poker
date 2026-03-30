import streamlit as st

st.set_page_config(page_title="Покерный Крупье", layout="wide")

# Инициализация базы данных игроков
if 'poker_data' not in st.session_state:
    st.session_state.poker_data = {
        "players": {"Игрок 1": 1000, "Игрок 2": 1000},
        "bank": 0,
        "game_started": False
    }

st.title("🎰 Универсальная панель Крупье")

# --- ЭКРАН НАСТРОЙКИ (показывается только в начале) ---
if not st.session_state.poker_data["game_started"]:
    st.subheader("Настройка игры")
    num_players = st.slider("Сколько игроков за столом?", 2, 10, 4)
    start_chips = st.number_input("Стартовый стек", value=1000, step=100)
    
    if st.button("🚀 НАЧАТЬ ИГРУ"):
        # Создаем список игроков динамически
        new_players = {f"Игрок {i+1}": start_chips for i in range(num_players)}
        st.session_state.poker_data["players"] = new_players
        st.session_state.poker_data["game_started"] = True
        st.rerun()

# --- ИГРОВОЙ ЭКРАН ---
else:
    st.info(f"## ОБЩИЙ БАНК: {st.session_state.poker_data['bank']}")

    # Автоматическое создание колонок под любое количество игроков
    players = st.session_state.poker_data["players"]
    cols = st.columns(len(players))

    for i, (name, stack) in enumerate(players.items()):
        with cols[i]:
            st.markdown(f"### {name}")
            st.metric("Фишки", stack)
            
            # Поле ставки для конкретного игрока
            bet = st.number_input("Ставка", min_value=0, max_value=stack, key=f"bet_{name}", step=10)
            
            if st.button(f"В банк 📥", key=f"btn_{name}"):
                if bet > 0:
                    st.session_state.poker_data["players"][name] -= bet
                    st.session_state.poker_data["bank"] += bet
                    st.rerun()

    st.divider()

    # Раздача выигрыша
    col_win1, col_win2 = st.columns([2, 1])
    with col_win1:
        winner = st.selectbox("Кто выиграл раздачу?", list(players.keys()))
    with col_win2:
        if st.button("🏆 ОТДАТЬ ВЕСЬ БАНК"):
            st.session_state.poker_data["players"][winner] += st.session_state.poker_data["bank"]
            st.session_state.poker_data["bank"] = 0
            st.success(f"Банк передан {winner}!")
            st.rerun()

    # Кнопка сброса
    if st.sidebar.button("⚙️ Сбросить и настроить заново"):
        st.session_state.poker_data["game_started"] = False
        st.rerun()
