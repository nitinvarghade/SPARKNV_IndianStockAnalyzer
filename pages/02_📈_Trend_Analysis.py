# pages/02_📈_Trend_Analysis.py

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

from analytics.trend_analysis import (
    calculate_daily_trend,
)


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Trend Analysis",
    page_icon="📈",
    layout="wide",
)


CURRENT_PAGE = (
    "pages/02_📈_Trend_Analysis.py"
)


page_header(
    "📈 Trend Analysis",
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


trend = calculate_daily_trend(
    data
)


latest = data.iloc[-1]


# ============================================================
# TREND
# ============================================================

st.subheader(
    f"Trend: {trend}"
)


# ============================================================
# METRICS
# ============================================================

c1, c2, c3 = st.columns(3)


c1.metric(
    "Price",
    f"₹{latest['Close']:,.2f}",
    help=(
        "Current closing price."
    ),
)


c2.metric(
    "SMA 20",
    f"₹{latest['SMA_20']:,.2f}",
    help=(
        "20-period Simple Moving Average."
    ),
)


c3.metric(
    "SMA 50",
    f"₹{latest['SMA_50']:,.2f}",
    help=(
        "50-period Simple Moving Average."
    ),
)


# ============================================================
# CHART
# ============================================================

st.subheader(
    "📈 Price vs Moving Averages"
)


st.line_chart(
    data[
        [
            "Close",
            "SMA_20",
            "SMA_50",
        ]
    ]
)


# ============================================================
# EDUCATION
# ============================================================

show_indicator_help(
    "Trend",
    expanded=True,
)


show_indicator_help(
    "SMA"
)


show_indicator_help(
    "EMA"
)


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()