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
# HELPERS
# ============================================================

def _safe_float(value, default=0.0):
    """
    Safely convert a value to float.
    """

    try:
        if pd.isna(value):
            return default

        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


def _latest_candlestick_pattern(data):
    """
    Return the detected candlestick patterns on
    the latest candle.

    Multiple patterns can be detected simultaneously.
    """

    if (
        data is None
        or data.empty
    ):
        return "None"

    latest = data.iloc[-1]

    patterns = []

    for pattern in PATTERN_COLUMNS:

        if pattern not in data.columns:
            continue

        try:
            detected = bool(
                latest[pattern]
            )
        except Exception:
            detected = False

        if detected:
            patterns.append(
                pattern.replace(
                    "_",
                    " ",
                )
            )

    if not patterns:
        return "None"

    return ", ".join(patterns)


# ============================================================
# ANALYZE STOCK
# ============================================================

def analyze_stock(
    symbol,
    period="6mo",
    interval="1d",
):
    """
    Download and analyze a stock.

    Pipeline:

    1. Market data
    2. Technical indicators
    3. Volume analysis
    4. Candlestick patterns
    """

    data = download_stock_data(
        symbol,
        period,
        interval,
    )

    if data is None or data.empty:
        raise ValueError(
            f"No market data available for {symbol}."
        )

    data = add_technical_indicators(
        data
    )

    data = add_volume_analysis(
        data
    )

    data = detect_candlestick_patterns(
        data
    )

    return data


# ============================================================
# RECOMMENDATION
# ============================================================

def calculate_recommendation(data):
    """
    Calculate technical recommendation.

    Existing scoring model is intentionally preserved.

    Score components:

    Price vs SMA 20       +1 / -1
    Price vs SMA 50       +1 / -1
    RSI                   +1 / -1
    MACD                  +1 / -1
    Supertrend            +2 / -2
    Volume spike          +1

    Recommendation:

    >= 6       STRONG BUY
    >= 3       BUY
    <= -4      STRONG SELL
    <= -2      SELL
    otherwise  HOLD
    """

    if (
        data is None
        or data.empty
    ):
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

    close = _safe_float(
        latest.get(
            "Close",
            0,
        )
    )

    sma_20 = _safe_float(
        latest.get(
            "SMA_20",
            0,
        )
    )

    if close > sma_20:

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

    sma_50 = _safe_float(
        latest.get(
            "SMA_50",
            0,
        )
    )

    if close > sma_50:

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

    rsi = _safe_float(
        latest.get(
            "RSI",
            50,
        ),
        50,
    )

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

    else:

        reasons.append(
            "RSI is neutral"
        )

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

    macd = _safe_float(
        latest.get(
            "MACD",
            0,
        )
    )

    macd_signal = _safe_float(
        latest.get(
            "MACD_Signal",
            0,
        )
    )

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

    supertrend_direction = _safe_float(
        latest.get(
            "Supertrend_Direction",
            0,
        )
    )

    if supertrend_direction == 1:

        score += 2

        reasons.append(
            "Supertrend bullish"
        )

    else:

        score -= 2

        reasons.append(
            "Supertrend bearish"
        )

    # --------------------------------------------------------
    # VOLUME
    # --------------------------------------------------------

    volume_ratio = _safe_float(
        latest.get(
            "Volume_Ratio",
            0,
        )
    )

    if volume_ratio >= 1.5:

        score += 1

        reasons.append(
            "Volume spike detected"
        )

    # --------------------------------------------------------
    # FINAL RECOMMENDATION
    # --------------------------------------------------------

    if score >= 6:

        recommendation = "STRONG BUY"

    elif score >= 3:

        recommendation = "BUY"

    elif score <= -4:

        recommendation = "STRONG SELL"

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
    """
    Return a compact summary used by
    Stock Comparison.
    """

    data = analyze_stock(
        symbol
    )

    if (
        data is None
        or data.empty
    ):
        raise ValueError(
            f"No analysis data available for {symbol}."
        )

    (
        recommendation,
        confidence,
        reasons,
    ) = calculate_recommendation(
        data
    )

    latest = data.iloc[-1]

    return {
        "Symbol": symbol,

        "Price": _safe_float(
            latest.get(
                "Close",
                0,
            )
        ),

        "Recommendation": recommendation,

        "Confidence": confidence,

        "Trend": calculate_daily_trend(
            data
        ),

        "RSI": _safe_float(
            latest.get(
                "RSI",
                0,
            )
        ),

        "MomentumScore": momentum_score(
            data
        ),

        "VolumeRatio": _safe_float(
            latest.get(
                "Volume_Ratio",
                0,
            )
        ),

        "Volatility": calculate_volatility(
            data
        ),

        "Candlestick": _latest_candlestick_pattern(
            data
        ),

        "Reasons": reasons,
    }