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


CURRENT_PAGE = (
    "pages/04_⚡_Momentum.py"
)


page_header(
    "⚡ Momentum Analysis",
    CURRENT_PAGE
)


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


c1, c2, c3 = st.columns(3)


c1.metric(
    "Momentum Score",
    score
)

c2.metric(
    "Momentum",
    status
)

c3.metric(
    "RSI",
    f"{latest['RSI']:.2f}"
)


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


with st.expander(
    "ℹ️ Momentum Trading Guide"
):

    st.markdown(
        """
### Positive Momentum

Look for:

- RSI above 50
- MACD above signal
- Price above EMA 20
- Increasing volume

### Strong Momentum

A stronger setup occurs when
multiple indicators confirm each other.

Avoid relying on a single momentum
indicator.
"""
    )


st.divider()

show_page_navigation()