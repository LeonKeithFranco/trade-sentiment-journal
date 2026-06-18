import streamlit as st
from src.core.config import get_settings

st.title(get_settings().app.name)

st.divider()

st.header("Login")

with st.form(key="login_form"):
    st.text_input("Email", key="login_email")
    st.text_input("Password", key="login_password", type="password")

    st.form_submit_button("Login")

st.divider()

with st.form(key="register_form"):
    st.text_input("Email", key="register_email")
    st.text_input("Password", key="register_password", type="password")
    st.text_input("Confirm Password", key="register_confirm_password", type="password")

    st.form_submit_button("Login")
