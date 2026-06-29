from http import HTTPStatus
from typing import Any, cast

import pandas as pd
import plotly.express as px
import streamlit as st
from src.core.api import make_api_request
from src.core.auth import auth_check

st.title("Analytics")

st.divider()

auth_check()


def sentiment_chart() -> None:
    st.subheader("Sentiment Chart")

    sentiment_response = make_api_request("GET", "/analytics/sentiment-vs-returns")

    match sentiment_response.status_code:
        case HTTPStatus.OK:
            data = cast(list[dict[str, Any]], sentiment_response.json())
            all_sentiments = ["negative", "neutral", "positive"]
            existing = {item["sentiment"] for item in data}

            for sentiment in all_sentiments:
                if sentiment not in existing:
                    data.append(
                        {
                            "sentiment": sentiment,
                            "average_pnl": 0,
                            "total_pnl": 0,
                            "entry_count": 0,
                        }
                    )

            st.plotly_chart(
                px.bar(
                    data,
                    x="sentiment",
                    y="average_pnl",
                    labels={"sentiment": "Sentiment", "average_pnl": "Average P&L"},
                ),
                width="stretch",
            )

            df_data = pd.DataFrame(data)
            df_data = df_data.drop(["average_pnl"], axis=1)
            df_data = df_data[["sentiment", "total_pnl", "entry_count"]]
            df_data = df_data.rename(
                columns={k: k.replace("_", " ").title() for k in data[0].keys()}
            )

            st.dataframe(df_data, width="stretch", hide_index=True)
        case _:
            st.error(sentiment_response.json())


def confidence_chart() -> None:
    confidence_response = make_api_request("GET", "/analytics/confidence-breakdown")


sentiment_chart()
st.divider()
confidence_chart()
