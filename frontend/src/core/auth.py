import streamlit as st


def auth_check() -> None:
    if st.session_state["access_token"] is None:
        st.error("Please login first.")
        st.stop()
