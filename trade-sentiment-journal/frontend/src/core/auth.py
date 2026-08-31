import streamlit as st


def auth_check() -> None:
    """Guard a page against unauthenticated access.

    Halts execution of the current Streamlit page and shows an error
    message if no access token is present in session state.
    """
    if st.session_state["access_token"] is None:
        st.error("Please login first.")
        st.stop()
