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


CURRENT_PAGE = (
    "pages/06_🌊_Volatility.py"
)


page_header(
    "🌊 Volatility Analysis",
    CURRENT_PAGE
)


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


c1, c2, c3 = st.columns(3)


c1.metric(
    "Volatility",
    f"{volatility:.2f}%"
)

c2.metric(
    "Status",
    status
)

c3.metric(
    "ATR",
    f"{latest['ATR']:.2f}"
)


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


with st.expander(
    "ℹ️ Volatility Guide"
):

    st.markdown(
        """
### High Volatility

Advantages:
- Larger price moves
- More trading opportunities

Risks:
- Wider stop-loss
- Greater drawdown risk

### Low Volatility

Can indicate consolidation.

A Bollinger Band squeeze can sometimes
precede a breakout, but direction requires
confirmation.
"""
    )


st.divider()

show_page_navigation()