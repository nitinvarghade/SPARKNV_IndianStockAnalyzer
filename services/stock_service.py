# services/stock_service.py

import pandas as pd

from services.market_data import (
    download_stock_data,
)

from analytics.technical_indicators import (
    add_technical_indicators,
)

from analytics.trend_analysis import (
    calculate_daily_trend,
)

from analytics.momentum import (
    momentum_score,
)

from analytics.volume_analysis import (
    add_volume_analysis,
)

from analytics.volatility import (
    calculate_volatility,
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

    data = detect_candlestick_patterns(
        data
    )

    return data


# ============================================================
# GET LATEST CANDLESTICK PATTERNS
# ============================================================

def get_latest_candlestick_patterns(
    data,
):

    if data is None or data.empty:
        return []

    latest = data.iloc[-1]

    patterns = []

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
    # PRICE VS SMA 20
    # --------------------------------------------------------

    if (
        "SMA_20" in data.columns
        and
        pd.notna(
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
    # PRICE VS SMA 50
    # --------------------------------------------------------

    if (
        "SMA_50" in data.columns
        and
        pd.notna(
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
    # RSI
    # --------------------------------------------------------

    rsi = latest.get(
        "RSI",
        50,
    )

    if pd.notna(rsi):

        if 50 <= rsi <= 70:

            score += 1

            reasons.append(
                "RSI supports positive momentum"
            )

        elif rsi < 30:

            score += 1

            reasons.append(
                "RSI indicates oversold condition"
            )

        elif rsi > 75:

            score -= 1

            reasons.append(
                "RSI indicates overbought condition"
            )

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

    macd = latest.get(
        "MACD",
        None,
    )

    macd_signal = latest.get(
        "MACD_Signal",
        None,
    )

    if (
        macd is not None
        and
        macd_signal is not None
        and
        pd.notna(macd)
        and
        pd.notna(macd_signal)
    ):

        if macd > macd_signal:

            score += 1

            reasons.append(
                "MACD bullish"
            )

        else:

            score -= 1

            reasons.append(
                "MACD bearish"
            )

    # --------------------------------------------------------
    # SUPERTREND
    # --------------------------------------------------------

    supertrend = latest.get(
        "Supertrend_Direction",
        0,
    )

    if pd.notna(supertrend):

        if supertrend == 1:

            score += 2

            reasons.append(
                "Supertrend bullish"
            )

        elif supertrend == -1:

            score -= 2

            reasons.append(
                "Supertrend bearish"
            )

    # --------------------------------------------------------
    # VOLUME
    # --------------------------------------------------------

    volume_ratio = latest.get(
        "Volume_Ratio",
        0,
    )

    if (
        pd.notna(volume_ratio)
        and
        volume_ratio >= 1.5
    ):

        score += 1

        reasons.append(
            "Volume spike detected"
        )

    # --------------------------------------------------------
    # CANDLESTICK CONFIRMATION
    # --------------------------------------------------------

    bullish_patterns = {
        "Bullish_Engulfing",
        "Bullish_Harami",
        "Hammer",
        "Inverted_Hammer",
        "Morning_Star",
        "Piercing_Pattern",
        "Three_White_Soldiers",
        "Bullish_Marubozu",
    }

    bearish_patterns = {
        "Bearish_Engulfing",
        "Bearish_Harami",
        "Shooting_Star",
        "Evening_Star",
        "Dark_Cloud_Cover",
        "Three_Black_Crows",
        "Bearish_Marubozu",
    }

    detected_patterns = (
        get_latest_candlestick_patterns(
            data
        )
    )

    detected_columns = {
        pattern.replace(
            " ",
            "_",
        )
        for pattern in detected_patterns
    }

    bullish_detected = (
        detected_columns
        &
        bullish_patterns
    )

    bearish_detected = (
        detected_columns
        &
        bearish_patterns
    )

    if bullish_detected:

        score += 1

        reasons.append(
            "Bullish candlestick confirmation: "
            + ", ".join(
                p.replace(
                    "_",
                    " ",
                )
                for p in bullish_detected
            )
        )

    if bearish_detected:

        score -= 1

        reasons.append(
            "Bearish candlestick confirmation: "
            + ", ".join(
                p.replace(
                    "_",
                    " ",
                )
                for p in bearish_detected
            )
        )

    # --------------------------------------------------------
    # FINAL RECOMMENDATION
    # --------------------------------------------------------

    if score >= 6:

        recommendation = (
            "STRONG BUY"
        )

    elif score >= 3:

        recommendation = "BUY"

    elif score <= -4:

        recommendation = (
            "STRONG SELL"
        )

    elif score <= -2:

        recommendation = "SELL"

    else:

        recommendation = "HOLD"

    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    confidence = min(
        95,
        max(
            50,
            50 + abs(score) * 7,
        ),
    )

    return (
        recommendation,
        confidence,
        reasons,
    )


# ============================================================
# STOCK SUMMARY
# ============================================================

def get_stock_summary(
    symbol,
):

    data = analyze_stock(
        symbol
    )

    if data is None or data.empty:

        return {
            "Symbol": symbol,
            "Price": 0,
            "Recommendation": "HOLD",
            "Confidence": 0,
            "Trend": "Unknown",
            "RSI": 0,
            "MomentumScore": 0,
            "VolumeRatio": 0,
            "Volatility": 0,
            "Candlestick": "None",
            "Reasons": [],
        }

    (
        recommendation,
        confidence,
        reasons,
    ) = calculate_recommendation(
        data
    )

    latest = data.iloc[-1]

    try:

        trend = calculate_daily_trend(
            data
        )

    except Exception:

        trend = "Unknown"

    try:

        momentum = momentum_score(
            data
        )

    except Exception:

        momentum = 0

    try:

        volatility = calculate_volatility(
            data
        )

    except Exception:

        volatility = 0

    return {
        "Symbol": symbol,

        "Price": float(
            latest.get(
                "Close",
                0,
            )
        ),

        "Recommendation": (
            recommendation
        ),

        "Confidence": (
            confidence
        ),

        "Trend": trend,

        "RSI": float(
            latest.get(
                "RSI",
                0,
            )
        ),

        "MomentumScore": momentum,

        "VolumeRatio": float(
            latest.get(
                "Volume_Ratio",
                0,
            )
        ),

        "Volatility": volatility,

        "Candlestick": (
            get_latest_candlestick_text(
                data
            )
        ),

        "Reasons": reasons,
    }