# analytics/trend_analysis.py

import pandas as pd


def calculate_daily_trend(data):

    if data is None or data.empty:

        return "UNKNOWN"

    close = data["Close"]

    sma20 = close.rolling(20).mean()

    sma50 = close.rolling(50).mean()

    latest_close = close.iloc[-1]

    latest_sma20 = sma20.iloc[-1]

    latest_sma50 = sma50.iloc[-1]

    if (
        latest_close > latest_sma20
        and
        latest_sma20 > latest_sma50
    ):

        return "STRONG UPTREND"

    if (
        latest_close > latest_sma20
    ):

        return "UPTREND"

    if (
        latest_close < latest_sma20
        and
        latest_sma20 < latest_sma50
    ):

        return "STRONG DOWNTREND"

    if (
        latest_close < latest_sma20
    ):

        return "DOWNTREND"

    return "SIDEWAYS"


def trend_score(data):

    if data is None or data.empty:
        return 0

    score = 0

    close = data["Close"].iloc[-1]

    sma20 = data["SMA_20"].iloc[-1]

    sma50 = data["SMA_50"].iloc[-1]

    if close > sma20:
        score += 1

    if close > sma50:
        score += 1

    if sma20 > sma50:
        score += 1

    return score