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
    get_latest_pattern_text,
)


# ============================================================
# HELPERS
# ============================================================

def _safe_float(
    value,
    default=0.0,
):

    try:

        if pd.isna(value):
            return default

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


# ============================================================
# ANALYZE STOCK
# ============================================================

def analyze_stock(
    symbol,
    period="6mo",
    interval="1d",
):
    """
    Complete stock-analysis pipeline.

    Market Data
        ↓
    Technical Indicators
        ↓
    Volume Analysis
        ↓
    Candlestick Patterns
    """

    data = download_stock_data(
        symbol,
        period,
        interval,
    )

    if data is None:
        return pd.DataFrame()

    if data.empty:
        return pd.DataFrame()

    # --------------------------------------------------------
    # TECHNICAL INDICATORS
    # --------------------------------------------------------

    data = add_technical_indicators(
        data
    )

    # --------------------------------------------------------
    # VOLUME
    # --------------------------------------------------------

    data = add_volume_analysis(
        data
    )

    # --------------------------------------------------------
    # CANDLESTICK PATTERNS
    # --------------------------------------------------------

    data = detect_candlestick_patterns(
        data
    )

    return data


# ============================================================
# RECOMMENDATION
# ============================================================

def calculate_recommendation(
    data,
):
    """
    Calculate technical recommendation.

    Score:

    Price > SMA20        +1
    Price > SMA50        +1
    RSI                  +1 / -1
    MACD                 +1 / -1
    Supertrend           +2 / -2
    Volume Spike         +1

    Result:

    >= 6       STRONG BUY
    >= 3       BUY
    -1 to 2    HOLD
    <= -2      SELL
    <= -4      STRONG SELL
    """

    if (
        data is None
        or data.empty
    ):

        return (
            "HOLD",
            50,
            [],
        )

    latest = data.iloc[-1]

    score = 0

    reasons = []

    # ========================================================
    # PRICE / SMA 20
    # ========================================================

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

    if sma_20 > 0:

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

    # ========================================================
    # PRICE / SMA 50
    # ========================================================

    sma_50 = _safe_float(
        latest.get(
            "SMA_50",
            0,
        )
    )

    if sma_50 > 0:

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

    # ========================================================
    # RSI
    # ========================================================

    rsi = _safe_float(
        latest.get(
            "RSI",
            50,
        ),
        50,
    )

    if (
        50 <= rsi <= 70
    ):

        score += 1

        reasons.append(
            "RSI supports bullish momentum"
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
            "RSI neutral"
        )

    # ========================================================
    # MACD
    # ========================================================

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

    # ========================================================
    # SUPERTREND
    # ========================================================

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

    elif supertrend_direction == -1:

        score -= 2

        reasons.append(
            "Supertrend bearish"
        )

    # ========================================================
    # VOLUME
    # ========================================================

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

    # ========================================================
    # RECOMMENDATION
    # ========================================================

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

    # ========================================================
    # CONFIDENCE
    # ========================================================

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
    Compact summary used by
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
            f"No data available for {symbol}"
        )

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

        "Price": _safe_float(
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

        "RSI": _safe_float(
            latest.get(
                "RSI",
                0,
            )
        ),

        "MomentumScore": momentum,

        "VolumeRatio": _safe_float(
            latest.get(
                "Volume_Ratio",
                0,
            )
        ),

        "Volatility": volatility,

        "Candlestick": (
            get_latest_pattern_text(
                data
            )
        ),

        "Reasons": reasons,
    }