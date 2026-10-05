import streamlit as st


def clear_session() -> None:
    st.session_state["access_token"] = None
    st.session_state["refresh_token"] = None
    if "trade_options" in st.session_state:
        del st.session_state["trade_options"]
