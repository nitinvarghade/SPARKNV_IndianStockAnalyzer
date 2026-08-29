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

from components.indicator_help import (
    show_indicator_help,
)

from analytics.technical_indicators import (
    calculate_heikin_ashi,
)


# ============================================================
# PAGE
# ============================================================

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
    CURRENT_PAGE,
)


# ============================================================
# STOCK INPUT
# ============================================================

current_stock = get_selected_stock()

symbol = st.text_input(
    "NSE Stock Symbol",
    value=current_stock.replace(
        ".NS",
        "",
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
        f"Analyzing {selected_stock}..."
    ):

        data = analyze_stock(
            selected_stock
        )

except Exception as error:

    st.error(
        f"Unable to analyze {selected_stock}: {error}"
    )

    st.stop()


if data is None or data.empty:

    st.error(
        "No analysis data available."
    )

    st.stop()


# ============================================================
# RECOMMENDATION
# ============================================================

(
    recommendation,
    confidence,
    reasons,
) = calculate_recommendation(
    data
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
    change / previous * 100
    if previous
    else 0
)


# ============================================================
# KEY METRICS
# ============================================================

c1, c2, c3, c4, c5 = st.columns(5)


c1.metric(
    "Price",
    f"₹{price:,.2f}",
    f"{change_pct:+.2f}%",
    help=(
        "Latest closing price and change "
        "from the previous available candle."
    ),
)


c2.metric(
    "Recommendation",
    recommendation,
    help=(
        "Technical recommendation generated "
        "by the application's scoring engine."
    ),
)


c3.metric(
    "Confidence",
    f"{confidence:.0f}%",
    help=(
        "Model-strength score. "
        "This is NOT the probability of profit."
    ),
)


c4.metric(
    "RSI",
    f"{latest['RSI']:.2f}",
    help=(
        "RSI measures momentum on a 0–100 scale."
    ),
)


trend_text = (
    "Bullish"
    if latest["Supertrend_Direction"] == 1
    else "Bearish"
)


c5.metric(
    "Trend",
    trend_text,
    help=(
        "Directional assessment based on "
        "the Supertrend indicator."
    ),
)


# ============================================================
# RECOMMENDATION REASONS
# ============================================================

st.subheader(
    "🎯 Why this recommendation?"
)


if reasons:

    for reason in reasons:

        st.write(
            f"• {reason}"
        )

else:

    st.info(
        "No recommendation reasons available."
    )


# ============================================================
# EDUCATIONAL GUIDES
# ============================================================

st.subheader(
    "ℹ️ Understand the Signals"
)


c1, c2, c3 = st.columns(3)


with c1:

    show_indicator_help(
        "RSI"
    )


with c2:

    show_indicator_help(
        "Supertrend"
    )


with c3:

    show_indicator_help(
        "Recommendation"
    )


# ============================================================
# CHART TYPE
# ============================================================

st.divider()


chart_type = st.selectbox(
    "Chart Type",
    [
        "Candlestick",
        "Heikin Ashi",
    ],
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
# CANDLE PATTERN
# ============================================================

st.subheader(
    "🕯️ Latest Candlestick Pattern"
)


candlestick = latest.get(
    "Candlestick",
    "None",
)


if candlestick != "None":

    st.success(
        f"Detected: **{candlestick}**"
    )

else:

    st.info(
        "No major candlestick pattern detected."
    )


show_indicator_help(
    "Candlestick"
)


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()