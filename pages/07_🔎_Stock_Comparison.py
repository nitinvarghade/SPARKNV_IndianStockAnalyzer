# pages/07_🔎_Stock_Comparison.py

import streamlit as st
import pandas as pd

from components.navigation import (
    get_selected_stock,
    page_header,
    show_page_navigation,
)

from components.indicator_help import (
    show_indicator_help,
)

from services.stock_service import (
    get_stock_summary,
)


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Stock Comparison",
    page_icon="🔎",
    layout="wide",
)


CURRENT_PAGE = (
    "pages/07_🔎_Stock_Comparison.py"
)


page_header(
    "🔎 Stock Comparison",
    CURRENT_PAGE,
)


# ============================================================
# STOCKS
# ============================================================

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


# ============================================================
# ANALYSIS
# ============================================================

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


# ============================================================
# DATAFRAME
# ============================================================

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
    df[
        display_columns
    ],
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# EDUCATION
# ============================================================

st.divider()

st.subheader(
    "ℹ️ How to Compare These Indicators"
)


c1, c2, c3 = st.columns(3)


with c1:

    show_indicator_help(
        "RSI"
    )


with c2:

    show_indicator_help(
        "Momentum"
    )


with c3:

    show_indicator_help(
        "Volume Ratio"
    )


c1, c2 = st.columns(2)


with c1:

    show_indicator_help(
        "Volatility"
    )


with c2:

    show_indicator_help(
        "Candlestick"
    )


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()