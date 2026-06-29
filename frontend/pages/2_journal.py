import streamlit as st
from src.core.auth import auth_check

st.title("Trades")

st.divider()

auth_check()
