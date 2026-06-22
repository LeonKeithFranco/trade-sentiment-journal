import streamlit as st


def auth_check() -> None:
    if "access_token" not in st.session_state:
        st.stop()
