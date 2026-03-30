import streamlit as st

# Настройка интерфейса
st.set_page_config(page_title="Покерный Крупье", layout="wide")

# Инициализация данных (в памяти сервера на время сессии)
if 'poker_data' not in st.session_state:
    st.session_state.poker_data = {
        "Игрок 1": 1000, "Игрок 2": 1000, 
        "Игрок 3": 1000, "Игрок 4": 1000,
        "bank": 0
    }

st.title("🎰 Панель управления фишками")

# Отображение Банка
st.info(f"## ОБЩИЙ БАНК: {st.session_state.poker_data['bank']}")

# Колонки для игроков
cols = st.columns(4)
player_names = list(st.session_state.poker_data.keys())[:4]

for i, name in enumerate(player_names):
    with cols[i]:
        st.subheader(name)
        st.metric("Стек", st.session_state.poker_data[name])
        
        # Поле ввода ставки
        bet = st.number_input("Ставка", min_value=0, step=10, key=f"bet_{name}")
        
        if st.button(f"В банк 📥", key=f"btn_{name}"):
            if st.session_state.poker_data[name] >= bet:
                st.session_state.poker_data[name] -= bet
                st.session_state.poker_data["bank"] += bet
                st.rerun()

st.divider()

# Раздача выигрыша
st.subheader("🏆 Завершение раздачи")
winner = st.selectbox("Кто забирает банк?", player_names)

if st.button("ОТДАТЬ БАНК ПОБЕДИТЕЛЮ 🎉"):
    st.session_state.poker_data[winner] += st.session_state.poker_data["bank"]
    st.session_state.poker_data["bank"] = 0
    st.success(f"Банк передан {winner}!")
    st.rerun()

if st.button("Сбросить всё"):
    st.session_state.poker_data = {"Игрок 1": 1000, "Игрок 2": 1000, "Игрок 3": 1000, "Игрок 4": 1000, "bank": 0}
    st.rerun()