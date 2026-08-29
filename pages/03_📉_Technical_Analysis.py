# pages/03_📉_Technical_Analysis.py

import streamlit as st

from components.navigation import (
    get_selected_stock,
    page_header,
    show_page_navigation,
)

from services.stock_service import (
    analyze_stock,
)

from utils.indicator_guide import (
    get_indicator_tooltip,
    show_indicator_guide,
)


CURRENT_PAGE = (
    "pages/03_📉_Technical_Analysis.py"
)


# ============================================================
# PAGE HEADER
# ============================================================

page_header(
    "📉 Technical Analysis",
    CURRENT_PAGE
)


# ============================================================
# STOCK DATA
# ============================================================

stock = get_selected_stock()

data = analyze_stock(
    stock
)

latest = data.iloc[-1]


# ============================================================
# INDICATOR SELECTOR
# ============================================================

indicator = st.selectbox(
    "Technical Indicator",
    [
        "RSI",
        "MACD",
        "Bollinger Bands",
        "Moving Averages",
        "VWAP",
        "Supertrend",
        "ATR",
    ]
)


# ============================================================
# RSI
# ============================================================

if indicator == "RSI":

    st.metric(
        "RSI",
        f"{latest['RSI']:.2f}",
        help=get_indicator_tooltip("RSI")
    )

    st.line_chart(
        data["RSI"]
    )

    with st.expander(
        "📚 RSI — Complete Study Guide"
    ):

        show_indicator_guide(
            st,
            "RSI"
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

    with st.expander(
        "📚 MACD — Complete Study Guide"
    ):

        show_indicator_guide(
            st,
            "MACD"
        )


# ============================================================
# BOLLINGER BANDS
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

    with st.expander(
        "📚 Bollinger Bands — Complete Study Guide"
    ):

        show_indicator_guide(
            st,
            "Bollinger Bands"
        )


# ============================================================
# MOVING AVERAGES
# ============================================================

elif indicator == "Moving Averages":

    st.line_chart(
        data[
            [
                "Close",
                "SMA_20",
                "SMA_50",
                "SMA_200",
                "EMA_20",
            ]
        ]
    )

    with st.expander(
        "📚 Moving Averages — Complete Study Guide"
    ):

        show_indicator_guide(
            st,
            "SMA"
        )

        st.markdown(
            "---"
        )

        show_indicator_guide(
            st,
            "EMA"
        )


# ============================================================
# VWAP
# ============================================================

elif indicator == "VWAP":

    st.metric(
        "VWAP",
        f"{latest['VWAP']:.2f}",
        help=get_indicator_tooltip("VWAP")
    )

    st.line_chart(
        data[
            [
                "Close",
                "VWAP",
            ]
        ]
    )

    with st.expander(
        "📚 VWAP — Complete Study Guide"
    ):

        show_indicator_guide(
            st,
            "VWAP"
        )


# ============================================================
# SUPERTREND
# ============================================================

elif indicator == "Supertrend":

    st.metric(
        "Supertrend",
        f"{latest['Supertrend']:.2f}",
        help=get_indicator_tooltip("Supertrend")
    )

    st.line_chart(
        data[
            [
                "Close",
                "Supertrend",
            ]
        ]
    )

    with st.expander(
        "📚 Supertrend — Complete Study Guide"
    ):

        show_indicator_guide(
            st,
            "Supertrend"
        )


# ============================================================
# ATR
# ============================================================

elif indicator == "ATR":

    st.metric(
        "ATR",
        f"{latest['ATR']:.2f}",
        help=get_indicator_tooltip("ATR")
    )

    st.line_chart(
        data["ATR"]
    )

    with st.expander(
        "📚 ATR — Complete Study Guide"
    ):

        show_indicator_guide(
            st,
            "ATR"
        )


# ============================================================
# COMPLETE STUDY LIBRARY
# ============================================================

st.divider()

with st.expander(
    "🎓 Open Complete Technical Indicator Library"
):

    st.info(
        "Use this section to study all indicators "
        "used throughout IndianStockAnalyzer."
    )

    for name in [
        "RSI",
        "MACD",
        "VWAP",
        "Supertrend",
        "SMA",
        "EMA",
        "Bollinger Bands",
        "ATR",
        "ADX",
        "Stochastic",
        "CCI",
        "MFI",
        "OBV",
        "Volume",
        "Volume Ratio",
        "Momentum",
        "ROC",
        "Williams %R",
        "Candlestick",
    ]:

        with st.expander(
            f"📖 {name}"
        ):

            show_indicator_guide(
                st,
                name
            )


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()
