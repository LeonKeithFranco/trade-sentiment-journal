from http import HTTPStatus

import plotly.express as px
import streamlit as st
from src.core.api import make_api_request
from src.core.auth import auth_check

st.title("Analytics")

st.divider()

auth_check()


def sentiment_chart() -> None:
    sentiment_response = make_api_request("GET", "/analytics/sentiment-vs-returns")

    match sentiment_response.status_code:
        case HTTPStatus.OK:
            data = sentiment_response.json()
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
        case _:
            st.error(sentiment_response.json())


sentiment_chart()
# confidence_response = make_api_request("GET", "/analytics/confidence-breakdown")
