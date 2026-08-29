# pages/05_📊_Volume_Analysis.py

import streamlit as st

from components.navigation import (
    get_selected_stock,
    page_header,
    show_page_navigation,
)

from services.stock_service import (
    analyze_stock,
)


CURRENT_PAGE = (
    "pages/05_📊_Volume_Analysis.py"
)


page_header(
    "📊 Volume Analysis",
    CURRENT_PAGE
)


stock = get_selected_stock()


data = analyze_stock(
    stock
)


latest = data.iloc[-1]


volume_ratio = latest.get(
    "Volume_Ratio",
    0
)


c1, c2 = st.columns(2)


c1.metric(
    "Volume",
    f"{latest['Volume']:,.0f}"
)


c2.metric(
    "Volume / 20D Avg",
    f"{volume_ratio:.2f}x"
)


st.subheader(
    "📊 Volume Chart"
)


st.bar_chart(
    data["Volume"]
)


with st.expander(
    "ℹ️ Volume Analysis Guide"
):

    st.markdown(
        """
### Volume Spike

A volume spike can indicate increased
market participation.

### Bullish Confirmation

Price breakout + high volume

is generally more meaningful than
a breakout with weak volume.

### Bearish Confirmation

Price breakdown + high volume

can strengthen the bearish signal.

### Rule used by this application

Volume >= 1.5 × 20-day average

is treated as a volume spike.
"""
    )


st.divider()

show_page_navigation()