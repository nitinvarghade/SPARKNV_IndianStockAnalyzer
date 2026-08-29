# pages/04_⚡_Momentum.py

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

from analytics.momentum import (
    momentum_score,
    momentum_status,
)


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Momentum Analysis",
    page_icon="⚡",
    layout="wide",
)


CURRENT_PAGE = (
    "pages/04_⚡_Momentum.py"
)


page_header(
    "⚡ Momentum Analysis",
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


score = momentum_score(
    data
)


status = momentum_status(
    data
)


latest = data.iloc[-1]


# ============================================================
# METRICS
# ============================================================

c1, c2, c3 = st.columns(3)


c1.metric(
    "Momentum Score",
    score,
    help=(
        "Overall momentum score calculated "
        "by the application's momentum engine."
    ),
)


c2.metric(
    "Momentum",
    status,
    help=(
        "Overall momentum status."
    ),
)


c3.metric(
    "RSI",
    f"{latest['RSI']:.2f}",
    help=(
        "RSI measures momentum."
    ),
)


# ============================================================
# CHART
# ============================================================

st.subheader(
    "📈 Momentum Indicators"
)


st.line_chart(
    data[
        [
            "RSI",
            "MACD",
            "MACD_Signal",
        ]
    ]
)


# ============================================================
# EDUCATION
# ============================================================

show_indicator_help(
    "Momentum",
    expanded=True,
)


show_indicator_help(
    "RSI"
)


show_indicator_help(
    "MACD"
)


show_indicator_help(
    "EMA"
)


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()