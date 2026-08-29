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
# HEADER
# ============================================================

page_header(
    "📉 Technical Analysis",
    CURRENT_PAGE
)


# ============================================================
# STOCK
# ============================================================

stock = get_selected_stock()


try:

    data = analyze_stock(
        stock
    )

except Exception as error:

    st.error(
        str(error)
    )

    st.stop()


if data is None or data.empty:

    st.warning(
        f"No data available for {stock}."
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
    help=(
        "Select a technical indicator to view its "
        "current value, chart and educational guide."
    ),
)


# ============================================================
# RSI
# ============================================================

if indicator == "RSI":

    st.subheader(
        "Relative Strength Index (RSI)",
        help=get_indicator_tooltip(
            "RSI"
        ),
    )

    value = latest.get(
        "RSI"
    )

    st.metric(
        "RSI",
        (
            f"{value:.2f}"
            if value is not None
            else "N/A"
        ),
        help=get_indicator_tooltip(
            "RSI"
        ),
    )

    st.line_chart(
        data["RSI"]
    )

    with st.expander(
        "📚 RSI Explanation & Trading Guide"
    ):

        show_indicator_guide(
            st,
            "RSI"
        )


# ============================================================
# MACD
# ============================================================

elif indicator == "MACD":

    st.subheader(
        "MACD",
        help=get_indicator_tooltip(
            "MACD"
        ),
    )

    st.line_chart(
        data[
            [
                "MACD",
                "MACD_Signal",
            ]
        ]
    )

    st.metric(
        "MACD",
        f"{latest['MACD']:.4f}",
        help=get_indicator_tooltip(
            "MACD"
        ),
    )

    st.metric(
        "Signal",
        f"{latest['MACD_Signal']:.4f}",
        help=get_indicator_tooltip(
            "MACD"
        ),
    )

    st.metric(
        "Histogram",
        f"{latest['MACD_Histogram']:.4f}",
        help=get_indicator_tooltip(
            "MACD Histogram"
        ),
    )

    with st.expander(
        "📚 MACD Explanation & Trading Guide"
    ):

        show_indicator_guide(
            st,
            "MACD"
        )

        st.markdown(
            "---"
        )

        show_indicator_guide(
            st,
            "MACD Histogram"
        )


# ============================================================
# BOLLINGER BANDS
# ============================================================

elif indicator == "Bollinger Bands":

    st.subheader(
        "Bollinger Bands",
        help=get_indicator_tooltip(
            "Bollinger Bands"
        ),
    )

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

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Upper Band",
        f"₹{latest['BB_Upper']:.2f}",
        help=(
            "Upper Bollinger Band = SMA 20 "
            "+ 2 standard deviations."
        ),
    )

    c2.metric(
        "Middle Band",
        f"₹{latest['BB_Middle']:.2f}",
        help=(
            "Middle Bollinger Band is the "
            "20-period Simple Moving Average."
        ),
    )

    c3.metric(
        "Lower Band",
        f"₹{latest['BB_Lower']:.2f}",
        help=(
            "Lower Bollinger Band = SMA 20 "
            "- 2 standard deviations."
        ),
    )

    with st.expander(
        "📚 Bollinger Bands Explanation & Trading Guide"
    ):

        show_indicator_guide(
            st,
            "Bollinger Bands"
        )


# ============================================================
# MOVING AVERAGES
# ============================================================

elif indicator == "Moving Averages":

    st.subheader(
        "Moving Averages",
        help=(
            "Moving averages smooth price data and help "
            "identify trend direction."
        ),
    )

    columns = [
        "Close",
        "SMA_20",
        "SMA_50",
        "SMA_200",
        "EMA_9",
        "EMA_20",
        "EMA_50",
    ]

    available = [
        column
        for column in columns
        if column in data.columns
    ]

    st.line_chart(
        data[available]
    )

    st.markdown(
        "### SMA"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "SMA 20",
        f"₹{latest['SMA_20']:.2f}",
        help=get_indicator_tooltip(
            "SMA 20"
        ),
    )

    c2.metric(
        "SMA 50",
        f"₹{latest['SMA_50']:.2f}",
        help=get_indicator_tooltip(
            "SMA 50"
        ),
    )

    c3.metric(
        "SMA 200",
        f"₹{latest['SMA_200']:.2f}",
        help=get_indicator_tooltip(
            "SMA 200"
        ),
    )

    st.markdown(
        "### EMA"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "EMA 9",
        f"₹{latest['EMA_9']:.2f}",
        help=get_indicator_tooltip(
            "EMA 9"
        ),
    )

    c2.metric(
        "EMA 20",
        f"₹{latest['EMA_20']:.2f}",
        help=get_indicator_tooltip(
            "EMA 20"
        ),
    )

    c3.metric(
        "EMA 50",
        f"₹{latest['EMA_50']:.2f}",
        help=get_indicator_tooltip(
            "EMA 50"
        ),
    )

    with st.expander(
        "📚 Moving Average Explanation & Trading Guide"
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

    st.subheader(
        "Volume Weighted Average Price (VWAP)",
        help=get_indicator_tooltip(
            "VWAP"
        ),
    )

    st.line_chart(
        data[
            [
                "Close",
                "VWAP",
            ]
        ]
    )

    c1, c2 = st.columns(2)

    c1.metric(
        "Current Price",
        f"₹{latest['Close']:.2f}",
        help=(
            "Latest closing price in the selected "
            "CSV data."
        ),
    )

    c2.metric(
        "VWAP",
        f"₹{latest['VWAP']:.2f}",
        help=get_indicator_tooltip(
            "VWAP"
        ),
    )

    with st.expander(
        "📚 VWAP Explanation & Trading Guide"
    ):

        show_indicator_guide(
            st,
            "VWAP"
        )


# ============================================================
# SUPERTREND
# ============================================================

elif indicator == "Supertrend":

    st.subheader(
        "Supertrend",
        help=get_indicator_tooltip(
            "Supertrend"
        ),
    )

    st.line_chart(
        data[
            [
                "Close",
                "Supertrend",
            ]
        ]
    )

    direction = latest.get(
        "Supertrend_Direction"
    )

    trend = (
        "Bullish"
        if direction == 1
        else "Bearish"
    )

    c1, c2 = st.columns(2)

    c1.metric(
        "Supertrend",
        f"₹{latest['Supertrend']:.2f}",
        help=get_indicator_tooltip(
            "Supertrend"
        ),
    )

    c2.metric(
        "Direction",
        trend,
        help=(
            "Bullish when price is generally above "
            "the Supertrend line; bearish when below."
        ),
    )

    with st.expander(
        "📚 Supertrend Explanation & Trading Guide"
    ):

        show_indicator_guide(
            st,
            "Supertrend"
        )


# ============================================================
# ATR
# ============================================================

elif indicator == "ATR":

    st.subheader(
        "Average True Range (ATR)",
        help=get_indicator_tooltip(
            "ATR"
        ),
    )

    st.line_chart(
        data["ATR"]
    )

    st.metric(
        "ATR",
        f"{latest['ATR']:.2f}",
        help=get_indicator_tooltip(
            "ATR"
        ),
    )

    with st.expander(
        "📚 ATR Explanation & Trading Guide"
    ):

        show_indicator_guide(
            st,
            "ATR"
        )


# ============================================================
# COMMON WARNING
# ============================================================

st.divider()

st.info(
    "⚠️ Technical indicators are analytical tools, "
    "not guaranteed Buy/Sell predictions. Use multiple "
    "independent confirmations and risk management."
)


# ============================================================
# NAVIGATION
# ============================================================

show_page_navigation()