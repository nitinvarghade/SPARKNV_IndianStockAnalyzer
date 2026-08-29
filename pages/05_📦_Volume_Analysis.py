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

from utils.indicator_guide import (
    get_indicator_tooltip,
    show_indicator_guide,
)


CURRENT_PAGE = (
    "pages/05_📊_Volume_Analysis.py"
)


# ============================================================
# HEADER
# ============================================================

page_header(
    "📊 Volume Analysis",
    CURRENT_PAGE
)


# ============================================================
# DATA
# ============================================================

stock = get_selected_stock()

data = analyze_stock(
    stock
)

latest = data.iloc[-1]


volume_ratio = latest.get(
    "Volume_Ratio",
    0
)


# ============================================================
# METRICS
# ============================================================

c1, c2 = st.columns(2)


c1.metric(
    "Volume",
    f"{latest['Volume']:,.0f}",
    help=get_indicator_tooltip("Volume")
)


c2.metric(
    "Volume / 20D Avg",
    f"{volume_ratio:.2f}x",
    help=get_indicator_tooltip("Volume Ratio")
)


# ============================================================
# CHART
# ============================================================

st.subheader(
    "📊 Volume Chart"
)

st.bar_chart(
    data["Volume"]
)


# ============================================================
# VOLUME STUDY GUIDE
# ============================================================

with st.expander(
    "📚 Volume Indicator Study Guide"
):

    show_indicator_guide(
        st,
        "Volume"
    )

    st.markdown(
        "---"
    )

    show_indicator_guide(
        st,
        "Volume Ratio"
    )


# ============================================================
# VOLUME CONFIRMATION
# ============================================================

with st.expander(
    "🎯 How to Study Volume Confirmation"
):

    st.markdown(
        """
### 🟢 Bullish confirmation

Price breakout

+

High volume

can provide stronger confirmation than a breakout with weak volume.

### 🔴 Bearish confirmation

Price breakdown

+

High volume

can strengthen the bearish interpretation.

### 📌 Application rule

Volume >= 1.5 × 20-day average

is treated as a volume spike.

### ⚠️ Important

High volume by itself does not determine direction.
Always study it together with price movement.
"""
    )


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()