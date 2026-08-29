# pages/07_🔎_Stock_Comparison.py

import streamlit as st
import pandas as pd

from components.navigation import (
    get_selected_stock,
    page_header,
    show_page_navigation,
)

from services.stock_service import (
    get_stock_summary,
)


CURRENT_PAGE = (
    "pages/07_🔎_Stock_Comparison.py"
)


page_header(
    "🔎 Stock Comparison",
    CURRENT_PAGE
)


selected_stock = get_selected_stock()


default_stocks = [
    selected_stock,
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
]


default_stocks = list(
    dict.fromkeys(
        default_stocks
    )
)


stocks = st.multiselect(
    "Select Stocks",
    options=default_stocks,
    default=default_stocks[:4],
)


if not stocks:

    st.warning(
        "Select at least one stock."
    )

    st.stop()


results = []


for stock in stocks:

    try:

        summary = get_stock_summary(
            stock
        )

        results.append(
            summary
        )

    except Exception as error:

        st.warning(
            f"{stock}: {error}"
        )


if not results:

    st.error(
        "No stock data available."
    )

    st.stop()


df = pd.DataFrame(
    results
)


display_columns = [
    "Symbol",
    "Price",
    "Recommendation",
    "Confidence",
    "Trend",
    "RSI",
    "MomentumScore",
    "VolumeRatio",
    "Volatility",
    "Candlestick",
]


display_columns = [
    column
    for column in display_columns
    if column in df.columns
]


st.dataframe(
    df[display_columns],
    use_container_width=True,
)


st.divider()

show_page_navigation()