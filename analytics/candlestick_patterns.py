PATTERN_DESCRIPTIONS = {

    "Doji": (
        "Indecision candle. "
        "More useful near important support/resistance."
    ),

    "Hammer": (
        "Potential bullish reversal pattern, "
        "especially after a decline."
    ),

    "Inverted_Hammer": (
        "Potential bullish reversal pattern "
        "after a decline."
    ),

    "Shooting_Star": (
        "Potential bearish reversal pattern "
        "near resistance after an advance."
    ),

    "Bullish_Engulfing": (
        "Potential bullish reversal pattern where "
        "the bullish candle engulfs the previous bearish candle."
    ),

    "Bearish_Engulfing": (
        "Potential bearish reversal pattern where "
        "the bearish candle engulfs the previous bullish candle."
    ),

    "Bullish_Harami": (
        "Potential bullish reversal/indecision pattern."
    ),

    "Bearish_Harami": (
        "Potential bearish reversal/indecision pattern."
    ),

    "Bullish_Marubozu": (
        "Strong bullish candle with very small wicks."
    ),

    "Bearish_Marubozu": (
        "Strong bearish candle with very small wicks."
    ),

    "Morning_Star": (
        "Potential bullish three-candle reversal pattern."
    ),

    "Evening_Star": (
        "Potential bearish three-candle reversal pattern."
    ),

    "Piercing_Pattern": (
        "Potential bullish reversal pattern."
    ),

    "Dark_Cloud_Cover": (
        "Potential bearish reversal pattern."
    ),

    "Three_White_Soldiers": (
        "Three consecutive strong bullish candles."
    ),

    "Three_Black_Crows": (
        "Three consecutive strong bearish candles."
    ),
}


def get_latest_candlestick_patterns(
    data
):
    """
    Return all candlestick patterns detected
    on the latest candle.
    """

    if data is None or data.empty:
        return []

    latest = data.iloc[-1]

    patterns = []

    for pattern in PATTERN_COLUMNS:

        if pattern not in data.columns:
            continue

        value = latest[pattern]

        if bool(value):

            patterns.append(
                {
                    "name": pattern,
                    "description": PATTERN_DESCRIPTIONS.get(
                        pattern,
                        "Candlestick pattern detected."
                    ),
                }
            )

    return patterns