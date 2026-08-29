# services/stock_service.py

import pandas as pd

from services.market_data import (
    download_stock_data,
)

from analytics.technical_indicators import (
    add_technical_indicators,
)

from analytics.volume_analysis import (
    add_volume_analysis,
)

from analytics.candlestick_patterns import (
    detect_candlestick_patterns,
    PATTERN_COLUMNS,
)


# ============================================================
# ANALYZE STOCK
# ============================================================

def analyze_stock(
    symbol,
    period="6mo",
    interval="1d",
):

    data = download_stock_data(
        symbol,
        period,
        interval,
    )

    if data is None or data.empty:
        return pd.DataFrame()

    # --------------------------------------------------------
    # Technical indicators
    # --------------------------------------------------------

    data = add_technical_indicators(
        data
    )

    # --------------------------------------------------------
    # Volume analysis
    # --------------------------------------------------------

    data = add_volume_analysis(
        data
    )

    # --------------------------------------------------------
    # Candlestick patterns
    # --------------------------------------------------------

    try:

        data = detect_candlestick_patterns(
            data
        )

    except Exception:

        # technical_indicators already creates
        # a Candlestick column
        pass

    return data


# ============================================================
# LATEST CANDLESTICK PATTERNS
# ============================================================

def get_latest_candlestick_patterns(
    data,
):

    if data is None or data.empty:
        return []

    latest = data.iloc[-1]

    patterns = []

    # Existing boolean-pattern implementation
    for column in PATTERN_COLUMNS:

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

    # Existing text-based implementation
    if "Candlestick" in data.columns:

        value = latest[
            "Candlestick"
        ]

        if (
            pd.notna(value)
            and str(value) not in [
                "",
                "None",
                "nan",
            ]
        ):

            text = str(value)

            if text not in patterns:
                patterns.append(
                    text
                )

    return patterns


def get_latest_candlestick_text(
    data,
):

    patterns = (
        get_latest_candlestick_patterns(
            data
        )
    )

    if not patterns:
        return "None"

    return ", ".join(
        patterns
    )


# ============================================================
# RECOMMENDATION
# ============================================================

def calculate_recommendation(
    data,
):

    if data is None or data.empty:

        return (
            "HOLD",
            0,
            [],
        )

    latest = data.iloc[-1]

    score = 0
    reasons = []

    # --------------------------------------------------------
    # SMA 20
    # --------------------------------------------------------

    if (
        "SMA_20" in data.columns
        and pd.notna(
            latest["SMA_20"]
        )
    ):

        if (
            latest["Close"]
            >
            latest["SMA_20"]
        ):

            score += 1

            reasons.append(
                "Price above SMA 20"
            )

        else:

            score -= 1

            reasons.append(
                "Price below SMA 20"
            )

    # --------------------------------------------------------
    # SMA 50
    # --------------------------------------------------------

    if (
        "SMA_50" in data.columns
        and pd.notna(
            latest["SMA_50"]
        )
    ):

        if (
            latest["Close"]
            >
            latest["SMA_50"]
        ):

            score += 1

            reasons.append(
                "Price above SMA 50"
            )

        else:

            score -= 1

            reasons.append(
                "Price below SMA 50"
            )

    # --------------------------------------------------------
    # SMA 200
    # --------------------------------------------------------

    if (
        "SMA_200" in data.columns
        and pd.notna(
            latest["SMA_200"]
        )
    ):

        if (
            latest["Close"]
            >
            latest["SMA_200"]
        ):

            score += 1

            reasons.append(
                "Price above SMA 200"
            )

        else:

            score -= 1

            reasons.append(
                "Price below SMA 200"
            )

    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------

    if (
        "RSI" in data.columns
        and pd.notna(
            latest["RSI"]
        )
    ):

        rsi = float(
            latest["RSI"]
        )

        if rsi >= 55:

            score += 1

            reasons.append(
                f"RSI positive at {rsi:.1f}"
            )

        elif rsi <= 45:

            score -= 1

            reasons.append(
                f"RSI weak at {rsi:.1f}"
            )

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

    if (
        "MACD" in data.columns
        and "MACD_Signal" in data.columns
    ):

        macd = latest["MACD"]
        signal = latest["MACD_Signal"]

        if (
            pd.notna(macd)
            and pd.notna(signal)
        ):

            if macd > signal:

                score += 1

                reasons.append(
                    "MACD above Signal"
                )

            else:

                score -= 1

                reasons.append(
                    "MACD below Signal"
                )

    # --------------------------------------------------------
    # Supertrend
    # --------------------------------------------------------

    if (
        "Supertrend_Direction"
        in data.columns
    ):

        direction = latest[
            "Supertrend_Direction"
        ]

        if direction == 1:

            score += 1

            reasons.append(
                "Supertrend bullish"
            )

        elif direction == -1:

            score -= 1

            reasons.append(
                "Supertrend bearish"
            )

    # --------------------------------------------------------
    # VWAP
    # --------------------------------------------------------

    if "VWAP" in data.columns:

        vwap = latest["VWAP"]

        if (
            pd.notna(vwap)
        ):

            if (
                latest["Close"]
                >
                vwap
            ):

                score += 1

                reasons.append(
                    "Price above VWAP"
                )

            else:

                score -= 1

                reasons.append(
                    "Price below VWAP"
                )

    # --------------------------------------------------------
    # Volume
    # --------------------------------------------------------

    if "Volume_Ratio" in data.columns:

        ratio = latest[
            "Volume_Ratio"
        ]

        if (
            pd.notna(ratio)
            and ratio >= 1.5
        ):

            if latest["Close"] > 0:

                reasons.append(
                    f"Volume spike {ratio:.2f}x"
                )

                # Volume confirms direction
                if len(data) >= 2:

                    previous_close = (
                        data["Close"]
                        .iloc[-2]
                    )

                    if (
                        latest["Close"]
                        >
                        previous_close
                    ):

                        score += 1

                    else:

                        score -= 1

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    max_score = 9

    confidence = (
        abs(score)
        /
        max_score
        *
        100
    )

    if score >= 5:

        recommendation = "STRONG BUY"

    elif score >= 2:

        recommendation = "BUY"

    elif score <= -5:

        recommendation = "STRONG SELL"

    elif score <= -2:

        recommendation = "SELL"

    else:

        recommendation = "HOLD"

    return (
        recommendation,
        min(confidence, 100),
        reasons,
    )