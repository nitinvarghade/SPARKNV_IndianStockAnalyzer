# pages/01_📊_Dashboard.py

import streamlit as st
import pandas as pd

from services.stock_service import (
    analyze_stock,
    calculate_recommendation,
)

from components.navigation import (
    get_selected_stock,
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
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Indian Stock Analyzer - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PAGE CONSTANTS
# ============================================================

CURRENT_PAGE = "pages/01_📊_Dashboard.py"


# ============================================================
# PAGE HEADER
# ============================================================

page_header(
    "📊 Indian Stock Analyzer Dashboard",
    CURRENT_PAGE,
)


# ============================================================
# PAGE NAVIGATION
# ============================================================

show_page_navigation()


# ============================================================
# GET SELECTED STOCK
# ============================================================

selected_stock = get_selected_stock()

if not selected_stock:
    st.warning(
        "Please select a stock symbol."
    )
    st.stop()


# Display clean symbol
display_symbol = (
    selected_stock
    .replace(".NS", "")
    .upper()
)


# ============================================================
# STOCK ANALYSIS
# ============================================================

with st.spinner(
    f"Loading analysis for {display_symbol}..."
):

    try:
        analysis_df = analyze_stock(
            selected_stock
        )

    except Exception as e:

        st.error(
            f"Unable to analyze {display_symbol}."
        )

        st.exception(e)

        st.stop()


# ============================================================
# VALIDATE DATA
# ============================================================

if analysis_df is None:

    st.warning(
        f"No market data available for {display_symbol}."
    )

    st.stop()


if isinstance(
    analysis_df,
    pd.DataFrame,
):

    if analysis_df.empty:

        st.warning(
            f"No market data available for {display_symbol}."
        )

        st.stop()

else:

    st.error(
        "Stock analysis returned an invalid data format."
    )

    st.stop()


# ============================================================
# NORMALIZE COLUMN NAMES
# ============================================================

analysis_df.columns = [
    str(column).strip()
    for column in analysis_df.columns
]


# ============================================================
# LATEST ROW
# ============================================================

latest = analysis_df.iloc[-1]


# ============================================================
# HELPER FUNCTION
# ============================================================

def get_value(
    row,
    column,
    default=None,
):

    if column not in row.index:
        return default

    value = row[column]

    if pd.isna(value):
        return default

    return value


# ============================================================
# PRICE DATA
# ============================================================

close_price = get_value(
    latest,
    "Close",
    0,
)

open_price = get_value(
    latest,
    "Open",
    0,
)

high_price = get_value(
    latest,
    "High",
    0,
)

low_price = get_value(
    latest,
    "Low",
    0,
)

volume = get_value(
    latest,
    "Volume",
    0,
)


# ============================================================
# PRICE CHANGE
# ============================================================

previous_close = None

if len(analysis_df) >= 2:

    previous_close = get_value(
        analysis_df.iloc[-2],
        "Close",
        None,
    )


if (
    previous_close is not None
    and previous_close != 0
):

    price_change = (
        float(close_price)
        - float(previous_close)
    )

    price_change_pct = (
        price_change
        / float(previous_close)
    ) * 100

else:

    price_change = 0
    price_change_pct = 0


# ============================================================
# TECHNICAL INDICATORS
# ============================================================

rsi = get_value(
    latest,
    "RSI",
    None,
)

macd = get_value(
    latest,
    "MACD",
    None,
)

macd_signal = get_value(
    latest,
    "MACD_Signal",
    None,
)

macd_histogram = get_value(
    latest,
    "MACD_Histogram",
    None,
)

sma_20 = get_value(
    latest,
    "SMA_20",
    None,
)

sma_50 = get_value(
    latest,
    "SMA_50",
    None,
)

ema_20 = get_value(
    latest,
    "EMA_20",
    None,
)

ema_50 = get_value(
    latest,
    "EMA_50",
    None,
)

vwap = get_value(
    latest,
    "VWAP",
    None,
)

supertrend = get_value(
    latest,
    "Supertrend",
    None,
)

atr = get_value(
    latest,
    "ATR",
    None,
)

bollinger_upper = get_value(
    latest,
    "BB_Upper",
    None,
)

bollinger_middle = get_value(
    latest,
    "BB_Middle",
    None,
)

bollinger_lower = get_value(
    latest,
    "BB_Lower",
    None,
)

momentum = get_value(
    latest,
    "Momentum",
    None,
)

volume_ratio = get_value(
    latest,
    "Volume_Ratio",
    None,
)


# ============================================================
# RECOMMENDATION
# ============================================================

try:

    recommendation_result = (
        calculate_recommendation(
            analysis_df
        )
    )

except Exception:

    recommendation_result = None


# ============================================================
# NORMALIZE RECOMMENDATION RESULT
# ============================================================

recommendation = "HOLD"
confidence = 0
recommendation_reasons = []


if isinstance(
    recommendation_result,
    dict,
):

    recommendation = str(
        recommendation_result.get(
            "recommendation",
            recommendation_result.get(
                "Recommendation",
                "HOLD",
            ),
        )
    ).upper()

    confidence = (
        recommendation_result.get(
            "confidence",
            recommendation_result.get(
                "Confidence",
                0,
            ),
        )
    )

    recommendation_reasons = (
        recommendation_result.get(
            "reasons",
            recommendation_result.get(
                "Reasons",
                [],
            ),
        )
    )

elif isinstance(
    recommendation_result,
    str,
):

    recommendation = (
        recommendation_result.upper()
    )


# ============================================================
# RECOMMENDATION HEADER
# ============================================================

st.markdown(
    f"""
    <div style="
        padding: 18px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-bottom: 20px;
    ">
        <h2 style="margin:0;">
            {display_symbol}
        </h2>
        <p style="margin-top:6px;">
            Latest market analysis and technical indicators
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# KEY METRICS
# ============================================================

st.subheader("📌 Market Overview")


metric1, metric2, metric3, metric4, metric5 = (
    st.columns(5)
)


with metric1:

    st.metric(
        "Current Price",
        (
            f"₹{float(close_price):,.2f}"
            if close_price is not None
            else "N/A"
        ),
        (
            f"{price_change_pct:+.2f}%"
            if previous_close is not None
            else None
        ),
    )


with metric2:

    st.metric(
        "Open",
        (
            f"₹{float(open_price):,.2f}"
            if open_price is not None
            else "N/A"
        ),
    )


with metric3:

    st.metric(
        "Day High",
        (
            f"₹{float(high_price):,.2f}"
            if high_price is not None
            else "N/A"
        ),
    )


with metric4:

    st.metric(
        "Day Low",
        (
            f"₹{float(low_price):,.2f}"
            if low_price is not None
            else "N/A"
        ),
    )


with metric5:

    if volume is not None:

        try:
            volume_text = (
                f"{float(volume):,.0f}"
            )

        except Exception:
            volume_text = str(volume)

    else:

        volume_text = "N/A"

    st.metric(
        "Volume",
        volume_text,
    )


# ============================================================
# RECOMMENDATION
# ============================================================

st.subheader("🎯 Trading Recommendation")


rec_col1, rec_col2, rec_col3 = (
    st.columns(3)
)


with rec_col1:

    st.metric(
        "Recommendation",
        recommendation,
    )


with rec_col2:

    try:

        confidence_value = float(
            confidence
        )

        if confidence_value <= 1:
            confidence_value *= 100

        confidence_text = (
            f"{confidence_value:.1f}%"
        )

    except Exception:

        confidence_text = str(
            confidence
        )

    st.metric(
        "Confidence",
        confidence_text,
    )


with rec_col3:

    if rsi is not None:

        try:

            if float(rsi) >= 70:
                rsi_status = "Overbought"

            elif float(rsi) <= 30:
                rsi_status = "Oversold"

            else:
                rsi_status = "Neutral"

        except Exception:

            rsi_status = "N/A"

    else:

        rsi_status = "N/A"

    st.metric(
        "RSI Status",
        rsi_status,
    )


# ============================================================
# RECOMMENDATION REASONS
# ============================================================

if recommendation_reasons:

    st.markdown(
        "### 🧠 Recommendation Reasons"
    )

    if isinstance(
        recommendation_reasons,
        (list, tuple),
    ):

        for reason in recommendation_reasons:

            st.write(
                f"• {reason}"
            )

    else:

        st.write(
            recommendation_reasons
        )


# ============================================================
# PRICE CHART
# ============================================================

st.subheader("📈 Price Chart")


chart_type = st.radio(
    "Chart Type",
    [
        "Candlestick",
        "Heikin Ashi",
    ],
    horizontal=True,
    key="dashboard_chart_type",
)


# ============================================================
# CANDLESTICK CHART
# ============================================================

if chart_type == "Candlestick":

    try:

        fig = create_price_chart(
            analysis_df,
            symbol=display_symbol,
        )

        if fig is not None:
            st.plotly_chart(
                fig,
                width="stretch",
            )

        else:

            st.line_chart(
                analysis_df["Close"]
            )

    except Exception:

        st.line_chart(
            analysis_df["Close"]
        )


# ============================================================
# HEIKIN ASHI CHART
# ============================================================

else:

    try:

        heikin_ashi_df = (
            calculate_heikin_ashi(
                analysis_df.copy()
            )
        )

        fig = create_heikin_ashi_chart(
            heikin_ashi_df,
            symbol=display_symbol,
        )

        if fig is not None:

            st.plotly_chart(
                fig,
                width="stretch",
            )

        else:

            st.line_chart(
                heikin_ashi_df[
                    "HA_Close"
                ]
            )

    except Exception as e:

        st.warning(
            "Heikin Ashi chart could not be generated. "
            "Showing closing price instead."
        )

        st.line_chart(
            analysis_df["Close"]
        )


# ============================================================
# TECHNICAL INDICATORS
# ============================================================

st.subheader(
    "📊 Technical Indicators"
)


# ------------------------------------------------------------
# RSI
# ------------------------------------------------------------

show_indicator_guide(
    st,
    "RSI",
)


col1, col2, col3 = st.columns(3)


with col1:

    if rsi is not None:

        try:
            rsi_text = (
                f"{float(rsi):.2f}"
            )
        except Exception:
            rsi_text = str(rsi)

    else:

        rsi_text = "N/A"

    st.metric(
        "RSI",
        rsi_text,
        help=get_indicator_tooltip(
            "RSI"
        ),
    )


with col2:

    if macd is not None:

        try:
            macd_text = (
                f"{float(macd):.2f}"
            )
        except Exception:
            macd_text = str(macd)

    else:

        macd_text = "N/A"

    st.metric(
        "MACD",
        macd_text,
        help=get_indicator_tooltip(
            "MACD"
        ),
    )


with col3:

    if macd_histogram is not None:

        try:
            histogram_text = (
                f"{float(macd_histogram):.2f}"
            )
        except Exception:
            histogram_text = str(
                macd_histogram
            )

    else:

        histogram_text = "N/A"

    st.metric(
        "MACD Histogram",
        histogram_text,
        help=get_indicator_tooltip(
            "MACD Histogram"
        ),
    )


# ============================================================
# MOVING AVERAGES
# ============================================================

st.markdown(
    "### 📐 Moving Averages"
)


ma1, ma2, ma3, ma4 = st.columns(4)


with ma1:

    value = (
        f"₹{float(sma_20):,.2f}"
        if sma_20 is not None
        else "N/A"
    )

    st.metric(
        "SMA 20",
        value,
        help=get_indicator_tooltip(
            "SMA"
        ),
    )


with ma2:

    value = (
        f"₹{float(sma_50):,.2f}"
        if sma_50 is not None
        else "N/A"
    )

    st.metric(
        "SMA 50",
        value,
        help=get_indicator_tooltip(
            "SMA"
        ),
    )


with ma3:

    value = (
        f"₹{float(ema_20):,.2f}"
        if ema_20 is not None
        else "N/A"
    )

    st.metric(
        "EMA 20",
        value,
        help=get_indicator_tooltip(
            "EMA"
        ),
    )


with ma4:

    value = (
        f"₹{float(ema_50):,.2f}"
        if ema_50 is not None
        else "N/A"
    )

    st.metric(
        "EMA 50",
        value,
        help=get_indicator_tooltip(
            "EMA"
        ),
    )


# ============================================================
# VWAP / SUPERTREND / ATR
# ============================================================

st.markdown(
    "### 📈 Trend & Volatility Indicators"
)


indicator1, indicator2, indicator3 = (
    st.columns(3)
)


with indicator1:

    value = (
        f"₹{float(vwap):,.2f}"
        if vwap is not None
        else "N/A"
    )

    st.metric(
        "VWAP",
        value,
        help=get_indicator_tooltip(
            "VWAP"
        ),
    )


with indicator2:

    value = (
        f"₹{float(supertrend):,.2f}"
        if supertrend is not None
        else "N/A"
    )

    st.metric(
        "Supertrend",
        value,
        help=get_indicator_tooltip(
            "Supertrend"
        ),
    )


with indicator3:

    value = (
        f"₹{float(atr):,.2f}"
        if atr is not None
        else "N/A"
    )

    st.metric(
        "ATR",
        value,
        help=get_indicator_tooltip(
            "ATR"
        ),
    )


# ============================================================
# BOLLINGER BANDS
# ============================================================

st.markdown(
    "### 📉 Bollinger Bands"
)


bb1, bb2, bb3 = st.columns(3)


with bb1:

    value = (
        f"₹{float(bollinger_upper):,.2f}"
        if bollinger_upper is not None
        else "N/A"
    )

    st.metric(
        "Upper Band",
        value,
        help=get_indicator_tooltip(
            "Bollinger Bands"
        ),
    )


with bb2:

    value = (
        f"₹{float(bollinger_middle):,.2f}"
        if bollinger_middle is not None
        else "N/A"
    )

    st.metric(
        "Middle Band",
        value,
        help=get_indicator_tooltip(
            "Bollinger Bands"
        ),
    )


with bb3:

    value = (
        f"₹{float(bollinger_lower):,.2f}"
        if bollinger_lower is not None
        else "N/A"
    )

    st.metric(
        "Lower Band",
        value,
        help=get_indicator_tooltip(
            "Bollinger Bands"
        ),
    )


# ============================================================
# MOMENTUM & VOLUME
# ============================================================

st.markdown(
    "### 🚀 Momentum & Volume"
)


mv1, mv2 = st.columns(2)


with mv1:

    if momentum is not None:

        try:

            momentum_text = (
                f"{float(momentum):.2f}"
            )

        except Exception:

            momentum_text = str(
                momentum
            )

    else:

        momentum_text = "N/A"

    st.metric(
        "Momentum",
        momentum_text,
        help=get_indicator_tooltip(
            "Momentum"
        ),
    )


with mv2:

    if volume_ratio is not None:

        try:

            volume_ratio_text = (
                f"{float(volume_ratio):.2f}x"
            )

        except Exception:

            volume_ratio_text = str(
                volume_ratio
            )

    else:

        volume_ratio_text = "N/A"

    st.metric(
        "Volume Ratio",
        volume_ratio_text,
        help=get_indicator_tooltip(
            "Volume Ratio"
        ),
    )


# ============================================================
# INDICATOR CHARTS
# ============================================================

st.subheader(
    "📊 Indicator Charts"
)


# ------------------------------------------------------------
# RSI CHART
# ------------------------------------------------------------

if "RSI" in analysis_df.columns:

    st.markdown(
        "#### RSI"
    )

    st.line_chart(
        analysis_df[
            ["RSI"]
        ],
        width="stretch",
    )

    st.caption(
        get_indicator_tooltip(
            "RSI"
        )
    )


# ------------------------------------------------------------
# MACD CHART
# ------------------------------------------------------------

macd_columns = [
    column
    for column in [
        "MACD",
        "MACD_Signal",
        "MACD_Histogram",
    ]
    if column in analysis_df.columns
]


if macd_columns:

    st.markdown(
        "#### MACD"
    )

    st.line_chart(
        analysis_df[
            macd_columns
        ],
        width="stretch",
    )

    st.caption(
        get_indicator_tooltip(
            "MACD"
        )
    )


# ------------------------------------------------------------
# MOVING AVERAGES CHART
# ------------------------------------------------------------

ma_columns = [
    column
    for column in [
        "Close",
        "SMA_20",
        "SMA_50",
        "EMA_20",
        "EMA_50",
    ]
    if column in analysis_df.columns
]


if len(ma_columns) > 1:

    st.markdown(
        "#### Moving Averages"
    )

    st.line_chart(
        analysis_df[
            ma_columns
        ],
        width="stretch",
    )

    st.caption(
        get_indicator_tooltip(
            "SMA"
        )
    )


# ============================================================
# VOLUME CHART
# ============================================================

if "Volume" in analysis_df.columns:

    st.markdown(
        "#### Volume"
    )

    st.bar_chart(
        analysis_df[
            ["Volume"]
        ],
        width="stretch",
    )

    st.caption(
        get_indicator_tooltip(
            "Volume"
        )
    )


# ============================================================
# RECENT MARKET DATA
# ============================================================

st.subheader(
    "📋 Recent Market Data"
)


display_columns = [
    column
    for column in [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "RSI",
        "MACD",
        "SMA_20",
        "SMA_50",
        "VWAP",
        "ATR",
        "Momentum",
        "Volume_Ratio",
    ]
    if column in analysis_df.columns
]


if display_columns:

    recent_data = (
        analysis_df[
            display_columns
        ]
        .tail(10)
        .copy()
    )

    st.dataframe(
        recent_data,
        width="stretch",
        hide_index=True,
    )


# ============================================================
# EDUCATIONAL GUIDE
# ============================================================

with st.expander(
    "📚 How to use the Dashboard"
):

    st.markdown(
        """
### 📊 Dashboard Guide

**Current Price**
- Shows the latest available market price.
- The percentage beside the price shows the change from the previous trading session.

**RSI**
- Below 30 → potentially oversold.
- Above 70 → potentially overbought.
- 30–70 → generally neutral.

**MACD**
- MACD above signal → bullish momentum.
- MACD below signal → bearish momentum.
- Histogram shows the strength of the difference.

**Moving Averages**
- Price above moving averages can indicate a stronger trend.
- Price below moving averages can indicate weaker trend conditions.

**VWAP**
- Price above VWAP can indicate intraday bullish strength.
- Price below VWAP can indicate intraday bearish strength.

**Supertrend**
- Price above Supertrend → generally bullish.
- Price below Supertrend → generally bearish.

**ATR**
- Measures market volatility.
- Higher ATR means larger expected price movement.

**Bollinger Bands**
- Helps identify volatility and potential overextension.
- Narrow bands can indicate lower volatility.
- Expanding bands can indicate increasing volatility.

**Volume Ratio**
- Compares current volume with average volume.
- A high ratio can provide confirmation for a price move.

### ⚠️ Important

Technical indicators should not be used individually.

For a stronger trading decision, combine:

**Trend + Momentum + Volume + Price Action + Risk Management**
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    f"Indian Stock Analyzer • "
    f"Selected Stock: {display_symbol} • "
    f"Data source: Yahoo Finance"
)