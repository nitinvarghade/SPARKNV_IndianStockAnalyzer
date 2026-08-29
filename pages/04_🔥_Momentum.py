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


page_header(
    "⚡ Momentum Analysis",
    CURRENT_PAGE
)


stock = get_selected_stock()


try:

    data = analyze_stock(
        stock
    )

except Exception as error:

    st.error(
        str(error)
    )

    st.stop()


if data.empty:

    st.warning(
        f"No data available for {stock}."
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
    help=get_indicator_tooltip(
        "Momentum"
    ),
)


c2.metric(
    "Momentum",
    status,
    help=get_indicator_tooltip(
        "Momentum"
    ),
)


c3.metric(
    "RSI",
    f"{latest['RSI']:.2f}",
    help=get_indicator_tooltip(
        "RSI"
    ),
)


# ============================================================
# INDICATORS
# ============================================================

st.subheader(
    "📈 Momentum Indicators",
    help=(
        "Momentum indicators help evaluate whether "
        "price movement is strengthening or weakening."
    ),
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
# MACD DETAILS
# ============================================================

c1, c2, c3 = st.columns(3)


c1.metric(
    "MACD",
    f"{latest['MACD']:.4f}",
    help=get_indicator_tooltip(
        "MACD"
    ),
)


c2.metric(
    "MACD Signal",
    f"{latest['MACD_Signal']:.4f}",
    help=get_indicator_tooltip(
        "MACD"
    ),
)


c3.metric(
    "MACD Histogram",
    f"{latest['MACD_Histogram']:.4f}",
    help=get_indicator_tooltip(
        "MACD Histogram"
    ),
)


# ============================================================
# GUIDE
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
        "MACD Histogram"
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
# TRADING GUIDE
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


st.divider()

show_page_navigation()