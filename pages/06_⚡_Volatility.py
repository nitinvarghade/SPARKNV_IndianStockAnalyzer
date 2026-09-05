# pages/05_📊_Volume_Analysis.py

import streamlit as st

from components.navigation import (
    get_selected_stock,
    page_header,
    show_page_navigation,
)

from services.stock_service import (
    analyze_stock,
)

from utils.indicator_guide import (
    get_indicator_tooltip,
    show_indicator_guide,
)


# ============================================================
# PAGE
# ============================================================

CURRENT_PAGE = (
    "pages/05_📊_Volume_Analysis.py"
)


page_header(
    "📊 Volume Analysis",
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
        f"Analyzing volume for {stock}..."
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
# VOLUME
# ============================================================

volume = latest.get(
    "Volume",
    0
)


volume_ratio = latest.get(
    "Volume_Ratio",
    0
)


try:

    volume_value = float(
        volume
    )

except Exception:

    volume_value = 0


try:

    volume_ratio_value = float(
        volume_ratio
    )

except Exception:

    volume_ratio_value = 0


# ============================================================
# HEADER
# ============================================================

st.subheader(
    f"📊 Volume Analysis — {stock}",
    help=get_indicator_tooltip(
        "Volume"
    ),
)


st.caption(
    "Volume helps measure market participation and "
    "can confirm price breakouts or breakdowns."
)


# ============================================================
# KEY METRICS
# ============================================================

c1, c2, c3 = st.columns(3)


c1.metric(
    "Volume",
    f"{volume_value:,.0f}",
    help=get_indicator_tooltip(
        "Volume"
    ),
)


c2.metric(
    "Volume / 20D Avg",
    f"{volume_ratio_value:.2f}x",
    help=get_indicator_tooltip(
        "Volume Ratio"
    ),
)


if volume_ratio_value >= 1.5:

    volume_status = "🔥 Volume Spike"

elif volume_ratio_value >= 1.0:

    volume_status = "Normal"

else:

    volume_status = "Below Average"


c3.metric(
    "Volume Status",
    volume_status,
    help=(
        "Volume is classified as a spike when "
        "current volume is at least 1.5 times "
        "the 20-period average."
    ),
)


# ============================================================
# VOLUME INTERPRETATION
# ============================================================

if volume_ratio_value >= 1.5:

    st.success(
        f"🔥 Volume spike detected: "
        f"{volume_ratio_value:.2f}x the 20-period average."
    )

elif volume_ratio_value >= 1.0:

    st.info(
        f"Volume is around or above its average: "
        f"{volume_ratio_value:.2f}x."
    )

else:

    st.warning(
        f"Volume is below its 20-period average: "
        f"{volume_ratio_value:.2f}x."
    )


# ============================================================
# VOLUME CHART
# ============================================================

st.subheader(
    "📊 Volume Chart",
    help=get_indicator_tooltip(
        "Volume"
    ),
)


if "Volume" in data.columns:

    st.bar_chart(
        data["Volume"]
    )

else:

    st.warning(
        "Volume data is not available."
    )


# ============================================================
# VOLUME RATIO CHART
# ============================================================

if "Volume_Ratio" in data.columns:

    st.subheader(
        "📈 Volume Ratio",
        help=get_indicator_tooltip(
            "Volume Ratio"
        ),
    )

    st.line_chart(
        data["Volume_Ratio"]
    )


# ============================================================
# PRICE + VOLUME INTERPRETATION
# ============================================================

st.subheader(
    "🔎 Price + Volume Confirmation"
)


close_price = latest.get(
    "Close"
)

previous_close = (
    data["Close"].iloc[-2]
    if len(data) > 1
    else close_price
)


if (
    close_price is not None
    and previous_close is not None
):

    try:

        price_change = (
            float(close_price)
            - float(previous_close)
        )

    except Exception:

        price_change = 0

else:

    price_change = 0


if (
    volume_ratio_value >= 1.5
    and price_change > 0
):

    st.success(
        "📈 Price is rising with a volume spike. "
        "This can provide stronger bullish confirmation."
    )


elif (
    volume_ratio_value >= 1.5
    and price_change < 0
):

    st.error(
        "📉 Price is falling with a volume spike. "
        "This can provide stronger bearish confirmation."
    )


elif price_change > 0:

    st.info(
        "Price is rising, but volume does not meet "
        "the application's 1.5x volume-spike threshold."
    )


elif price_change < 0:

    st.warning(
        "Price is falling and volume is not showing "
        "a strong spike."
    )


else:

    st.info(
        "Price movement is relatively unchanged."
    )


# ============================================================
# VOLUME RULE
# ============================================================

st.subheader(
    "📏 Volume Rule",
    help=get_indicator_tooltip(
        "Volume Ratio"
    ),
)


rule1, rule2, rule3 = st.columns(3)


rule1.metric(
    "Current Volume",
    f"{volume_value:,.0f}",
    help=get_indicator_tooltip(
        "Volume"
    ),
)


average_volume = (
    volume_value /
    volume_ratio_value
    if volume_ratio_value > 0
    else 0
)


rule2.metric(
    "Estimated 20D Avg",
    (
        f"{average_volume:,.0f}"
        if average_volume
        else "N/A"
    ),
    help=(
        "Approximate average volume implied "
        "by the current Volume Ratio."
    ),
)


rule3.metric(
    "Spike Threshold",
    "1.50x",
    help=(
        "The application considers volume >= 1.5x "
        "the 20-period average to be a volume spike."
    ),
)


# ============================================================
# GUIDE
# ============================================================

with st.expander(
    "📚 Volume & Volume Ratio Guide"
):

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
# TRADING INTERPRETATION
# ============================================================

with st.expander(
    "💡 How to use Volume for confirmation"
):

    st.markdown(
        """
### Potential Bullish Confirmation

Look for:

- Price breakout
- Volume >= 1.5x average
- Positive momentum
- Price above important moving averages
- RSI/MACD confirmation

### Potential Bearish Confirmation

Look for:

- Price breakdown
- Volume >= 1.5x average
- Negative momentum
- Price below important moving averages
- RSI/MACD confirmation

### Important

A volume spike alone does not mean BUY or SELL.

Always combine volume with price action, trend and momentum.
"""
    )


# ============================================================
# DISCLAIMER
# ============================================================

st.divider()

st.info(
    "⚠️ High volume indicates market participation, "
    "not direction by itself. Always confirm volume "
    "with price action and other indicators."
)


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()
