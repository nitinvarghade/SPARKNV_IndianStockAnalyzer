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


# ============================================================
# PAGE CONFIG
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
        "Enter an NSE stock symbol from your "
        "NIFTY 500 master list. Example: RELIANCE, "
        "TCS, INFY."
    ),
)


if st.button(
    "🔄 Load Stock",
    type="primary",
    use_container_width=False,
):

    clean_symbol = (
        symbol
        .strip()
        .upper()
    )

    if not clean_symbol:

        st.warning(
            "Please enter an NSE stock symbol."
        )

        st.stop()

    set_selected_stock(
        clean_symbol
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
        str(error)
    )

    st.stop()


if data is None or data.empty:

    st.warning(
        f"No historical market data available "
        f"for {selected_stock}."
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
    change /
    previous *
    100
    if previous
    else 0
)


# ============================================================
# TREND
# ============================================================

supertrend_direction = latest.get(
    "Supertrend_Direction",
    0
)


if supertrend_direction == 1:

    trend = "Bullish"

elif supertrend_direction == -1:

    trend = "Bearish"

else:

    trend = "Neutral"


# ============================================================
# KEY METRICS
# ============================================================

c1, c2, c3, c4, c5 = st.columns(5)


c1.metric(
    "Price",
    f"₹{price:,.2f}",
    f"{change_pct:+.2f}%",
    help=(
        "Latest available closing price from "
        "the historical market data."
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
        "Technical model-strength score. "
        "This is NOT a statistical probability "
        "of making a profit."
    ),
)


rsi_value = latest.get(
    "RSI"
)


if rsi_value is not None:

    c4.metric(
        "RSI",
        f"{float(rsi_value):.2f}",
        help=get_indicator_tooltip(
            "RSI"
        ),
    )

else:

    c4.metric(
        "RSI",
        "N/A",
        help=get_indicator_tooltip(
            "RSI"
        ),
    )


c5.metric(
    "Trend",
    trend,
    help=get_indicator_tooltip(
        "Supertrend"
    ),
)


# ============================================================
# STOCK INFORMATION
# ============================================================

company_name = latest.get(
    "Company Name"
)

industry = latest.get(
    "Industry"
)

isin = latest.get(
    "ISIN Code"
)


if company_name or industry or isin:

    with st.expander(
        "🏢 Company Information"
    ):

        info1, info2, info3 = st.columns(3)

        info1.write(
            "**Company**"
        )

        info1.write(
            company_name
            if company_name
            else "N/A"
        )

        info2.write(
            "**Industry**"
        )

        info2.write(
            industry
            if industry
            else "N/A"
        )

        info3.write(
            "**ISIN**"
        )

        info3.write(
            isin
            if isin
            else "N/A"
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


if reasons:

    for reason in reasons:

        st.write(
            f"• {reason}"
        )

else:

    st.info(
        "No individual recommendation reasons "
        "were returned."
    )


# ============================================================
# RECOMMENDATION GUIDE
# ============================================================

with st.expander(
    "📚 How to interpret the recommendation"
):

    show_indicator_guide(
        st,
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
    help=(
        "Candlestick shows actual OHLC prices. "
        "Heikin Ashi smooths price movement to "
        "make trends easier to visualize."
    ),
)


# ============================================================
# CHART
# ============================================================

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
# CHART GUIDE
# ============================================================

with st.expander(
    "📚 Chart & Indicator Guide"
):

    if chart_type == "Candlestick":

        show_indicator_guide(
            st,
            "Bollinger Bands"
        )

        st.markdown(
            "---"
        )

        show_indicator_guide(
            st,
            "SMA"
        )

        st.markdown(
            "---"
        )

        show_indicator_guide(
            st,
            "EMA"
        )

    else:

        show_indicator_guide(
            st,
            "Heikin Ashi"
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
    "📚 Candlestick Pattern — Explanation"
):

    show_indicator_guide(
        st,
        "Candlestick"
    )


# ============================================================
# QUICK INDICATOR SUMMARY
# ============================================================

st.subheader(
    "📊 Technical Indicator Snapshot"
)


summary_columns = st.columns(6)


# RSI
summary_columns[0].metric(
    "RSI",
    (
        f"{float(latest['RSI']):.2f}"
        if "RSI" in latest
        else "N/A"
    ),
    help=get_indicator_tooltip(
        "RSI"
    ),
)


# MACD
summary_columns[1].metric(
    "MACD",
    (
        f"{float(latest['MACD']):.2f}"
        if "MACD" in latest
        else "N/A"
    ),
    help=get_indicator_tooltip(
        "MACD"
    ),
)


# VWAP
summary_columns[2].metric(
    "VWAP",
    (
        f"₹{float(latest['VWAP']):,.2f}"
        if "VWAP" in latest
        else "N/A"
    ),
    help=get_indicator_tooltip(
        "VWAP"
    ),
)


# ATR
summary_columns[3].metric(
    "ATR",
    (
        f"{float(latest['ATR']):.2f}"
        if "ATR" in latest
        else "N/A"
    ),
    help=get_indicator_tooltip(
        "ATR"
    ),
)


# Volume Ratio
volume_ratio = latest.get(
    "Volume_Ratio"
)


summary_columns[4].metric(
    "Volume Ratio",
    (
        f"{float(volume_ratio):.2f}x"
        if volume_ratio is not None
        else "N/A"
    ),
    help=get_indicator_tooltip(
        "Volume Ratio"
    ),
)


# Supertrend
summary_columns[5].metric(
    "Supertrend",
    (
        f"₹{float(latest['Supertrend']):,.2f}"
        if "Supertrend" in latest
        else "N/A"
    ),
    help=get_indicator_tooltip(
        "Supertrend"
    ),
)


# ============================================================
# FULL TECHNICAL GUIDE
# ============================================================

with st.expander(
    "📖 Complete Technical Indicator Guide"
):

    tabs = st.tabs(
        [
            "RSI",
            "MACD",
            "Moving Average",
            "VWAP",
            "Supertrend",
            "Bollinger",
            "ATR",
            "Volume",
        ]
    )


    with tabs[0]:

        show_indicator_guide(
            st,
            "RSI"
        )


    with tabs[1]:

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


    with tabs[2]:

        show_indicator_guide(
            st,
            "SMA"
        )

        st.markdown(
            "---"
        )

        show_indicator_guide(
            st,
            "EMA"
        )


    with tabs[3]:

        show_indicator_guide(
            st,
            "VWAP"
        )


    with tabs[4]:

        show_indicator_guide(
            st,
            "Supertrend"
        )


    with tabs[5]:

        show_indicator_guide(
            st,
            "Bollinger Bands"
        )


    with tabs[6]:

        show_indicator_guide(
            st,
            "ATR"
        )


    with tabs[7]:

        show_indicator_guide(
            st,
            "Volume"
        )

        st.markdown(
            "---"
        )

        show_indicator_guide(
            st,
            "Volume Ratio"
        )


# ============================================================
# DISCLAIMER
# ============================================================

st.divider()

st.info(
    "⚠️ Technical indicators are analytical tools and "
    "do not guarantee profit. Use multiple confirmations, "
    "position sizing and risk management before making "
    "an investment decision."
)


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()