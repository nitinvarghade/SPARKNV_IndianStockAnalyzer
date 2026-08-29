# pages/03_📉_Technical_Analysis.py

import streamlit as st

from components.navigation import (
    get_selected_stock,
    page_header,
    show_page_navigation,
)

from components.indicator_help import (
    show_indicator_help,
)

from services.stock_service import (
    analyze_stock,
)


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Technical Analysis",
    page_icon="📉",
    layout="wide",
)


CURRENT_PAGE = (
    "pages/03_📉_Technical_Analysis.py"
)


page_header(
    "📉 Technical Analysis",
    CURRENT_PAGE,
)


# ============================================================
# STOCK
# ============================================================

stock = get_selected_stock()


# ============================================================
# ANALYSIS
# ============================================================

try:

    data = analyze_stock(
        stock
    )

except Exception as error:

    st.error(
        f"Unable to analyze {stock}: {error}"
    )

    st.stop()


if data.empty:

    st.error(
        "No analysis data available."
    )

    st.stop()


latest = data.iloc[-1]


# ============================================================
# INDICATOR
# ============================================================

indicator = st.selectbox(
    "Technical Indicator",
    [
        "RSI",
        "MACD",
        "MACD Histogram",
        "Bollinger Bands",
        "Moving Averages",
        "VWAP",
        "Supertrend",
        "ATR",
    ],
)


# ============================================================
# RSI
# ============================================================

if indicator == "RSI":

    st.metric(
        "RSI",
        f"{latest['RSI']:.2f}",
        help=(
            "RSI measures momentum on a "
            "0–100 scale."
        ),
    )

    st.line_chart(
        data["RSI"]
    )

    show_indicator_help(
        "RSI",
        expanded=True,
    )


# ============================================================
# MACD
# ============================================================

elif indicator == "MACD":

    st.line_chart(
        data[
            [
                "MACD",
                "MACD_Signal",
            ]
        ]
    )

    show_indicator_help(
        "MACD",
        expanded=True,
    )

    if "MACD_Histogram" in data.columns:

        show_indicator_help(
            "MACD Histogram"
        )


# ============================================================
# MACD HISTOGRAM
# ============================================================

elif indicator == "MACD Histogram":

    if "MACD_Histogram" in data.columns:

        st.line_chart(
            data[
                "MACD_Histogram"
            ]
        )

    else:

        histogram = (
            data["MACD"]
            - data["MACD_Signal"]
        )

        st.line_chart(
            histogram
        )

    show_indicator_help(
        "MACD Histogram",
        expanded=True,
    )


# ============================================================
# BOLLINGER
# ============================================================

elif indicator == "Bollinger Bands":

    st.line_chart(
        data[
            [
                "Close",
                "BB_Upper",
                "BB_Middle",
                "BB_Lower",
            ]
        ]
    )

    show_indicator_help(
        "Bollinger Bands",
        expanded=True,
    )


# ============================================================
# MOVING AVERAGES
# ============================================================

elif indicator == "Moving Averages":

    columns = [
        "Close",
        "SMA_20",
        "SMA_50",
        "EMA_20",
    ]

    if "SMA_200" in data.columns:

        columns.append(
            "SMA_200"
        )

    st.line_chart(
        data[columns]
    )

    show_indicator_help(
        "SMA",
        expanded=True,
    )

    show_indicator_help(
        "EMA"
    )


# ============================================================
# VWAP
# ============================================================

elif indicator == "VWAP":

    st.line_chart(
        data[
            [
                "Close",
                "VWAP",
            ]
        ]
    )

    show_indicator_help(
        "VWAP",
        expanded=True,
    )


# ============================================================
# SUPERTREND
# ============================================================

elif indicator == "Supertrend":

    st.line_chart(
        data[
            [
                "Close",
                "Supertrend",
            ]
        ]
    )

    show_indicator_help(
        "Supertrend",
        expanded=True,
    )


# ============================================================
# ATR
# ============================================================

elif indicator == "ATR":

    st.line_chart(
        data["ATR"]
    )

    show_indicator_help(
        "ATR",
        expanded=True,
    )


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()