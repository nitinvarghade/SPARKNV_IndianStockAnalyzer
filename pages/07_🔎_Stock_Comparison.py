# pages/07_🔎_Stock_Comparison.py

import streamlit as st
import pandas as pd

from components.navigation import (
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


CURRENT_PAGE = (
    "pages/07_🔎_Stock_Comparison.py"
)


# ============================================================
# HEADER
# ============================================================

page_header(
    "🔎 Stock Comparison",
    CURRENT_PAGE
)


st.caption(
    "Compare technical indicators of multiple Indian stocks."
)


# ============================================================
# STOCK SELECTION
# ============================================================

available_stocks = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "LT.NS",
    "ITC.NS",
    "BHARTIARTL.NS",
    "AXISBANK.NS",
]


selected_stocks = st.multiselect(
    "Select stocks to compare",
    available_stocks,
    default=[
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
    ],
)


# ============================================================
# LOAD COMPARISON DATA
# ============================================================

if not selected_stocks:

    st.info(
        "Select at least two stocks to compare."
    )

    st.stop()


comparison_rows = []


with st.spinner(
    "Loading stock analysis..."
):

    for stock in selected_stocks:

        try:

            data = analyze_stock(
                stock
            )


            if data is None or data.empty:
                continue


            latest = data.iloc[-1]


            def get_value(
                column,
                default=None
            ):

                if column not in data.columns:
                    return default


                value = latest[column]


                if pd.isna(value):
                    return default


                return value


            comparison_rows.append(
                {
                    "Stock": stock,

                    "Price": get_value(
                        "Close"
                    ),

                    "RSI": get_value(
                        "RSI"
                    ),

                    "MACD": get_value(
                        "MACD"
                    ),

                    "MACD Signal": get_value(
                        "MACD_Signal"
                    ),

                    "SMA 20": get_value(
                        "SMA_20"
                    ),

                    "SMA 50": get_value(
                        "SMA_50"
                    ),

                    "SMA 200": get_value(
                        "SMA_200"
                    ),

                    "EMA 20": get_value(
                        "EMA_20"
                    ),

                    "VWAP": get_value(
                        "VWAP"
                    ),

                    "Supertrend": get_value(
                        "Supertrend"
                    ),

                    "ATR": get_value(
                        "ATR"
                    ),

                    "Volume": get_value(
                        "Volume"
                    ),

                    "Volume Ratio": get_value(
                        "Volume_Ratio"
                    ),
                }
            )


        except Exception as e:

            st.warning(
                f"{stock}: {e}"
            )


# ============================================================
# CHECK RESULTS
# ============================================================

if not comparison_rows:

    st.error(
        "Unable to retrieve analysis for the selected stocks."
    )

    st.stop()


comparison_df = pd.DataFrame(
    comparison_rows
)


# ============================================================
# PRICE COMPARISON
# ============================================================

st.subheader(
    "💰 Price Comparison"
)


price_columns = [
    "Stock",
    "Price",
]


price_display = comparison_df[
    price_columns
].copy()


price_display["Price"] = (
    price_display["Price"]
    .apply(
        lambda x:
        f"₹{x:,.2f}"
        if pd.notna(x)
        else "N/A"
    )
)


st.dataframe(
    price_display,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# TECHNICAL COMPARISON
# ============================================================

st.subheader(
    "📊 Technical Indicator Comparison"
)


technical_columns = [
    "Stock",
    "RSI",
    "MACD",
    "MACD Signal",
    "SMA 20",
    "SMA 50",
    "SMA 200",
    "EMA 20",
    "VWAP",
    "Supertrend",
    "ATR",
    "Volume Ratio",
]


technical_columns = [
    column
    for column in technical_columns
    if column in comparison_df.columns
]


technical_display = comparison_df[
    technical_columns
].copy()


# Format numeric values

for column in technical_display.columns:

    if column == "Stock":
        continue

    technical_display[column] = (
        pd.to_numeric(
            technical_display[column],
            errors="coerce"
        )
        .round(2)
    )


st.dataframe(
    technical_display,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# RSI COMPARISON
# ============================================================

st.subheader(
    "📊 RSI Comparison"
)


rsi_chart = comparison_df[
    ["Stock", "RSI"]
].dropna()


if not rsi_chart.empty:

    rsi_chart = rsi_chart.set_index(
        "Stock"
    )

    st.bar_chart(
        rsi_chart
    )


# ============================================================
# MACD COMPARISON
# ============================================================

st.subheader(
    "📈 MACD Comparison"
)


macd_chart = comparison_df[
    [
        "Stock",
        "MACD",
        "MACD Signal",
    ]
].dropna(
    subset=["MACD"]
)


if not macd_chart.empty:

    macd_chart = macd_chart.set_index(
        "Stock"
    )

    st.bar_chart(
        macd_chart[
            [
                "MACD",
                "MACD Signal",
            ]
        ]
    )


# ============================================================
# VOLUME COMPARISON
# ============================================================

st.subheader(
    "📦 Volume Ratio Comparison"
)


volume_chart = comparison_df[
    [
        "Stock",
        "Volume Ratio",
    ]
].dropna()


if not volume_chart.empty:

    volume_chart = volume_chart.set_index(
        "Stock"
    )

    st.bar_chart(
        volume_chart
    )


# ============================================================
# SELECT STOCK FOR DETAILED STUDY
# ============================================================

st.divider()

st.subheader(
    "🔎 Detailed Technical Study"
)


selected_stock = st.selectbox(
    "Select a stock",
    comparison_df["Stock"].tolist(),
)


selected_row = comparison_df[
    comparison_df["Stock"]
    == selected_stock
].iloc[0]


# ============================================================
# SELECTED STOCK METRICS
# ============================================================

c1, c2, c3, c4 = st.columns(4)


rsi = selected_row["RSI"]
macd = selected_row["MACD"]
sma20 = selected_row["SMA 20"]
ema20 = selected_row["EMA 20"]


c1.metric(
    "RSI",
    (
        f"{rsi:.2f}"
        if pd.notna(rsi)
        else "N/A"
    ),
    help=get_indicator_tooltip(
        "RSI"
    )
)


c2.metric(
    "MACD",
    (
        f"{macd:.2f}"
        if pd.notna(macd)
        else "N/A"
    ),
    help=get_indicator_tooltip(
        "MACD"
    )
)


c3.metric(
    "SMA 20",
    (
        f"₹{sma20:,.2f}"
        if pd.notna(sma20)
        else "N/A"
    ),
    help=get_indicator_tooltip(
        "SMA"
    )
)


c4.metric(
    "EMA 20",
    (
        f"₹{ema20:,.2f}"
        if pd.notna(ema20)
        else "N/A"
    ),
    help=get_indicator_tooltip(
        "EMA"
    )
)


# ============================================================
# SECOND ROW
# ============================================================

c1, c2, c3, c4 = st.columns(4)


vwap = selected_row["VWAP"]
supertrend = selected_row["Supertrend"]
atr = selected_row["ATR"]
volume_ratio = selected_row["Volume Ratio"]


c1.metric(
    "VWAP",
    (
        f"₹{vwap:,.2f}"
        if pd.notna(vwap)
        else "N/A"
    ),
    help=get_indicator_tooltip(
        "VWAP"
    )
)


c2.metric(
    "Supertrend",
    (
        f"₹{supertrend:,.2f}"
        if pd.notna(supertrend)
        else "N/A"
    ),
    help=get_indicator_tooltip(
        "Supertrend"
    )
)


c3.metric(
    "ATR",
    (
        f"{atr:.2f}"
        if pd.notna(atr)
        else "N/A"
    ),
    help=get_indicator_tooltip(
        "ATR"
    )
)


c4.metric(
    "Volume Ratio",
    (
        f"{volume_ratio:.2f}x"
        if pd.notna(volume_ratio)
        else "N/A"
    ),
    help=get_indicator_tooltip(
        "Volume Ratio"
    )
)


# ============================================================
# EDUCATIONAL GUIDE
# ============================================================

st.divider()

with st.expander(
    "📚 Technical Indicators — Study Guide"
):

    st.info(
        "Hover over metrics for quick explanations. "
        "Open the sections below for detailed study."
    )


    with st.expander("📖 RSI"):
        show_indicator_guide(
            st,
            "RSI"
        )


    with st.expander("📖 MACD"):
        show_indicator_guide(
            st,
            "MACD"
        )


    with st.expander("📖 SMA"):
        show_indicator_guide(
            st,
            "SMA"
        )


    with st.expander("📖 EMA"):
        show_indicator_guide(
            st,
            "EMA"
        )


    with st.expander("📖 VWAP"):
        show_indicator_guide(
            st,
            "VWAP"
        )


    with st.expander("📖 Supertrend"):
        show_indicator_guide(
            st,
            "Supertrend"
        )


    with st.expander("📖 ATR"):
        show_indicator_guide(
            st,
            "ATR"
        )


    with st.expander("📖 Volume"):
        show_indicator_guide(
            st,
            "Volume"
        )


    with st.expander("📖 Volume Ratio"):
        show_indicator_guide(
            st,
            "Volume Ratio"
        )


    with st.expander("📖 Bollinger Bands"):
        show_indicator_guide(
            st,
            "Bollinger Bands"
        )


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()