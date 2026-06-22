import streamlit as st
from src.core.auth import auth_check

st.title("Trades")

st.divider()

auth_check()

with st.form("trade_form"):
    ticker = st.text_input("Ticker", placeholder="e.g. AABL")
    direction = st.selectbox("Direction", options=["Long", "Short"])
    position_size = st.number_input(
        "Position Size", min_value=0.0, step=1.0, format="%.4f"
    )
    entry_price = st.number_input("Entry Price", min_value=0.0, step=0.1)
    opened_at = st.date_input("Opened At")

    if st.form_submit_button():
        pass
