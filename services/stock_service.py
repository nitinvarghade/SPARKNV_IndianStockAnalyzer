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


# ============================================================
# ANALYZE STOCK
# ============================================================

def analyze_stock(
    symbol,
    period="6mo",
    interval="1d"
):

    data = download_stock_data(
        symbol,
        period,
        interval
    )

    data = add_technical_indicators(
        data
    )

    data = add_volume_analysis(
        data
    )

    return data


# ============================================================
# RECOMMENDATION
# ============================================================

def calculate_recommendation(data):

    if data is None or data.empty:

        return (
            "HOLD",
            0,
            []
        )

    latest = data.iloc[-1]

    score = 0

    reasons = []


    # --------------------------------------------------------
    # PRICE VS SMA
    # --------------------------------------------------------

    if latest["Close"] > latest["SMA_20"]:

        score += 1

        reasons.append(
            "Price above SMA 20"
        )

    else:

        score -= 1

        reasons.append(
            "Price below SMA 20"
        )


    if latest["Close"] > latest["SMA_50"]:

        score += 1

        reasons.append(
            "Price above SMA 50"
        )

    else:

        score -= 1


    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------

    rsi = latest["RSI"]


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

    if (
        latest["MACD"]
        >
        latest["MACD_Signal"]
    ):

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

    if latest[
        "Supertrend_Direction"
    ] == 1:

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

    if latest.get(
        "Volume_Ratio",
        0
    ) >= 1.5:

        score += 1

        reasons.append(
            "Volume spike detected"
        )


    # --------------------------------------------------------
    # FINAL
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


    confidence = min(
        95,
        max(
            50,
            50 + abs(score) * 7
        )
    )


    return (
        recommendation,
        confidence,
        reasons
    )


# ============================================================
# STOCK SUMMARY
# ============================================================

def get_stock_summary(
    symbol
):

    data = analyze_stock(
        symbol
    )

    recommendation, confidence, reasons = (
        calculate_recommendation(
            data
        )
    )

    latest = data.iloc[-1]


    return {
        "Symbol": symbol,
        "Price": float(
            latest["Close"]
        ),
        "Recommendation": recommendation,
        "Confidence": confidence,
        "Trend": calculate_daily_trend(
            data
        ),
        "RSI": float(
            latest["RSI"]
        ),
        "MomentumScore": momentum_score(
            data
        ),
        "VolumeRatio": float(
            latest.get(
                "Volume_Ratio",
                0
            )
        ),
        "Volatility": calculate_volatility(
            data
        ),
        "Candlestick": latest.get(
            "Candlestick",
            "None"
        ),
        "Reasons": reasons,
    }