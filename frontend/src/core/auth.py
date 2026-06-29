import streamlit as st


def auth_check() -> None:
    if st.session_state.get("access_token"):
        st.error("Please login first.")
        st.stop()
