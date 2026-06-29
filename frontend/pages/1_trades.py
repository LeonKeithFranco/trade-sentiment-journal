from datetime import UTC, datetime, time
from http import HTTPStatus

import pandas as pd
import streamlit as st
from src.core.api import (
    convert_pydantic_error_to_human_readable_message,
    get_all_trades,
    make_api_request,
)
from src.core.auth import auth_check

st.title("Trades")

st.divider()

auth_check()

with st.form("trade_form"):
    st.subheader("Create Trade")

    ticker = st.text_input("Ticker", placeholder="e.g. AAPL")
    direction = st.selectbox("Direction", options=["Long", "Short"]).upper()
    position_size = st.number_input(
        "Position Size", min_value=0.0, step=1.0, format="%.4f"
    )
    entry_price = st.number_input("Entry Price", min_value=0.0, step=0.1)
    opened_at = st.date_input("Opened At")
    exit_price = st.number_input(
        "Exit Price (Optional)", min_value=0.0, step=0.1, value=None
    )
    closed_at = st.date_input("Closed At (Optional)", value=None)

    if st.form_submit_button():
        if ticker == "":
            st.error("Ticker field was left blank.")
            st.stop()

        response = make_api_request(
            "POST",
            "/trades",
            json={
                "ticker": ticker,
                "direction": direction,
                "position_size": position_size,
                "entry_price": entry_price,
                "opened_at": datetime.combine(
                    opened_at, time.min, tzinfo=UTC
                ).isoformat(),
                "exit_price": exit_price,
                "closed_at": datetime.combine(
                    closed_at, time.min, tzinfo=UTC
                ).isoformat()
                if closed_at
                else None,
            },
        )

        match response.status_code:
            case HTTPStatus.CREATED:
                st.success("Trade created.")
            case HTTPStatus.UNPROCESSABLE_ENTITY:
                err_detail = response.json()["detail"][0]

                st.error(
                    convert_pydantic_error_to_human_readable_message(
                        err_detail, "Unable to create Trade."
                    )
                )
            case _:
                st.error(response.json())

st.divider()

st.header("All Trades")

with st.spinner("Loading..."):
    trades = get_all_trades()

    if not trades:
        st.info("There are no trades yet.")
        st.stop()

    df_trade = pd.DataFrame(trades)
    df_trade = df_trade.drop(["public_id", "created_on", "updated_on"], axis=1)

    df_trade["opened_at"] = pd.to_datetime(df_trade["opened_at"]).dt.strftime(
        "%b %d, %Y"
    )
    df_trade["closed_at"] = pd.to_datetime(df_trade["closed_at"]).dt.strftime(
        "%b %d, %Y"
    )

    df_trade = df_trade.fillna("-")
    df_trade = df_trade.rename(
        columns={k: k.replace("_", " ").title() for k in trades[0].keys()}
    )

    st.dataframe(df_trade, use_container_width=True, hide_index=True)
