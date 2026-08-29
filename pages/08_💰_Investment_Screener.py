# pages/08_💰_Investment_Screener.py

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
    get_trading_guide,
)


CURRENT_PAGE = (
    "pages/08_💰_Investment_Screener.py"
)


# ============================================================
# HEADER
# ============================================================

page_header(
    "💰 Investment Screener",
    CURRENT_PAGE
)


st.caption(
    "Educational stock screening using technical indicators."
)


# ============================================================
# STOCK LIST
# ============================================================

DEFAULT_STOCKS = [
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


stocks = st.multiselect(
    "Select stocks to screen",
    DEFAULT_STOCKS,
    default=DEFAULT_STOCKS[:5],
)


# ============================================================
# INVESTMENT TYPE
# ============================================================

investment_type = st.radio(
    "Investment Type",
    [
        "Intraday",
        "Swing",
        "Long Term",
    ],
    horizontal=True,
)


# ============================================================
# SCREEN
# ============================================================

if st.button(
    "🔍 Run Investment Screener",
    use_container_width=True,
):

    if not stocks:

        st.warning(
            "Please select at least one stock."
        )

        st.stop()


    results = []


    progress = st.progress(0)


    for index, stock in enumerate(stocks):

        try:

            data = analyze_stock(stock)

            if data is None or data.empty:
                continue


            latest = data.iloc[-1]


            def value(
                column,
                default=None
            ):

                if column not in data.columns:
                    return default

                result = latest[column]

                if pd.isna(result):
                    return default

                return result


            close = value(
                "Close",
                0
            )

            rsi = value(
                "RSI"
            )

            macd = value(
                "MACD"
            )

            macd_signal = value(
                "MACD_Signal"
            )

            sma20 = value(
                "SMA_20"
            )

            sma50 = value(
                "SMA_50"
            )

            sma200 = value(
                "SMA_200"
            )

            ema20 = value(
                "EMA_20"
            )

            supertrend = value(
                "Supertrend"
            )

            volume = value(
                "Volume",
                0
            )

            volume_ratio = value(
                "Volume_Ratio"
            )

            atr = value(
                "ATR"
            )

            vwap = value(
                "VWAP"
            )


            # =================================================
            # SCORING
            # =================================================

            score = 0


            # RSI
            if rsi is not None:

                if 50 <= rsi <= 70:
                    score += 1

                elif rsi > 70:
                    score += 0

                elif rsi < 30:
                    score -= 1


            # MACD
            if (
                macd is not None
                and macd_signal is not None
            ):

                if macd > macd_signal:
                    score += 1
                else:
                    score -= 1


            # SMA trend
            if (
                close
                and sma20 is not None
                and sma50 is not None
            ):

                if (
                    close > sma20
                    and sma20 > sma50
                ):
                    score += 1

                elif (
                    close < sma20
                    and sma20 < sma50
                ):
                    score -= 1


            # SMA 200
            if (
                close
                and sma200 is not None
            ):

                if close > sma200:
                    score += 1

                else:
                    score -= 1


            # EMA
            if (
                close
                and ema20 is not None
            ):

                if close > ema20:
                    score += 1

                else:
                    score -= 1


            # Supertrend
            if (
                close
                and supertrend is not None
            ):

                if close > supertrend:
                    score += 1

                else:
                    score -= 1


            # Volume
            if (
                volume_ratio is not None
                and volume_ratio >= 1.5
            ):

                score += 1


            # =================================================
            # CLASSIFICATION
            # =================================================

            if score >= 4:

                recommendation = "🟢 Bullish"

            elif score <= -3:

                recommendation = "🔴 Bearish"

            else:

                recommendation = "🟡 Neutral"


            results.append(
                {
                    "Stock": stock,
                    "Price": close,
                    "RSI": rsi,
                    "MACD": macd,
                    "MACD Signal": macd_signal,
                    "SMA 20": sma20,
                    "SMA 50": sma50,
                    "SMA 200": sma200,
                    "EMA 20": ema20,
                    "Supertrend": supertrend,
                    "Volume": volume,
                    "Volume Ratio": volume_ratio,
                    "ATR": atr,
                    "VWAP": vwap,
                    "Score": score,
                    "Recommendation": recommendation,
                }
            )


        except Exception as e:

            st.warning(
                f"{stock}: {e}"
            )


        progress.progress(
            (index + 1) / len(stocks)
        )


    progress.empty()


    # =========================================================
    # RESULTS
    # =========================================================

    if not results:

        st.warning(
            "No stock analysis results available."
        )

        st.stop()


    result_df = pd.DataFrame(
        results
    )


    result_df = result_df.sort_values(
        "Score",
        ascending=False
    )


    st.session_state[
        "investment_screener_results"
    ] = result_df


# ============================================================
# DISPLAY SAVED RESULTS
# ============================================================

if (
    "investment_screener_results"
    in st.session_state
):

    result_df = st.session_state[
        "investment_screener_results"
    ]


    # ========================================================
    # SUMMARY
    # ========================================================

    st.subheader(
        f"📊 {investment_type} Screening Results"
    )


    bullish_count = len(
        result_df[
            result_df["Score"] >= 4
        ]
    )


    bearish_count = len(
        result_df[
            result_df["Score"] <= -3
        ]
    )


    neutral_count = (
        len(result_df)
        - bullish_count
        - bearish_count
    )


    c1, c2, c3 = st.columns(3)


    c1.metric(
        "🟢 Bullish",
        bullish_count,
        help=(
            "Stocks whose combined technical score "
            "meets the bullish threshold."
        )
    )


    c2.metric(
        "🟡 Neutral",
        neutral_count,
        help=(
            "Stocks where the technical indicators "
            "do not provide a strong directional agreement."
        )
    )


    c3.metric(
        "🔴 Bearish",
        bearish_count,
        help=(
            "Stocks whose combined technical score "
            "meets the bearish threshold."
        )
    )


    # ========================================================
    # TABLE
    # ========================================================

    st.subheader(
        "📋 Ranked Stocks"
    )


    display_columns = [
        "Stock",
        "Price",
        "RSI",
        "MACD",
        "SMA 20",
        "SMA 50",
        "EMA 20",
        "Supertrend",
        "Volume Ratio",
        "Score",
        "Recommendation",
    ]


    display_columns = [
        column
        for column in display_columns
        if column in result_df.columns
    ]


    st.dataframe(
        result_df[
            display_columns
        ],
        use_container_width=True,
        hide_index=True,
    )


    # ========================================================
    # SELECT STOCK
    # ========================================================

    st.subheader(
        "🔎 Study Selected Stock"
    )


    selected_stock = st.selectbox(
        "Select stock",
        result_df["Stock"].tolist(),
    )


    selected = result_df[
        result_df["Stock"]
        == selected_stock
    ].iloc[0]


    # ========================================================
    # SELECTED STOCK METRICS
    # ========================================================

    st.markdown(
        f"### {selected_stock}"
    )


    c1, c2, c3, c4 = st.columns(4)


    c1.metric(
        "Price",
        (
            f"₹{selected['Price']:,.2f}"
            if pd.notna(selected["Price"])
            else "N/A"
        ),
        help=(
            "Latest available closing price."
        )
    )


    c2.metric(
        "RSI",
        (
            f"{selected['RSI']:.2f}"
            if pd.notna(selected["RSI"])
            else "N/A"
        ),
        help=get_indicator_tooltip("RSI")
    )


    c3.metric(
        "MACD",
        (
            f"{selected['MACD']:.2f}"
            if pd.notna(selected["MACD"])
            else "N/A"
        ),
        help=get_indicator_tooltip("MACD")
    )


    c4.metric(
        "Volume Ratio",
        (
            f"{selected['Volume Ratio']:.2f}x"
            if pd.notna(
                selected["Volume Ratio"]
            )
            else "N/A"
        ),
        help=get_indicator_tooltip(
            "Volume Ratio"
        )
    )


    # ========================================================
    # SECONDARY METRICS
    # ========================================================

    c1, c2, c3, c4 = st.columns(4)


    c1.metric(
        "SMA 20",
        (
            f"₹{selected['SMA 20']:,.2f}"
            if pd.notna(selected["SMA 20"])
            else "N/A"
        ),
        help=get_indicator_tooltip("SMA")
    )


    c2.metric(
        "SMA 50",
        (
            f"₹{selected['SMA 50']:,.2f}"
            if pd.notna(selected["SMA 50"])
            else "N/A"
        ),
        help=get_indicator_tooltip("SMA")
    )


    c3.metric(
        "EMA 20",
        (
            f"₹{selected['EMA 20']:,.2f}"
            if pd.notna(selected["EMA 20"])
            else "N/A"
        ),
        help=get_indicator_tooltip("EMA")
    )


    c4.metric(
        "ATR",
        (
            f"{selected['ATR']:.2f}"
            if pd.notna(selected["ATR"])
            else "N/A"
        ),
        help=get_indicator_tooltip("ATR")
    )


    # ========================================================
    # TECHNICAL STUDY GUIDE
    # ========================================================

    st.divider()

    with st.expander(
        "📚 Investment Screener — Technical Indicator Study Guide"
    ):

        st.info(
            "The screener score is an educational technical "
            "screen. It should not be interpreted as a "
            "guaranteed probability of profit."
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


        with st.expander("📖 Supertrend"):
            show_indicator_guide(
                st,
                "Supertrend"
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


        with st.expander("📖 ATR"):
            show_indicator_guide(
                st,
                "ATR"
            )


        with st.expander("📖 VWAP"):
            show_indicator_guide(
                st,
                "VWAP"
            )


    # ========================================================
    # BUY / SELL / HOLD GUIDE
    # ========================================================

    with st.expander(
        "🎯 How to Study the Screener Recommendation"
    ):

        tab1, tab2, tab3 = st.tabs(
            [
                "🟢 Bullish",
                "🔴 Bearish",
                "🟡 Neutral",
            ]
        )


        with tab1:

            st.markdown(
                get_trading_guide("BUY")
            )


        with tab2:

            st.markdown(
                get_trading_guide("SELL")
            )


        with tab3:

            st.markdown(
                get_trading_guide("HOLD")
            )


    # ========================================================
    # RISK GUIDE
    # ========================================================

    with st.expander(
        "⚠️ Risk Management"
    ):

        st.markdown(
            get_trading_guide("RISK")
        )


# ============================================================
# NAVIGATION
# ============================================================

st.divider()

show_page_navigation()