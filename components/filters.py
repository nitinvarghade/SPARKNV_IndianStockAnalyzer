# components/filters.py

import streamlit as st


def stock_selector(
    default="RELIANCE.NS"
):

    value = st.text_input(
        "Stock Symbol",
        value=default.replace(
            ".NS",
            ""
        ),
    )

    if value:

        value = value.strip().upper()

        if not value.endswith(".NS"):

            value += ".NS"

    return value


def timeframe_selector():

    return st.selectbox(
        "Timeframe",
        [
            "1d",
            "1wk",
            "1mo",
        ],
        index=0,
    )


def period_selector():

    return st.selectbox(
        "Period",
        [
            "1mo",
            "3mo",
            "6mo",
            "1y",
            "2y",
            "5y",
        ],
        index=2,
    )