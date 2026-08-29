# pages/04_⚡_Momentum.py

import streamlit as st

from components.navigation import (
    get_selected_stock,
    page_header,
    show_page_navigation,
)

from services.stock_service import (
    analyze_stock,
)

from analytics.momentum import (
    momentum_score,
    momentum_status,
)

from utils.indicator_guide import (
    get_indicator_tooltip,
    show_indicator_guide,
    get_trading_guide,
)


CURRENT_PAGE = (
    "pages/04_⚡_Momentum.py"
)


# ============================================================
# HEADER
# ============================================================

page_header(
    "⚡ Momentum Analysis",
    CURRENT_PAGE
)


# ============================================================
# DATA
# ============================================================

stock = get_selected_stock()

data = analyze_stock(
    stock
)

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
        "by the application."
    )
)


c2.metric(
    "Momentum",
    status,
    help=(
        "Current momentum classification "
        "calculated by the application."
    )
)


c3.metric(
    "RSI",
    f"{latest['RSI']:.2f}",
    help=get_indicator_tooltip("RSI")
)


# ============================================================
# MOMENTUM CHART
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
# INDICATOR GUIDES
# ============================================================

with st.expander(
    "📚 Momentum Indicator Study Guide"
):

    show_indicator_guide(
        st,
        "RSI"
    )

    st.markdown(
        "---"
    )

    show_indicator_guide(
        st,
        "MACD"
    )

    st.markdown(
        "---"
    )

    show_indicator_guide(
        st,
        "EMA"
    )

    st.markdown(
        "---"
    )

    show_indicator_guide(
        st,
        "Volume"
    )

    st.markdown(
        "---"
    )

    show_indicator_guide(
        st,
        "Momentum"
    )


# ============================================================
# TRADING STUDY GUIDE
# ============================================================

with st.expander(
    "🎯 How to Study Momentum Signals"
):

    st.markdown(
        get_trading_guide(
            "BUY"
        )
    )

    st.markdown(
        "---"
    )

    st.markdown(
        get_trading_guide(
            "SELL"
        )
    )

    st.markdown(
        "---"
    )

    st.markdown(
        get_trading_guide(
            "HOLD"
        )
    )


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()
