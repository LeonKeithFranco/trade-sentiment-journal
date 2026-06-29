import streamlit as st
from src.core.auth import auth_check

st.title("Journal Entries")

st.divider()

auth_check()
