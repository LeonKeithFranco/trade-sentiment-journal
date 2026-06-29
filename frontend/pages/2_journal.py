from datetime import datetime
from http import HTTPStatus
from typing import Any, cast

import pandas as pd
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
def journal_form() -> None:
    with st.form("entry_form"):
        st.subheader("Create Journal Entry")

        trade_option = st.selectbox("Trades", options=st.session_state["trade_options"])
        title = st.text_input("Title (Optional)", value=None)
        entry = st.text_area("Entry")

        if st.form_submit_button():
            response = make_api_request(
                "POST",
                "/journal-entries",
                json={
                    "title": title if title else None,
                    "entry": entry,
                    "trade_public_id": st.session_state["trade_options"][trade_option],
                },
            )

            match response.status_code:
                case HTTPStatus.CREATED:
                    st.success("Journal entry created.")

                    st.rerun()
                case HTTPStatus.UNPROCESSABLE_ENTITY:
                    err_detail = response.json()["detail"][0]

                    st.error(
                        convert_pydantic_error_to_human_readable_message(
                            err_detail, "Unable to create Journal entry."
                        )
                    )
                case _:
                    st.error(response.json())


@st.fragment
def journal_entries_table() -> None:
    st.header("All Journal Entries")

    response = make_api_request("GET", "/journal-entries")
    journal_entries = cast(list[dict[str, Any]], response.json())

    if not journal_entries:
        st.info("There are no journal entries yet.")
        st.stop()

    df_journal_entries = pd.DataFrame(journal_entries)
    df_journal_entries = df_journal_entries.drop(
        ["public_id", "created_on", "updated_on"], axis=1
    )

    df_journal_entries = df_journal_entries.fillna("-")
    df_journal_entries = df_journal_entries.rename(
        columns={k: k.replace("_", " ").title() for k in journal_entries[0].keys()}
    )

    st.dataframe(df_journal_entries, width=True, hide_index=True)


with st.spinner("Loading..."):
    if "trade_options" not in st.session_state:
        trades = get_all_trades()

        if not trades:
            st.info("Create a trade first.")
            st.stop()

        st.session_state["trade_options"] = {
            f"{trade['ticker']}: {trade['direction']} - {datetime.fromisoformat(trade['opened_at']).strftime('%b %d, %Y')}": trade[
                "public_id"
            ]
            for trade in trades
        }

journal_form()
st.divider()
journal_entries_table()
