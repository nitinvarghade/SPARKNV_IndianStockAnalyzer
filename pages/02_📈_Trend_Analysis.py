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


CURRENT_PAGE = (
    "pages/02_📈_Trend_Analysis.py"
)


page_header(
    "📈 Trend Analysis",
    CURRENT_PAGE
)


stock = get_selected_stock()


data = analyze_stock(
    stock
)


trend = calculate_daily_trend(
    data
)


latest = data.iloc[-1]


st.subheader(
    f"Trend: {trend}"
)


c1, c2, c3 = st.columns(3)


c1.metric(
    "Price",
    f"₹{latest['Close']:,.2f}"
)

c2.metric(
    "SMA 20",
    f"₹{latest['SMA_20']:,.2f}"
)

c3.metric(
    "SMA 50",
    f"₹{latest['SMA_50']:,.2f}"
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


with st.expander(
    "ℹ️ How to use Trend Analysis"
):

    st.markdown(
        """
### Trend Analysis

**Bullish**
- Price above SMA 20
- SMA 20 above SMA 50
- Higher highs / higher lows

**Potential Buy**
- Price above major moving averages
- SMA 20 crossing above SMA 50
- Momentum confirmation

**Potential Sell**
- Price below SMA 20 and SMA 50
- SMA 20 crossing below SMA 50

A trend indicator should generally be
combined with volume and momentum rather
than used alone.
"""
    )


st.divider()

show_page_navigation()