import streamlit as st


def chart_controls():

    st.sidebar.markdown("---")
    st.sidebar.header("📊 Chart Settings")

    # ========================================================
    # CHART TYPE
    # ========================================================

    chart_type = st.sidebar.selectbox(
        "Chart Type",
        [
            "Candlestick",
            "Heikin Ashi",
            "OHLC",
            "Line",
            "Area"
        ]
    )

    # ========================================================
    # TIMEFRAME
    # ========================================================

    timeframe = st.sidebar.selectbox(
        "Timeframe",
        [
            "1m",
            "3m",
            "5m",
            "10m",
            "15m",
            "30m",
            "1h",
            "2h",
            "4h",
            "1d",
            "1wk",
            "1mo"
        ],
        index=2
    )

    # ========================================================
    # PRICE STUDIES
    # ========================================================

    st.sidebar.subheader("📈 Price Studies")

    price_studies = {
        "SMA": st.sidebar.checkbox(
            "SMA",
            value=True
        ),

        "EMA": st.sidebar.checkbox(
            "EMA",
            value=True
        ),

        "WMA": st.sidebar.checkbox(
            "WMA"
        ),

        "VWAP": st.sidebar.checkbox(
            "VWAP",
            value=True
        ),

        "Bollinger Bands": st.sidebar.checkbox(
            "Bollinger Bands",
            value=True
        ),

        "Supertrend": st.sidebar.checkbox(
            "Supertrend",
            value=True
        ),

        "Ichimoku Cloud": st.sidebar.checkbox(
            "Ichimoku Cloud"
        ),

        "Parabolic SAR": st.sidebar.checkbox(
            "Parabolic SAR"
        ),

        "Donchian Channel": st.sidebar.checkbox(
            "Donchian Channel"
        ),

        "Keltner Channel": st.sidebar.checkbox(
            "Keltner Channel"
        ),

        "Pivot Points": st.sidebar.checkbox(
            "Pivot Points"
        ),

        "Support Resistance": st.sidebar.checkbox(
            "Support / Resistance"
        ),

        "Fibonacci": st.sidebar.checkbox(
            "Fibonacci Retracement"
        )
    }

    # ========================================================
    # MOMENTUM
    # ========================================================

    st.sidebar.subheader("📉 Momentum")

    momentum = {
        "RSI": st.sidebar.checkbox("RSI"),
        "MACD": st.sidebar.checkbox("MACD"),
        "Stochastic": st.sidebar.checkbox("Stochastic"),
        "Stochastic RSI": st.sidebar.checkbox("Stochastic RSI"),
        "CCI": st.sidebar.checkbox("CCI"),
        "ROC": st.sidebar.checkbox("ROC"),
        "Williams %R": st.sidebar.checkbox("Williams %R"),
        "MFI": st.sidebar.checkbox("MFI"),
        "ADX": st.sidebar.checkbox("ADX"),
        "Momentum": st.sidebar.checkbox("Momentum")
    }

    # ========================================================
    # VOLUME
    # ========================================================

    st.sidebar.subheader("📊 Volume")

    volume = {
        "Volume": st.sidebar.checkbox(
            "Volume",
            value=True
        ),

        "Volume SMA": st.sidebar.checkbox(
            "Volume SMA"
        ),

        "Volume Ratio": st.sidebar.checkbox(
            "Volume Ratio"
        ),

        "OBV": st.sidebar.checkbox(
            "OBV"
        ),

        "CMF": st.sidebar.checkbox(
            "CMF"
        ),

        "A/D": st.sidebar.checkbox(
            "Accumulation / Distribution"
        )
    }

    # ========================================================
    # VOLATILITY
    # ========================================================

    st.sidebar.subheader("〽️ Volatility")

    volatility = {
        "ATR": st.sidebar.checkbox(
            "ATR"
        ),

        "Historical Volatility": st.sidebar.checkbox(
            "Historical Volatility"
        ),

        "BB Width": st.sidebar.checkbox(
            "Bollinger Band Width"
        )
    }

    # ========================================================
    # CANDLESTICK PATTERNS
    # ========================================================

    st.sidebar.subheader("🕯️ Candlestick Patterns")

    patterns = {
        "Doji": st.sidebar.checkbox("Doji"),

        "Hammer": st.sidebar.checkbox("Hammer"),

        "Inverted Hammer": st.sidebar.checkbox(
            "Inverted Hammer"
        ),

        "Shooting Star": st.sidebar.checkbox(
            "Shooting Star"
        ),

        "Bullish Engulfing": st.sidebar.checkbox(
            "Bullish Engulfing"
        ),

        "Bearish Engulfing": st.sidebar.checkbox(
            "Bearish Engulfing"
        ),

        "Bullish Harami": st.sidebar.checkbox(
            "Bullish Harami"
        ),

        "Bearish Harami": st.sidebar.checkbox(
            "Bearish Harami"
        ),

        "Morning Star": st.sidebar.checkbox(
            "Morning Star"
        ),

        "Evening Star": st.sidebar.checkbox(
            "Evening Star"
        ),

        "Piercing Pattern": st.sidebar.checkbox(
            "Piercing Pattern"
        ),

        "Dark Cloud Cover": st.sidebar.checkbox(
            "Dark Cloud Cover"
        ),

        "Marubozu": st.sidebar.checkbox(
            "Marubozu"
        ),

        "Three White Soldiers": st.sidebar.checkbox(
            "Three White Soldiers"
        ),

        "Three Black Crows": st.sidebar.checkbox(
            "Three Black Crows"
        )
    }

    # ========================================================
    # DISPLAY
    # ========================================================

    st.sidebar.subheader("🖥️ Display")

    show_crosshair = st.sidebar.checkbox(
        "Crosshair",
        value=True
    )

    show_volume_panel = st.sidebar.checkbox(
        "Volume Panel",
        value=True
    )

    fullscreen = st.sidebar.checkbox(
        "Large Chart",
        value=False
    )

    return {
        "chart_type": chart_type,
        "timeframe": timeframe,
        "price_studies": price_studies,
        "momentum": momentum,
        "volume": volume,
        "volatility": volatility,
        "patterns": patterns,
        "show_crosshair": show_crosshair,
        "show_volume_panel": show_volume_panel,
        "fullscreen": fullscreen
    }