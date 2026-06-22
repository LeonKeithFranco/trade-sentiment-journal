from http import HTTPStatus

import streamlit as st
from src.core.api import APIClient, convert_pydantic_error_to_human_readable_message
from src.core.config import get_settings


def _blank_fields_message(**kwargs) -> str | None:
    blank_fields: list[str] = []

    for field, val in kwargs.items():
        if val == "":
            blank_fields.append(field.replace("_", " ").title())

    if len(blank_fields) == 0:
        return None

    return ", ".join(f"{field}" for field in blank_fields)


def _handle_logout() -> None:
    del st.session_state["access_token"]


@st.fragment
def login_form_section() -> None:
    st.divider()

    st.header("Login")

    with st.form(key="login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", key="login_password", type="password")

        if st.form_submit_button("Login"):
            blank_fields = _blank_fields_message(email=email, password=password)

            if blank_fields:
                st.error(f"The following fields were left blank: {blank_fields}")
                st.stop()

            with APIClient() as client:
                response = client.post_login(email=email, password=password)

                if response.status_code == HTTPStatus.OK:
                    st.session_state["access_token"] = response.json()["access_token"]

                    st.rerun()
                else:
                    st.error("Please try again.")


@st.fragment
def register_form_section() -> None:
    st.divider()

    st.header("Register")

    with st.form(key="register_form"):
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", key="register_password", type="password")
        confirm_password = st.text_input(
            "Confirm Password", key="register_confirm_password", type="password"
        )

        if st.form_submit_button("Register"):
            blank_fields = _blank_fields_message(
                email=email, password=password, confirm_password=confirm_password
            )

            if blank_fields:
                st.error(f"The following fields were left blank: {blank_fields}")
                st.stop()

            if confirm_password != password:
                st.error("The passwords you entered don't match.")
                st.stop()

            with APIClient() as client:
                response = client.post_register(email=email, password=password)

                if response.status_code == HTTPStatus.CREATED:
                    st.success("Registration was successful.")
                    st.stop()

                match response.status_code:
                    case HTTPStatus.UNPROCESSABLE_ENTITY:
                        err_detail = response.json()["detail"][0]

                        st.error(
                            convert_pydantic_error_to_human_readable_message(
                                err_detail,
                                "Unable to complete registration. Please try again at a later time.",
                            )
                        )
                    case HTTPStatus.CONFLICT:
                        st.error("User already exists.")
                    case _:
                        st.error("Unable to register. Please try again.")
                        print(response.json())


st.title(get_settings().app.name)

if "access_token" in st.session_state:
    st.button("Logout", on_click=_handle_logout)

else:
    login_form_section()
    register_form_section()
