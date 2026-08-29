# pages/01_📊_Dashboard.py

import streamlit as st
import pandas as pd

from components.navigation import (
    get_selected_stock,
    page_header,
    show_page_navigation,
)

from services.stock_service import analyze_stock

from utils.indicator_guide import (
    get_indicator_tooltip,
    show_indicator_guide,
    get_trading_guide,
)


CURRENT_PAGE = "pages/01_📊_Dashboard.py"


# ============================================================
# PAGE HEADER
# ============================================================

page_header(
    "📊 Indian Stock Analyzer Dashboard",
    CURRENT_PAGE
)


# ============================================================
# SELECTED STOCK
# ============================================================

stock = get_selected_stock()

if not stock:
    st.warning("Please select a stock.")
    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

try:
    data = analyze_stock(stock)
except Exception as e:
    st.error(f"Unable to analyze {stock}: {e}")
    st.stop()


if data is None or data.empty:
    st.warning(
        f"No analysis data available for {stock}."
    )
    st.stop()


latest = data.iloc[-1]


# ============================================================
# HELPER
# ============================================================

def safe_value(column, default=None):

    if column not in data.columns:
        return default

    value = latest[column]

    if pd.isna(value):
        return default

    return value


# ============================================================
# STOCK HEADER
# ============================================================

st.title(f"📈 {stock}")

st.caption(
    "Technical analysis dashboard for the selected Indian stock."
)


# ============================================================
# BASIC PRICE METRICS
# ============================================================

st.subheader("💰 Price Overview")

c1, c2, c3, c4 = st.columns(4)


close_price = safe_value("Close", 0)
open_price = safe_value("Open", 0)
high_price = safe_value("High", 0)
low_price = safe_value("Low", 0)


c1.metric(
    "Current Price",
    f"₹{close_price:,.2f}",
    help=(
        "Latest available closing price of the selected stock."
    )
)


c2.metric(
    "Open",
    f"₹{open_price:,.2f}",
    help=(
        "Opening price of the latest available trading period."
    )
)


c3.metric(
    "Day High",
    f"₹{high_price:,.2f}",
    help=(
        "Highest traded price during the latest available period."
    )
)


c4.metric(
    "Day Low",
    f"₹{low_price:,.2f}",
    help=(
        "Lowest traded price during the latest available period."
    )
)


# ============================================================
# TREND INDICATORS
# ============================================================

st.subheader("📈 Trend Indicators")

c1, c2, c3, c4 = st.columns(4)


sma20 = safe_value("SMA_20")
sma50 = safe_value("SMA_50")
sma200 = safe_value("SMA_200")
ema20 = safe_value("EMA_20")


c1.metric(
    "SMA 20",
    f"₹{sma20:,.2f}" if sma20 is not None else "N/A",
    help=get_indicator_tooltip("SMA")
)


c2.metric(
    "SMA 50",
    f"₹{sma50:,.2f}" if sma50 is not None else "N/A",
    help=get_indicator_tooltip("SMA")
)


c3.metric(
    "SMA 200",
    f"₹{sma200:,.2f}" if sma200 is not None else "N/A",
    help=get_indicator_tooltip("SMA")
)


c4.metric(
    "EMA 20",
    f"₹{ema20:,.2f}" if ema20 is not None else "N/A",
    help=get_indicator_tooltip("EMA")
)


# ============================================================
# MOMENTUM INDICATORS
# ============================================================

st.subheader("⚡ Momentum Indicators")

c1, c2, c3 = st.columns(3)


rsi = safe_value("RSI")
macd = safe_value("MACD")
macd_signal = safe_value("MACD_Signal")


c1.metric(
    "RSI",
    f"{rsi:.2f}" if rsi is not None else "N/A",
    help=get_indicator_tooltip("RSI")
)


c2.metric(
    "MACD",
    f"{macd:.2f}" if macd is not None else "N/A",
    help=get_indicator_tooltip("MACD")
)


c3.metric(
    "MACD Signal",
    f"{macd_signal:.2f}" if macd_signal is not None else "N/A",
    help=get_indicator_tooltip("MACD")
)


# ============================================================
# TREND / VOLATILITY
# ============================================================

st.subheader("🌊 Trend & Volatility")

c1, c2, c3 = st.columns(3)


supertrend = safe_value("Supertrend")
atr = safe_value("ATR")
vwap = safe_value("VWAP")


c1.metric(
    "Supertrend",
    (
        f"₹{supertrend:,.2f}"
        if supertrend is not None
        else "N/A"
    ),
    help=get_indicator_tooltip("Supertrend")
)


c2.metric(
    "ATR",
    f"{atr:.2f}" if atr is not None else "N/A",
    help=get_indicator_tooltip("ATR")
)


c3.metric(
    "VWAP",
    (
        f"₹{vwap:,.2f}"
        if vwap is not None
        else "N/A"
    ),
    help=get_indicator_tooltip("VWAP")
)


# ============================================================
# VOLUME
# ============================================================

st.subheader("📊 Volume")

c1, c2 = st.columns(2)


volume = safe_value("Volume", 0)
volume_ratio = safe_value("Volume_Ratio")


c1.metric(
    "Volume",
    f"{volume:,.0f}",
    help=get_indicator_tooltip("Volume")
)


c2.metric(
    "Volume Ratio",
    (
        f"{volume_ratio:.2f}x"
        if volume_ratio is not None
        else "N/A"
    ),
    help=get_indicator_tooltip("Volume Ratio")
)


# ============================================================
# PRICE CHART
# ============================================================

st.subheader("📈 Price Chart")

chart_columns = ["Close"]

for column in [
    "SMA_20",
    "SMA_50",
    "SMA_200",
    "EMA_20",
]:
    if column in data.columns:
        chart_columns.append(column)


st.line_chart(
    data[chart_columns]
)


# ============================================================
# BOLLINGER BANDS
# ============================================================

bollinger_columns = [
    "Close"
]

for column in [
    "BB_Upper",
    "BB_Middle",
    "BB_Lower",
]:

    if column in data.columns:
        bollinger_columns.append(column)


if len(bollinger_columns) > 1:

    st.subheader("🌊 Bollinger Bands")

    st.line_chart(
        data[bollinger_columns]
    )


# ============================================================
# TECHNICAL INDICATOR STUDY GUIDE
# ============================================================

st.divider()

with st.expander(
    "📚 Dashboard — Technical Indicator Study Guide"
):

    st.info(
        "Hover over individual metrics for quick explanations. "
        "Use the sections below for detailed learning."
    )

    with st.expander("📖 RSI"):
        show_indicator_guide(st, "RSI")

    with st.expander("📖 MACD"):
        show_indicator_guide(st, "MACD")

    with st.expander("📖 SMA"):
        show_indicator_guide(st, "SMA")

    with st.expander("📖 EMA"):
        show_indicator_guide(st, "EMA")

    with st.expander("📖 VWAP"):
        show_indicator_guide(st, "VWAP")

    with st.expander("📖 Supertrend"):
        show_indicator_guide(st, "Supertrend")

    with st.expander("📖 ATR"):
        show_indicator_guide(st, "ATR")

    with st.expander("📖 Bollinger Bands"):
        show_indicator_guide(
            st,
            "Bollinger Bands"
        )

    with st.expander("📖 Volume"):
        show_indicator_guide(
            st,
            "Volume"
        )

    with st.expander("📖 Volume Ratio"):
        show_indicator_guide(
            st,
            "Volume Ratio"
        )


# ============================================================
# BUY / SELL / HOLD EDUCATION
# ============================================================

with st.expander(
    "🎯 How to Study BUY / SELL / HOLD Signals"
):

    tab1, tab2, tab3 = st.tabs(
        [
            "🟢 BUY Study",
            "🔴 SELL Study",
            "🟡 HOLD Study",
        ]
    )

    with tab1:
        st.markdown(
            get_trading_guide("BUY")
        )

    with tab2:
        st.markdown(
            get_trading_guide("SELL")
        )

    with tab3:
        st.markdown(
            get_trading_guide("HOLD")
        )


# ============================================================
# RISK MANAGEMENT
# ============================================================

with st.expander(
    "⚠️ Risk Management Study Guide"
):

    st.markdown(
        get_trading_guide("RISK")
    )


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()