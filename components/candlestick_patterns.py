import streamlit as st

from utils.tooltips import get_pattern_help


def detect_candlestick_patterns(df):

    patterns = []

    if len(df) < 2:
        return patterns

    current = df.iloc[-1]
    previous = df.iloc[-2]

    body = abs(
        current["close"] -
        current["open"]
    )

    candle_range = (
        current["high"] -
        current["low"]
    )

    upper_wick = (
        current["high"] -
        max(
            current["open"],
            current["close"]
        )
    )

    lower_wick = (
        min(
            current["open"],
            current["close"]
        ) -
        current["low"]
    )

    # --------------------------------------------------------
    # DOJI
    # --------------------------------------------------------

    if candle_range > 0:

        if body <= candle_range * 0.10:

            patterns.append("Doji")

    # --------------------------------------------------------
    # HAMMER
    # --------------------------------------------------------

    if (
        lower_wick >= body * 2
        and upper_wick <= body
    ):

        patterns.append("Hammer")

    # --------------------------------------------------------
    # SHOOTING STAR
    # --------------------------------------------------------

    if (
        upper_wick >= body * 2
        and lower_wick <= body
    ):

        patterns.append("Shooting Star")

    # --------------------------------------------------------
    # BULLISH ENGULFING
    # --------------------------------------------------------

    if (
        current["close"] >
        current["open"]

        and

        previous["close"] <
        previous["open"]

        and

        current["close"] >=
        previous["open"]

        and

        current["open"] <=
        previous["close"]
    ):

        patterns.append(
            "Bullish Engulfing"
        )

    # --------------------------------------------------------
    # BEARISH ENGULFING
    # --------------------------------------------------------

    if (
        current["close"] <
        current["open"]

        and

        previous["close"] >
        previous["open"]

        and

        current["open"] >=
        previous["close"]

        and

        current["close"] <=
        previous["open"]
    ):

        patterns.append(
            "Bearish Engulfing"
        )

    return patterns


def display_candlestick_patterns(df):

    st.subheader("🕯️ Candlestick Patterns")

    patterns = detect_candlestick_patterns(df)

    if not patterns:

        st.info(
            "No major candlestick pattern detected "
            "on the latest candle."
        )

        return

    for pattern in patterns:

        if pattern in [
            "Bullish Engulfing",
            "Hammer",
            "Inverted Hammer",
        ]:

            icon = "🟢"

        elif pattern in [
            "Bearish Engulfing",
            "Shooting Star",
        ]:

            icon = "🔴"

        else:

            icon = "🟡"

        st.markdown(
            f"### {icon} {pattern} ⓘ",
            help=get_pattern_help(pattern)
        )

        with st.expander(
            f"📖 {pattern} — Details"
        ):

            st.markdown(
                get_pattern_help(pattern)
            )