# pages/02_📈_Trend_Analysis.py

import streamlit as st

from components.navigation import (
    get_selected_stock,
    page_header,
    show_page_navigation,
)

from services.stock_service import (
    analyze_stock,
)

from analytics.trend_analysis import (
    calculate_daily_trend,
)

from utils.indicator_guide import (
    get_indicator_tooltip,
    show_indicator_guide,
)


CURRENT_PAGE = (
    "pages/02_📈_Trend_Analysis.py"
)


page_header(
    "📈 Trend Analysis",
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


trend = calculate_daily_trend(
    data
)

latest = data.iloc[-1]


st.subheader(
    f"Current Trend: {trend}",
    help=get_indicator_tooltip(
        "Trend"
    ),
)


c1, c2, c3 = st.columns(3)


c1.metric(
    "Price",
    f"₹{latest['Close']:,.2f}",
    help=(
        "Latest closing price from the "
        "NIFTY500 CSV data."
    ),
)


c2.metric(
    "SMA 20",
    f"₹{latest['SMA_20']:,.2f}",
    help=get_indicator_tooltip(
        "SMA 20"
    ),
)


c3.metric(
    "SMA 50",
    f"₹{latest['SMA_50']:,.2f}",
    help=get_indicator_tooltip(
        "SMA 50"
    ),
)


st.line_chart(
    data[
        [
            "Close",
            "SMA_20",
            "SMA_50",
            "SMA_200",
        ]
    ]
)


with st.expander(
    "📚 Trend Analysis Explanation & Trading Guide"
):

    show_indicator_guide(
        st,
        "Trend"
    )


st.divider()

show_page_navigation()