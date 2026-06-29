from datetime import datetime
from http import HTTPStatus
from typing import Any

import streamlit as st
from src.core.api import (
    convert_pydantic_error_to_human_readable_message,
    get_all_trades,
    make_api_request,
)
from src.core.auth import auth_check

st.title("Journal Entries")

st.divider()

auth_check()


@st.fragment
def journal_form_and_table(trade_options: dict[str, Any]) -> None:
    with st.form("entry_form"):
        st.subheader("Create Journal Entry")

        trade_option = st.selectbox("Trades", options=trade_options)
        title = st.text_input("Title (Optional)", value=None)
        entry = st.text_area("Entry")

        if st.form_submit_button():
            response = make_api_request(
                "POST",
                "/journal-entries",
                json={
                    "title": title if title else None,
                    "entry": entry,
                    "trade_public_id": trade_options[trade_option],
                },
            )

            match response.status_code:
                case HTTPStatus.CREATED:
                    st.success("Journal entry created.")
                case HTTPStatus.UNPROCESSABLE_ENTITY:
                    err_detail = response.json()["detail"][0]

                    st.error(
                        convert_pydantic_error_to_human_readable_message(
                            err_detail, "Unable to create Journal entry."
                        )
                    )
                case _:
                    st.error(response.json())


with st.spinner("Loading..."):
    trades = get_all_trades()

    if not trades:
        st.info("Create a trade first.")
        st.stop()

    trade_options = {
        f"{trade['ticker']}: {trade['direction']} - {datetime.fromisoformat(trade['opened_at']).strftime('%b %d, %Y')}": trade[
            "public_id"
        ]
        for trade in trades
    }

journal_form_and_table(trade_options)
