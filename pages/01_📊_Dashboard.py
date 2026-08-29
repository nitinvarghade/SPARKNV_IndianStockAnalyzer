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
)


from components.indicator_help import (
    show_indicator_help,
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
# SELECT STOCK
# ============================================================

current_stock = get_selected_stock()


input_symbol = st.text_input(
    "NSE Stock Symbol",
    value=current_stock.replace(
        ".NS",
        "",
    ),
    help=(
        "Enter NSE symbol, for example "
        "RELIANCE, TCS, INFY."
    ),
)


if st.button(
    "🔄 Load Stock",
    type="primary",
):

    clean_symbol = (
        input_symbol
        .strip()
        .upper()
    )

    if clean_symbol:

        if not clean_symbol.endswith(
            ".NS"
        ):

            clean_symbol += ".NS"

        set_selected_stock(
            clean_symbol
        )

        st.rerun()


selected_stock = get_selected_stock()


# ============================================================
# LOAD DATA
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
        f"Unable to analyze "
        f"{selected_stock}: {error}"
    )

    st.stop()


if data is None or data.empty:

    st.error(
        f"No data available for "
        f"{selected_stock}."
    )

    st.stop()


latest = data.iloc[-1]


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


# ============================================================
# PRICE
# ============================================================

price = float(
    latest["Close"]
)


if len(data) > 1:

    previous_price = float(
        data["Close"].iloc[-2]
    )

else:

    previous_price = price


change = (
    price - previous_price
)


change_pct = (
    change
    / previous_price
    * 100
    if previous_price
    else 0
)


# ============================================================
# METRICS
# ============================================================

c1, c2, c3, c4, c5 = st.columns(5)


c1.metric(
    "Price",
    f"₹{price:,.2f}",
    f"{change_pct:+.2f}%",
)


c2.metric(
    "Recommendation",
    recommendation,
)


c3.metric(
    "Confidence",
    f"{confidence:.0f}%",
    help=(
        "Technical model strength. "
        "It is NOT probability of profit."
    ),
)


c4.metric(
    "RSI",
    f"{latest.get('RSI', 0):.2f}",
)


trend = (
    "Bullish"
    if latest.get(
        "Supertrend_Direction",
        0,
    ) == 1
    else "Bearish"
)


c5.metric(
    "Trend",
    trend,
)


# ============================================================
# REASONS
# ============================================================

st.subheader(
    "🎯 Recommendation Signals"
)


for reason in reasons:

    st.write(
        f"• {reason}"
    )


# ============================================================
# EDUCATIONAL SECTION
# ============================================================

st.subheader(
    "ℹ️ Indicator Guide"
)


c1, c2, c3 = st.columns(3)


with c1:

    show_indicator_help(
        "RSI"
    )


with c2:

    show_indicator_help(
        "MACD"
    )


with c3:

    show_indicator_help(
        "Supertrend"
    )


# ============================================================
# PRICE CHART
# ============================================================

st.divider()


st.subheader(
    "📈 Price Chart"
)


try:

    fig = create_price_chart(
        data,
        show_bollinger=True,
        show_sma=True,
        show_ema=True,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

except Exception as error:

    st.warning(
        f"Unable to display chart: {error}"
    )


# ============================================================
# CANDLESTICK PATTERN
# ============================================================

st.subheader(
    "🕯️ Latest Candlestick Pattern"
)


pattern = "None"


pattern_columns = [
    "Doji",
    "Hammer",
    "Inverted_Hammer",
    "Shooting_Star",
    "Bullish_Engulfing",
    "Bearish_Engulfing",
    "Bullish_Harami",
    "Bearish_Harami",
    "Bullish_Marubozu",
    "Bearish_Marubozu",
    "Morning_Star",
    "Evening_Star",
    "Piercing_Pattern",
    "Dark_Cloud_Cover",
    "Three_White_Soldiers",
    "Three_Black_Crows",
]


patterns = []


for column in pattern_columns:

    if column not in data.columns:
        continue

    try:

        if bool(
            latest[column]
        ):

            patterns.append(
                column.replace(
                    "_",
                    " ",
                )
            )

    except Exception:

        continue


if patterns:

    pattern = ", ".join(
        patterns
    )

    st.success(
        f"Detected: **{pattern}**"
    )

else:

    st.info(
        "No major candlestick pattern "
        "detected on the latest candle."
    )


show_indicator_help(
    "Candlestick"
)


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()