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
)


# ============================================================
# PAGE
# ============================================================

CURRENT_PAGE = (
    "pages/04_⚡_Momentum.py"
)


page_header(
    "⚡ Momentum Analysis",
    CURRENT_PAGE
)


# ============================================================
# STOCK
# ============================================================

stock = get_selected_stock()


# ============================================================
# ANALYZE
# ============================================================

try:

    with st.spinner(
        f"Analyzing momentum for {stock}..."
    ):

        data = analyze_stock(
            stock
        )

except Exception as error:

    st.error(
        str(error)
    )

    st.stop()


if data is None or data.empty:

    st.warning(
        f"No historical data available for {stock}."
    )

    st.stop()


latest = data.iloc[-1]


# ============================================================
# MOMENTUM CALCULATION
# ============================================================

score = momentum_score(
    data
)


status = momentum_status(
    data
)


# ============================================================
# HEADER
# ============================================================

st.subheader(
    f"⚡ Momentum Analysis — {stock}",
    help=get_indicator_tooltip(
        "Momentum"
    ),
)


st.caption(
    "Momentum combines price strength, RSI, MACD, "
    "moving averages and volume confirmation."
)


# ============================================================
# KEY METRICS
# ============================================================

c1, c2, c3 = st.columns(3)


c1.metric(
    "Momentum Score",
    score,
    help=(
        "Momentum score produced by the application's "
        "momentum analysis logic. A higher score indicates "
        "stronger positive momentum according to the model."
    ),
)


c2.metric(
    "Momentum",
    status,
    help=get_indicator_tooltip(
        "Momentum"
    ),
)


rsi_value = latest.get(
    "RSI"
)


c3.metric(
    "RSI",
    (
        f"{float(rsi_value):.2f}"
        if rsi_value is not None
        else "N/A"
    ),
    help=get_indicator_tooltip(
        "RSI"
    ),
)


# ============================================================
# RSI STATUS
# ============================================================

if rsi_value is not None:

    rsi_value = float(
        rsi_value
    )

    if rsi_value >= 70:

        st.warning(
            f"RSI is {rsi_value:.2f}: "
            "momentum is strong but the stock may "
            "become technically extended."
        )

    elif rsi_value <= 30:

        st.info(
            f"RSI is {rsi_value:.2f}: "
            "the stock may be in an oversold area. "
            "A reversal should be confirmed before acting."
        )

    elif rsi_value >= 50:

        st.success(
            f"RSI is {rsi_value:.2f}: "
            "momentum is currently positive."
        )

    else:

        st.info(
            f"RSI is {rsi_value:.2f}: "
            "momentum is currently below the positive "
            "50-level threshold."
        )


# ============================================================
# MOMENTUM INDICATORS
# ============================================================

st.subheader(
    "📈 Momentum Indicators",
    help=get_indicator_tooltip(
        "Momentum"
    ),
)


# ============================================================
# INDICATOR CHART
# ============================================================

chart_columns = [
    column
    for column in [
        "RSI",
        "MACD",
        "MACD_Signal",
    ]
    if column in data.columns
]


if chart_columns:

    st.line_chart(
        data[
            chart_columns
        ]
    )

else:

    st.warning(
        "Momentum indicator columns are not available."
    )


# ============================================================
# INDICATOR SNAPSHOT
# ============================================================

st.subheader(
    "📊 Momentum Snapshot"
)


m1, m2, m3, m4 = st.columns(4)


# RSI
m1.metric(
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
m2.metric(
    "MACD",
    (
        f"{float(latest['MACD']):.4f}"
        if "MACD" in latest
        else "N/A"
    ),
    help=get_indicator_tooltip(
        "MACD"
    ),
)


# MACD Signal
m3.metric(
    "MACD Signal",
    (
        f"{float(latest['MACD_Signal']):.4f}"
        if "MACD_Signal" in latest
        else "N/A"
    ),
    help=get_indicator_tooltip(
        "MACD"
    ),
)


# MACD Histogram
m4.metric(
    "MACD Histogram",
    (
        f"{float(latest['MACD_Histogram']):.4f}"
        if "MACD_Histogram" in latest
        else "N/A"
    ),
    help=get_indicator_tooltip(
        "MACD Histogram"
    ),
)


# ============================================================
# MOMENTUM INTERPRETATION
# ============================================================

st.subheader(
    "🔎 Momentum Interpretation"
)


macd_value = latest.get(
    "MACD"
)

macd_signal = latest.get(
    "MACD_Signal"
)

ema20 = latest.get(
    "EMA_20"
)

close_price = latest.get(
    "Close"
)

volume_ratio = latest.get(
    "Volume_Ratio"
)


interpretation = []


if rsi_value is not None:

    if float(rsi_value) > 50:

        interpretation.append(
            "✅ RSI is above 50, supporting positive momentum."
        )

    else:

        interpretation.append(
            "⚠️ RSI is below 50, indicating weaker momentum."
        )


if (
    macd_value is not None
    and macd_signal is not None
):

    if float(macd_value) > float(macd_signal):

        interpretation.append(
            "✅ MACD is above its Signal line, supporting bullish momentum."
        )

    else:

        interpretation.append(
            "⚠️ MACD is below its Signal line, indicating bearish momentum."
        )


if (
    ema20 is not None
    and close_price is not None
):

    if float(close_price) > float(ema20):

        interpretation.append(
            "✅ Price is above EMA 20."
        )

    else:

        interpretation.append(
            "⚠️ Price is below EMA 20."
        )


if volume_ratio is not None:

    if float(volume_ratio) >= 1.5:

        interpretation.append(
            "✅ Volume is at least 1.5x the 20-period average."
        )

    else:

        interpretation.append(
            "ℹ️ Volume is below the 1.5x volume-spike threshold."
        )


if interpretation:

    for item in interpretation:

        st.write(
            item
        )

else:

    st.info(
        "No additional momentum interpretation is available."
    )


# ============================================================
# COMPLETE GUIDE
# ============================================================

with st.expander(
    "📚 Momentum Trading Guide"
):

    show_indicator_guide(
        st,
        "Momentum"
    )

    st.markdown(
        "---"
    )

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
        "Volume Ratio"
    )


# ============================================================
# DISCLAIMER
# ============================================================

st.divider()

st.info(
    "⚠️ Momentum indicators identify market conditions; "
    "they do not guarantee future price direction or profit."
)


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()