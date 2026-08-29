# pages/06_🌊_Volatility.py

import streamlit as st

from components.navigation import (
    get_selected_stock,
    page_header,
    show_page_navigation,
)

from services.stock_service import (
    analyze_stock,
)

from analytics.volatility import (
    calculate_volatility,
    volatility_status,
)

from utils.indicator_guide import (
    get_indicator_tooltip,
    show_indicator_guide,
)


CURRENT_PAGE = (
    "pages/06_🌊_Volatility.py"
)


# ============================================================
# HEADER
# ============================================================

page_header(
    "🌊 Volatility Analysis",
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
        "Volatility describes the magnitude "
        "of price movement. Higher volatility "
        "means larger price fluctuations."
    )
)


c2.metric(
    "Status",
    status,
    help=(
        "Current volatility classification "
        "calculated by the application."
    )
)


c3.metric(
    "ATR",
    f"{latest['ATR']:.2f}",
    help=get_indicator_tooltip("ATR")
)


# ============================================================
# BOLLINGER BANDS
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
# VOLATILITY STUDY GUIDE
# ============================================================

with st.expander(
    "📚 Volatility Indicator Study Guide"
):

    show_indicator_guide(
        st,
        "ATR"
    )

    st.markdown(
        "---"
    )

    show_indicator_guide(
        st,
        "Bollinger Bands"
    )


# ============================================================
# VOLATILITY INTERPRETATION
# ============================================================

with st.expander(
    "🎯 How to Study Volatility"
):

    st.markdown(
        """
### 🔥 High Volatility

Potential advantages:

- Larger price movement
- More trading opportunities

Potential risks:

- Wider stop-loss
- Larger drawdown
- Greater position-size risk

### 🧊 Low Volatility

Can indicate:

- Consolidation
- Reduced price movement
- Potential preparation for a breakout

### ⚠️ Bollinger squeeze

A Bollinger Band squeeze can sometimes precede
a larger move.

However, the direction needs confirmation.

Use:

**Trend + Volume + Momentum + Price Action**
"""
    )


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()