# analytics/signal_engine.py

import pandas as pd
import numpy as np


def _safe_float(value):
    """Safely convert a value to float."""

    try:
        if pd.isna(value):
            return None

        return float(value)

    except (TypeError, ValueError):
        return None


def calculate_signal_score(data: pd.DataFrame):
    """
    Calculate BUY / SELL / HOLD signal.

    Score:
        + points = bullish
        - points = bearish

    Final score:
        >= 70  -> STRONG BUY
        >= 55  -> BUY
        <= 30  -> STRONG SELL
        <= 45  -> SELL
        otherwise HOLD
    """

    if data is None or data.empty:

        return {
            "score": 50,
            "signal": "HOLD",
            "confidence": 0,
            "reasons": [
                "No market data available"
            ]
        }

    df = data.copy()

    latest = df.iloc[-1]

    bullish_points = 0
    bearish_points = 0

    bullish_reasons = []
    bearish_reasons = []
    neutral_reasons = []

    # ========================================================
    # 1. RSI
    # ========================================================

    rsi = _safe_float(
        latest.get("RSI")
    )

    if rsi is not None:

        if 50 <= rsi < 70:

            bullish_points += 10

            bullish_reasons.append(
                f"RSI bullish ({rsi:.1f})"
            )

        elif rsi >= 70:

            bearish_points += 5

            bearish_reasons.append(
                f"RSI overbought ({rsi:.1f})"
            )

        elif 30 < rsi < 50:

            bearish_points += 5

            bearish_reasons.append(
                f"RSI below 50 ({rsi:.1f})"
            )

        elif rsi <= 30:

            bullish_points += 5

            bullish_reasons.append(
                f"RSI oversold ({rsi:.1f})"
            )

    # ========================================================
    # 2. VWAP
    # ========================================================

    close = _safe_float(
        latest.get("Close")
    )

    vwap = _safe_float(
        latest.get("VWAP")
    )

    if close is not None and vwap is not None:

        if close > vwap:

            bullish_points += 10

            bullish_reasons.append(
                "Price above VWAP"
            )

        elif close < vwap:

            bearish_points += 10

            bearish_reasons.append(
                "Price below VWAP"
            )

    # ========================================================
    # 3. MACD
    # ========================================================

    macd = _safe_float(
        latest.get("MACD")
    )

    macd_signal = _safe_float(
        latest.get("MACD_Signal")
    )

    if macd is not None and macd_signal is not None:

        if macd > macd_signal:

            bullish_points += 10

            bullish_reasons.append(
                "MACD bullish crossover"
            )

        else:

            bearish_points += 10

            bearish_reasons.append(
                "MACD bearish crossover"
            )

    # ========================================================
    # 4. SUPERTREND
    # ========================================================

    supertrend = None

    for column in [
        "Supertrend",
        "SuperTrend",
        "SUPERT"
    ]:

        if column in df.columns:

            supertrend = _safe_float(
                latest[column]
            )

            break

    if close is not None and supertrend is not None:

        if close > supertrend:

            bullish_points += 15

            bullish_reasons.append(
                "Price above Supertrend"
            )

        else:

            bearish_points += 15

            bearish_reasons.append(
                "Price below Supertrend"
            )

    # ========================================================
    # 5. MOVING AVERAGES
    # ========================================================

    sma20 = _safe_float(
        latest.get("SMA20")
    )

    sma50 = _safe_float(
        latest.get("SMA50")
    )

    ema20 = _safe_float(
        latest.get("EMA20")
    )

    if close is not None:

        if sma20 is not None:

            if close > sma20:

                bullish_points += 5

                bullish_reasons.append(
                    "Price above SMA20"
                )

            else:

                bearish_points += 5

                bearish_reasons.append(
                    "Price below SMA20"
                )

        if sma50 is not None:

            if close > sma50:

                bullish_points += 5

                bullish_reasons.append(
                    "Price above SMA50"
                )

            else:

                bearish_points += 5

                bearish_reasons.append(
                    "Price below SMA50"
                )

        if ema20 is not None:

            if close > ema20:

                bullish_points += 5

            else:

                bearish_points += 5

    # ========================================================
    # 6. VOLUME CONFIRMATION
    # ========================================================

    volume_ratio = _safe_float(
        latest.get("Volume_Ratio")
    )

    if volume_ratio is not None:

        if volume_ratio >= 1.5:

            if bullish_points > bearish_points:

                bullish_points += 10

                bullish_reasons.append(
                    f"Strong volume confirmation ({volume_ratio:.2f}x)"
                )

            elif bearish_points > bullish_points:

                bearish_points += 10

                bearish_reasons.append(
                    f"Strong selling volume ({volume_ratio:.2f}x)"
                )

            else:

                neutral_reasons.append(
                    f"Volume spike ({volume_ratio:.2f}x)"
                )

    # ========================================================
    # 7. CANDLESTICK PATTERNS
    # ========================================================

    bullish_patterns = [
        "Bullish_Engulfing",
        "Hammer",
        "Inverted_Hammer",
        "Morning_Star",
        "Piercing_Pattern",
        "Bullish_Harami",
        "Three_White_Soldiers"
    ]

    bearish_patterns = [
        "Bearish_Engulfing",
        "Shooting_Star",
        "Evening_Star",
        "Dark_Cloud_Cover",
        "Bearish_Harami",
        "Three_Black_Crows"
    ]

    for pattern in bullish_patterns:

        if pattern in df.columns:

            value = latest.get(pattern)

            if bool(value):

                bullish_points += 5

                bullish_reasons.append(
                    pattern.replace("_", " ")
                )

    for pattern in bearish_patterns:

        if pattern in df.columns:

            value = latest.get(pattern)

            if bool(value):

                bearish_points += 5

                bearish_reasons.append(
                    pattern.replace("_", " ")
                )

    # ========================================================
    # 8. TREND
    # ========================================================

    trend = str(
        latest.get(
            "Trend",
            ""
        )
    ).upper()

    if trend in [
        "UPTREND",
        "BULLISH",
        "STRONG BUY",
        "BUY"
    ]:

        bullish_points += 10

        bullish_reasons.append(
            f"Trend: {trend}"
        )

    elif trend in [
        "DOWNTREND",
        "BEARISH",
        "STRONG SELL",
        "SELL"
    ]:

        bearish_points += 10

        bearish_reasons.append(
            f"Trend: {trend}"
        )

    # ========================================================
    # SCORE
    # ========================================================

    total_points = (
        bullish_points +
        bearish_points
    )

    if total_points == 0:

        score = 50

    else:

        # Convert bullish-vs-bearish balance to 0-100
        score = (
            bullish_points /
            total_points *
            100
        )

    score = int(
        round(
            max(
                0,
                min(
                    100,
                    score
                )
            )
        )
    )

    # ========================================================
    # FINAL SIGNAL
    # ========================================================

    if score >= 70:

        signal = "STRONG BUY"

    elif score >= 55:

        signal = "BUY"

    elif score <= 30:

        signal = "STRONG SELL"

    elif score <= 45:

        signal = "SELL"

    else:

        signal = "HOLD"

    # ========================================================
    # CONFIDENCE
    # ========================================================

    confidence = abs(
        score - 50
    ) * 2

    confidence = int(
        min(
            100,
            confidence
        )
    )

    # ========================================================
    # REASONS
    # ========================================================

    reasons = (
        bullish_reasons +
        bearish_reasons +
        neutral_reasons
    )

    return {

        "score": score,

        "signal": signal,

        "confidence": confidence,

        "bullish_points": bullish_points,

        "bearish_points": bearish_points,

        "reasons": reasons,

        "bullish_reasons":
            bullish_reasons,

        "bearish_reasons":
            bearish_reasons,

        "neutral_reasons":
            neutral_reasons
    }