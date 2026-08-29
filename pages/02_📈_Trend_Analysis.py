# pages/02_📈_Trend_Analysis.py

import streamlit as st

from components.navigation import (
    get_selected_stock,
    page_header,
    show_page_navigation,
)

from services.stock_service import (
    analyze_stock,
)

from analytics.trend_analysis import (
    calculate_daily_trend,
)

from utils.indicator_guide import (
    get_indicator_tooltip,
    show_indicator_guide,
)


CURRENT_PAGE = (
    "pages/02_📈_Trend_Analysis.py"
)


# ============================================================
# PAGE HEADER
# ============================================================

page_header(
    "📈 Trend Analysis",
    CURRENT_PAGE
)


# ============================================================
# STOCK DATA
# ============================================================

stock = get_selected_stock()

data = analyze_stock(
    stock
)

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
        "Latest closing price of the selected stock."
    )
)


c2.metric(
    "SMA 20",
    f"₹{latest['SMA_20']:,.2f}",
    help=get_indicator_tooltip("SMA")
)


c3.metric(
    "SMA 50",
    f"₹{latest['SMA_50']:,.2f}",
    help=get_indicator_tooltip("SMA")
)


# ============================================================
# TREND CHART
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
# TREND STUDY GUIDE
# ============================================================

with st.expander(
    "📚 Trend Analysis — Indicator Study Guide",
    expanded=False,
):

    show_indicator_guide(
        st,
        "SMA"
    )

    st.markdown(
        """
        ---

        ### 📌 How to Study the Trend

        **Bullish structure**

        Price > SMA 20 > SMA 50

        **Bearish structure**

        Price < SMA 20 < SMA 50

        ### 🟢 Potential bullish confirmation

        - Price above SMA 20
        - SMA 20 above SMA 50
        - Higher highs / higher lows
        - Positive momentum
        - Volume confirmation

        ### 🔴 Potential bearish confirmation

        - Price below SMA 20
        - SMA 20 below SMA 50
        - Lower highs / lower lows
        - Negative momentum
        - Selling volume

        ⚠️ Moving averages are lagging indicators.
        """
    )


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()
