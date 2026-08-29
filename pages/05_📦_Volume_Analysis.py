# pages/05_📊_Volume_Analysis.py

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
    page_title="Volume Analysis",
    page_icon="📊",
    layout="wide",
)


CURRENT_PAGE = (
    "pages/05_📊_Volume_Analysis.py"
)


page_header(
    "📊 Volume Analysis",
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


volume_ratio = float(
    latest.get(
        "Volume_Ratio",
        0,
    )
)


# ============================================================
# METRICS
# ============================================================

c1, c2 = st.columns(2)


c1.metric(
    "Volume",
    f"{latest['Volume']:,.0f}",
    help=(
        "Number of shares traded "
        "during the selected period."
    ),
)


c2.metric(
    "Volume / 20D Avg",
    f"{volume_ratio:.2f}x",
    help=(
        "Current volume divided by "
        "20-period average volume."
    ),
)


# ============================================================
# VOLUME CHART
# ============================================================

st.subheader(
    "📊 Volume Chart"
)


st.bar_chart(
    data["Volume"]
)


# ============================================================
# EDUCATION
# ============================================================

show_indicator_help(
    "Volume",
    expanded=True,
)


show_indicator_help(
    "Volume Ratio"
)


# ============================================================
# APPLICATION RULE
# ============================================================

if volume_ratio >= 1.5:

    st.success(
        f"📈 Volume spike detected: "
        f"{volume_ratio:.2f}x the 20-period average."
    )

else:

    st.info(
        f"Normal volume: "
        f"{volume_ratio:.2f}x the 20-period average."
    )


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()