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


page_header(
    "🌊 Volatility Analysis",
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
    help=get_indicator_tooltip(
        "Volatility"
    ),
)


c2.metric(
    "Status",
    status,
    help=get_indicator_tooltip(
        "Volatility"
    ),
)


c3.metric(
    "ATR",
    f"{latest['ATR']:.2f}",
    help=get_indicator_tooltip(
        "ATR"
    ),
)


# ============================================================
# BOLLINGER
# ============================================================

st.subheader(
    "📈 Bollinger Bands",
    help=get_indicator_tooltip(
        "Bollinger Bands"
    ),
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
# ATR
# ============================================================

st.subheader(
    "📊 ATR",
    help=get_indicator_tooltip(
        "ATR"
    ),
)


st.line_chart(
    data[
        [
            "ATR"
        ]
    ]
)


# ============================================================
# GUIDE
# ============================================================

with st.expander(
    "📚 Volatility & ATR Explanation"
):

    show_indicator_guide(
        st,
        "Volatility"
    )

    st.markdown(
        "---"
    )

    show_indicator_guide(
        st,
        "Bollinger Bands"
    )

    st.markdown(
        "---"
    )

    show_indicator_guide(
        st,
        "ATR"
    )


st.divider()

show_page_navigation()