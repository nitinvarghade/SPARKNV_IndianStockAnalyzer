# pages/06_🌊_Volatility.py

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

from analytics.volatility import (
    calculate_volatility,
    volatility_status,
)


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Volatility Analysis",
    page_icon="🌊",
    layout="wide",
)


CURRENT_PAGE = (
    "pages/06_🌊_Volatility.py"
)


page_header(
    "🌊 Volatility Analysis",
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


volatility = calculate_volatility(
    data
)


status = volatility_status(
    data
)


# ============================================================
# METRICS
# ============================================================

c1, c2, c3 = st.columns(3)


c1.metric(
    "Volatility",
    f"{volatility:.2f}%",
    help=(
        "Volatility measures the size of "
        "price movements, not direction."
    ),
)


c2.metric(
    "Status",
    status,
    help=(
        "Volatility classification calculated "
        "by the application."
    ),
)


c3.metric(
    "ATR",
    f"{latest['ATR']:.2f}",
    help=(
        "ATR measures average price movement "
        "and does not predict direction."
    ),
)


# ============================================================
# BOLLINGER
# ============================================================

st.subheader(
    "📈 Bollinger Bands"
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


# ============================================================
# EDUCATION
# ============================================================

show_indicator_help(
    "Volatility",
    expanded=True,
)


show_indicator_help(
    "ATR"
)


show_indicator_help(
    "Bollinger Bands"
)


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()