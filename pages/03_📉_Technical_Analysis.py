# pages/03_📉_Technical_Analysis.py

import streamlit as st

from components.navigation import (
    get_selected_stock,
    page_header,
    show_page_navigation,
)

from services.stock_service import (
    analyze_stock,
)


CURRENT_PAGE = (
    "pages/03_📉_Technical_Analysis.py"
)


page_header(
    "📉 Technical Analysis",
    CURRENT_PAGE
)


stock = get_selected_stock()


data = analyze_stock(
    stock
)


latest = data.iloc[-1]


# ============================================================
# INDICATOR
# ============================================================

indicator = st.selectbox(
    "Technical Indicator",
    [
        "RSI",
        "MACD",
        "Bollinger Bands",
        "Moving Averages",
        "VWAP",
        "Supertrend",
        "ATR",
    ],
)


# ============================================================
# RSI
# ============================================================

if indicator == "RSI":

    st.metric(
        "RSI",
        f"{latest['RSI']:.2f}"
    )

    st.line_chart(
        data["RSI"]
    )

    with st.expander(
        "ℹ️ RSI — Usage & Buy/Sell Guide"
    ):

        st.markdown(
            """
### RSI

RSI measures momentum.

**Below 30**
- Potentially oversold
- Possible reversal area
- Do not buy automatically

**30–50**
- Weak momentum

**50–70**
- Positive momentum

**Above 70**
- Potentially overbought
- Avoid chasing extended moves

### Potential Buy Confirmation

Consider RSI together with:
- Price above VWAP
- Bullish trend
- Positive MACD
- Volume confirmation

### Potential Sell Confirmation

Consider:
- RSI falling below 50
- MACD bearish crossover
- Price below VWAP
- Weak volume
"""
        )


# ============================================================
# MACD
# ============================================================

elif indicator == "MACD":

    st.line_chart(
        data[
            [
                "MACD",
                "MACD_Signal",
            ]
        ]
    )

    with st.expander(
        "ℹ️ MACD — Usage"
    ):

        st.markdown(
            """
### MACD

MACD measures momentum and trend.

**Bullish**
- MACD above Signal
- Histogram positive
- Price confirming the move

**Bearish**
- MACD below Signal
- Histogram negative

A MACD signal becomes stronger when
confirmed by trend and volume.
"""
        )


# ============================================================
# BOLLINGER
# ============================================================

elif indicator == "Bollinger Bands":

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
        "ℹ️ Bollinger Bands — Usage"
    ):

        st.markdown(
            """
### Bollinger Bands

Bollinger Bands measure price volatility.

**Price near lower band**
- Possible oversold condition

**Price near upper band**
- Possible overbought condition

**Band squeeze**
- Low volatility
- May precede a large move

Do not treat touching a band alone
as a Buy/Sell signal.
"""
        )


# ============================================================
# MOVING AVERAGE
# ============================================================

elif indicator == "Moving Averages":

    st.line_chart(
        data[
            [
                "Close",
                "SMA_20",
                "SMA_50",
                "SMA_200",
                "EMA_20",
            ]
        ]
    )

    with st.expander(
        "ℹ️ Moving Average — Usage"
    ):

        st.markdown(
            """
### Moving Averages

Common interpretation:

**Price > SMA 20 > SMA 50**
→ bullish structure

**Price < SMA 20 < SMA 50**
→ bearish structure

SMA 200 is commonly used for
longer-term trend analysis.
"""
        )


# ============================================================
# VWAP
# ============================================================

elif indicator == "VWAP":

    st.line_chart(
        data[
            [
                "Close",
                "VWAP",
            ]
        ]
    )

    with st.expander(
        "ℹ️ VWAP — Intraday Usage"
    ):

        st.markdown(
            """
### VWAP

VWAP = Volume Weighted Average Price.

For intraday trading:

**Price above VWAP**
→ bullish bias

**Price below VWAP**
→ bearish bias

Potential long setup:
- Price above VWAP
- Positive momentum
- Volume confirmation

Potential short setup:
- Price below VWAP
- Negative momentum
- Volume confirmation
"""
        )


# ============================================================
# SUPERTREND
# ============================================================

elif indicator == "Supertrend":

    st.line_chart(
        data[
            [
                "Close",
                "Supertrend",
            ]
        ]
    )

    with st.expander(
        "ℹ️ Supertrend — Usage"
    ):

        st.markdown(
            """
### Supertrend

Supertrend follows the direction of price.

**Bullish**
- Supertrend below price

**Bearish**
- Supertrend above price

Potential Buy:
- Supertrend turns bullish
- Price above VWAP/SMA
- Momentum confirms

Potential Sell:
- Supertrend turns bearish
- Price below major averages
"""
        )


# ============================================================
# ATR
# ============================================================

elif indicator == "ATR":

    st.line_chart(
        data["ATR"]
    )

    with st.expander(
        "ℹ️ ATR — Usage"
    ):

        st.markdown(
            """
### ATR

ATR measures volatility, not direction.

Higher ATR:
- Larger price movement
- Wider stop-loss may be required

Lower ATR:
- Smaller price movement

ATR can be useful for determining
position size and stop-loss distance.
"""
        )


st.divider()

show_page_navigation()