# pages/01_📊_Dashboard.py

import streamlit as st

from services.stock_service import (
    analyze_stock,
    calculate_recommendation,
)

from components.navigation import (
    get_selected_stock,
    set_selected_stock,
    page_header,
    show_page_navigation,
)

from components.charts import (
    create_price_chart,
    create_heikin_ashi_chart,
)

from analytics.technical_indicators import (
    calculate_heikin_ashi,
)

from utils.indicator_guide import (
    get_indicator_tooltip,
    show_indicator_guide,
)


st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
)


CURRENT_PAGE = (
    "pages/01_📊_Dashboard.py"
)


page_header(
    "📊 Dashboard",
    CURRENT_PAGE
)


# ============================================================
# STOCK INPUT
# ============================================================

current_stock = get_selected_stock()


symbol = st.text_input(
    "NSE Stock Symbol",
    value=current_stock.replace(
        ".NS",
        ""
    ),
    help=(
        "Enter an NSE symbol available in "
        "data/raw/nifty500.csv."
    ),
)


if st.button(
    "🔄 Load Stock",
    type="primary",
):

    set_selected_stock(
        symbol
    )

    st.rerun()


selected_stock = get_selected_stock()


# ============================================================
# ANALYZE
# ============================================================

try:

    with st.spinner(
        f"Processing {selected_stock} from NIFTY500 CSV..."
    ):

        data = analyze_stock(
            selected_stock
        )

except Exception as error:

    st.error(
        str(error)
    )

    st.stop()


if data.empty:

    st.warning(
        f"No data available for {selected_stock}."
    )

    st.stop()


# ============================================================
# RECOMMENDATION
# ============================================================

recommendation, confidence, reasons = (
    calculate_recommendation(
        data
    )
)


latest = data.iloc[-1]


# ============================================================
# PRICE
# ============================================================

price = float(
    latest["Close"]
)


previous = (
    float(
        data["Close"].iloc[-2]
    )
    if len(data) > 1
    else price
)


change = (
    price - previous
)


change_pct = (
    change
    /
    previous
    *
    100
    if previous
    else 0
)


# ============================================================
# METRICS
# ============================================================

c1, c2, c3, c4, c5 = (
    st.columns(5)
)


c1.metric(
    "Price",
    f"₹{price:,.2f}",
    f"{change_pct:+.2f}%",
    help=(
        "Latest closing price from the "
        "NIFTY500 CSV."
    ),
)


c2.metric(
    "Recommendation",
    recommendation,
    help=get_indicator_tooltip(
        "Recommendation"
    ),
)


c3.metric(
    "Confidence",
    f"{confidence:.0f}%",
    help=(
        "Model-strength score based on the "
        "technical conditions used by the "
        "recommendation engine. It is not a "
        "statistical probability of profit."
    ),
)


c4.metric(
    "RSI",
    f"{latest['RSI']:.2f}",
    help=get_indicator_tooltip(
        "RSI"
    ),
)


c5.metric(
    "Trend",
    (
        "Bullish"
        if latest[
            "Supertrend_Direction"
        ] == 1
        else "Bearish"
    ),
    help=get_indicator_tooltip(
        "Supertrend"
    ),
)


# ============================================================
# RECOMMENDATION REASONS
# ============================================================

st.subheader(
    "🎯 Why this recommendation?",
    help=get_indicator_tooltip(
        "Recommendation"
    ),
)


for reason in reasons:

    st.write(
        f"• {reason}"
    )


with st.expander(
    "📚 Recommendation Explanation"
):

    show_indicator_guide(
        st,
        "Recommendation"
    )


# ============================================================
# CHART
# ============================================================

st.divider()


chart_type = st.selectbox(
    "Chart Type",
    [
        "Candlestick",
        "Heikin Ashi",
    ],
    help=(
        "Candlestick shows the original OHLC data. "
        "Heikin Ashi smooths price movement to make "
        "trend direction easier to visualize."
    ),
)


if chart_type == "Candlestick":

    fig = create_price_chart(
        data,
        show_bollinger=True,
        show_sma=True,
        show_ema=True,
    )

else:

    ha = calculate_heikin_ashi(
        data
    )

    fig = create_heikin_ashi_chart(
        ha
    )


st.plotly_chart(
    fig,
    use_container_width=True,
)


# ============================================================
# CANDLESTICK PATTERN
# ============================================================

st.subheader(
    "🕯️ Latest Candlestick Pattern",
    help=get_indicator_tooltip(
        "Candlestick"
    ),
)


pattern = latest.get(
    "Candlestick",
    "None"
)


st.info(
    pattern
)


with st.expander(
    "📚 Candlestick Pattern Explanation"
):

    show_indicator_guide(
        st,
        "Candlestick"
    )


# ============================================================
# DATA SOURCE
# ============================================================

st.caption(
    "Data source: data/raw/nifty500.csv"
)


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()