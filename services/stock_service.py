# services/stock_service.py

import pandas as pd


# ============================================================
# MARKET DATA
# ============================================================

from services.market_data import (
    download_stock_data,
)


# ============================================================
# TECHNICAL INDICATORS
# ============================================================

from analytics.technical_indicators import (
    add_technical_indicators,
)


# ============================================================
# VOLUME ANALYSIS
# ============================================================

from analytics.volume_analysis import (
    add_volume_analysis,
)


# ============================================================
# CANDLESTICK PATTERNS
# ============================================================

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
    """
    Download stock data and calculate all
    available technical analysis components.

    Processing order:

        1. Download market data
        2. Technical indicators
        3. Volume analysis
        4. Candlestick patterns

    Parameters
    ----------
    symbol : str
        NSE stock symbol, for example:
        RELIANCE.NS

    period : str
        yfinance period, for example:
        1mo, 3mo, 6mo, 1y, 2y

    interval : str
        Data interval, for example:
        1d, 1h, 30m, 15m, 5m

    Returns
    -------
    pandas.DataFrame
    """

    # --------------------------------------------------------
    # Validate symbol
    # --------------------------------------------------------

    if symbol is None:

        return pd.DataFrame()

    symbol = str(
        symbol
    ).strip()

    if not symbol:

        return pd.DataFrame()

    # --------------------------------------------------------
    # Download market data
    # --------------------------------------------------------

    try:

        data = download_stock_data(
            symbol,
            period,
            interval,
        )

    except Exception:

        return pd.DataFrame()

    # --------------------------------------------------------
    # Validate downloaded data
    # --------------------------------------------------------

    if data is None or data.empty:

        return pd.DataFrame()

    # --------------------------------------------------------
    # Make a copy
    # --------------------------------------------------------

    data = data.copy()

    # --------------------------------------------------------
    # Normalize column names
    # --------------------------------------------------------

    data.columns = [
        str(column).strip()
        for column in data.columns
    ]

    # --------------------------------------------------------
    # Technical indicators
    # --------------------------------------------------------

    try:

        data = add_technical_indicators(
            data
        )

    except Exception:

        # Do not stop the complete stock
        # analysis if one indicator fails.
        pass

    # --------------------------------------------------------
    # Volume analysis
    # --------------------------------------------------------

    try:

        data = add_volume_analysis(
            data
        )

    except Exception:

        pass

    # --------------------------------------------------------
    # Candlestick patterns
    # --------------------------------------------------------

    try:

        data = detect_candlestick_patterns(
            data
        )

    except Exception:

        # Candlestick calculation should not
        # prevent the remaining stock analysis
        # from working.
        pass

    return data


# ============================================================
# LATEST CANDLESTICK PATTERNS
# ============================================================

def get_latest_candlestick_patterns(
    data,
):
    """
    Return candlestick patterns detected
    on the latest available candle.

    Supports:

        1. Boolean pattern columns
        2. Text-based Candlestick column

    Returns
    -------
    list
    """

    if data is None or data.empty:

        return []

    latest = data.iloc[-1]

    patterns = []

    # --------------------------------------------------------
    # Boolean pattern columns
    # --------------------------------------------------------

    for column in PATTERN_COLUMNS:

        if column not in data.columns:

            continue

        try:

            value = latest[column]

            if pd.isna(value):

                continue

            # Handle numeric/string booleans safely
            if isinstance(
                value,
                str,
            ):

                is_true = (
                    value.strip().lower()
                    in [
                        "true",
                        "1",
                        "yes",
                    ]
                )

            else:

                is_true = bool(
                    value
                )

            if is_true:

                pattern_name = (
                    column.replace(
                        "_",
                        " ",
                    )
                )

                if (
                    pattern_name
                    not in patterns
                ):

                    patterns.append(
                        pattern_name
                    )

        except Exception:

            continue

    # --------------------------------------------------------
    # Text-based Candlestick column
    # --------------------------------------------------------

    if "Candlestick" in data.columns:

        try:

            value = latest[
                "Candlestick"
            ]

            if pd.notna(value):

                text = str(
                    value
                ).strip()

                if (
                    text
                    and text.lower()
                    not in [
                        "none",
                        "nan",
                        "null",
                        "",
                    ]
                ):

                    # Some implementations may
                    # store multiple patterns
                    # separated by commas.
                    text_patterns = [
                        item.strip()
                        for item in text.split(",")
                        if item.strip()
                    ]

                    for item in text_patterns:

                        if (
                            item
                            not in patterns
                        ):

                            patterns.append(
                                item
                            )

        except Exception:

            pass

    return patterns


# ============================================================
# LATEST CANDLESTICK TEXT
# ============================================================

def get_latest_candlestick_text(
    data,
):
    """
    Return latest candlestick pattern(s)
    as a readable string.

    Example:

        Bullish Engulfing

    or:

        Hammer, Doji
    """

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
# TREND
# ============================================================

def get_stock_trend(
    data,
):
    """
    Determine the current stock trend.

    Primary logic:
        Price vs SMA 20

    Additional confirmation:
        SMA 20 vs SMA 50
        SMA 50 vs SMA 200

    Returns
    -------
    str
        Bullish / Bearish / Neutral / Unknown
    """

    if data is None or data.empty:

        return "Unknown"

    latest = data.iloc[-1]

    # --------------------------------------------------------
    # Price
    # --------------------------------------------------------

    if (
        "Close" not in data.columns
        or pd.isna(
            latest["Close"]
        )
    ):

        return "Unknown"

    close = float(
        latest["Close"]
    )

    # --------------------------------------------------------
    # SMA 20
    # --------------------------------------------------------

    if (
        "SMA_20" in data.columns
        and pd.notna(
            latest["SMA_20"]
        )
    ):

        sma20 = float(
            latest["SMA_20"]
        )

        if close > sma20:

            return "Bullish"

        if close < sma20:

            return "Bearish"

    # --------------------------------------------------------
    # SMA 50 fallback
    # --------------------------------------------------------

    if (
        "SMA_50" in data.columns
        and pd.notna(
            latest["SMA_50"]
        )
    ):

        sma50 = float(
            latest["SMA_50"]
        )

        if close > sma50:

            return "Bullish"

        if close < sma50:

            return "Bearish"

    return "Neutral"


# ============================================================
# RECOMMENDATION
# ============================================================

def calculate_recommendation(
    data,
):
    """
    Calculate stock recommendation.

    Indicators:

        SMA 20
        SMA 50
        SMA 200
        RSI
        MACD
        Supertrend
        VWAP
        Volume Ratio

    Scoring:

        Positive signal = +1
        Negative signal = -1

    Recommendation:

        >= +5 : STRONG BUY
        >= +2 : BUY
        <= -5 : STRONG SELL
        <= -2 : SELL
        otherwise HOLD

    Returns
    -------
    tuple

        (
            recommendation,
            confidence,
            reasons
        )
    """

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
    # Ensure Close exists
    # --------------------------------------------------------

    if (
        "Close" not in data.columns
        or pd.isna(
            latest["Close"]
        )
    ):

        return (
            "HOLD",
            0,
            [
                "Closing price unavailable"
            ],
        )

    close = float(
        latest["Close"]
    )

    # ========================================================
    # SMA 20
    # ========================================================

    if (
        "SMA_20" in data.columns
        and pd.notna(
            latest["SMA_20"]
        )
    ):

        sma20 = float(
            latest["SMA_20"]
        )

        if close > sma20:

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
    # SMA 50
    # ========================================================

    if (
        "SMA_50" in data.columns
        and pd.notna(
            latest["SMA_50"]
        )
    ):

        sma50 = float(
            latest["SMA_50"]
        )

        if close > sma50:

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
    # SMA 200
    # ========================================================

    if (
        "SMA_200" in data.columns
        and pd.notna(
            latest["SMA_200"]
        )
    ):

        sma200 = float(
            latest["SMA_200"]
        )

        if close > sma200:

            score += 1

            reasons.append(
                "Price above SMA 200"
            )

        else:

            score -= 1

            reasons.append(
                "Price below SMA 200"
            )

    # ========================================================
    # RSI
    # ========================================================

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

        else:

            reasons.append(
                f"RSI neutral at {rsi:.1f}"
            )

    # ========================================================
    # MACD
    # ========================================================

    if (
        "MACD" in data.columns
        and "MACD_Signal" in data.columns
    ):

        macd = latest[
            "MACD"
        ]

        signal = latest[
            "MACD_Signal"
        ]

        if (
            pd.notna(macd)
            and pd.notna(signal)
        ):

            macd = float(
                macd
            )

            signal = float(
                signal
            )

            if macd > signal:

                score += 1

                reasons.append(
                    "MACD above Signal"
                )

            elif macd < signal:

                score -= 1

                reasons.append(
                    "MACD below Signal"
                )

            else:

                reasons.append(
                    "MACD at Signal"
                )

    # ========================================================
    # SUPERTREND
    # ========================================================

    if (
        "Supertrend_Direction"
        in data.columns
    ):

        direction = latest[
            "Supertrend_Direction"
        ]

        if pd.notna(direction):

            try:

                direction = float(
                    direction
                )

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

            except Exception:

                pass

    # ========================================================
    # VWAP
    # ========================================================

    if (
        "VWAP" in data.columns
        and pd.notna(
            latest["VWAP"]
        )
    ):

        vwap = float(
            latest["VWAP"]
        )

        if close > vwap:

            score += 1

            reasons.append(
                "Price above VWAP"
            )

        elif close < vwap:

            score -= 1

            reasons.append(
                "Price below VWAP"
            )

    # ========================================================
    # VOLUME RATIO
    # ========================================================

    if (
        "Volume_Ratio"
        in data.columns
    ):

        ratio = latest[
            "Volume_Ratio"
        ]

        if pd.notna(ratio):

            try:

                ratio = float(
                    ratio
                )

                if ratio >= 1.5:

                    reasons.append(
                        f"Volume spike {ratio:.2f}x"
                    )

                    # ----------------------------------------
                    # Volume confirms price direction
                    # ----------------------------------------

                    if len(data) >= 2:

                        previous_close = (
                            data["Close"]
                            .iloc[-2]
                        )

                        if pd.notna(
                            previous_close
                        ):

                            previous_close = float(
                                previous_close
                            )

                            if close > previous_close:

                                score += 1

                                reasons.append(
                                    "Volume confirms bullish price movement"
                                )

                            elif close < previous_close:

                                score -= 1

                                reasons.append(
                                    "Volume confirms bearish price movement"
                                )

                elif ratio < 1.0:

                    reasons.append(
                        f"Low volume {ratio:.2f}x"
                    )

                else:

                    reasons.append(
                        f"Normal volume {ratio:.2f}x"
                    )

            except Exception:

                pass

    # ========================================================
    # CANDLESTICK CONFIRMATION
    # ========================================================

    patterns = (
        get_latest_candlestick_patterns(
            data
        )
    )

    bullish_patterns = {
        "Doji": 0,
        "Hammer": 1,
        "Inverted Hammer": 1,
        "Bullish Engulfing": 1,
        "Bullish Harami": 1,
        "Bullish Marubozu": 1,
        "Morning Star": 1,
        "Piercing Pattern": 1,
        "Three White Soldiers": 1,
    }

    bearish_patterns = {
        "Shooting Star": -1,
        "Bearish Engulfing": -1,
        "Bearish Harami": -1,
        "Bearish Marubozu": -1,
        "Evening Star": -1,
        "Dark Cloud Cover": -1,
        "Three Black Crows": -1,
    }

    for pattern in patterns:

        if pattern in bullish_patterns:

            if bullish_patterns[pattern] > 0:

                reasons.append(
                    f"Bullish candlestick: {pattern}"
                )

        elif pattern in bearish_patterns:

            if bearish_patterns[pattern] < 0:

                reasons.append(
                    f"Bearish candlestick: {pattern}"
                )

    # ========================================================
    # SCORE / CONFIDENCE
    # ========================================================

    # Maximum normal scoring components:
    #
    # SMA20       1
    # SMA50       1
    # SMA200      1
    # RSI         1
    # MACD        1
    # Supertrend  1
    # VWAP        1
    # Volume      1
    #
    # = 8 points
    #
    # Keep 9 for compatibility with the
    # existing recommendation model.

    max_score = 9

    confidence = (
        abs(score)
        /
        max_score
        *
        100
    )

    confidence = min(
        confidence,
        100,
    )

    # ========================================================
    # RECOMMENDATION
    # ========================================================

    if score >= 5:

        recommendation = (
            "STRONG BUY"
        )

    elif score >= 2:

        recommendation = (
            "BUY"
        )

    elif score <= -5:

        recommendation = (
            "STRONG SELL"
        )

    elif score <= -2:

        recommendation = (
            "SELL"
        )

    else:

        recommendation = (
            "HOLD"
        )

    return (
        recommendation,
        round(
            confidence,
            2,
        ),
        reasons,
    )


# ============================================================
# STOCK SUMMARY
# ============================================================

def get_stock_summary(
    symbol,
):
    """
    Return a compact stock summary.

    Used by:

        pages/07_🔎_Stock_Comparison.py

    Returns
    -------
    dict

        Symbol
        Price
        Recommendation
        Confidence
        Trend
        RSI
        MomentumScore
        VolumeRatio
        Volatility
        Candlestick
        Reasons
    """

    # --------------------------------------------------------
    # Analyze stock
    # --------------------------------------------------------

    data = analyze_stock(
        symbol,
        period="6mo",
        interval="1d",
    )

    # --------------------------------------------------------
    # No data
    # --------------------------------------------------------

    if (
        data is None
        or data.empty
    ):

        return {
            "Symbol": symbol,
            "Price": None,
            "Recommendation": "NO DATA",
            "Confidence": 0,
            "Trend": "Unknown",
            "RSI": None,
            "MomentumScore": None,
            "VolumeRatio": None,
            "Volatility": None,
            "Candlestick": "None",
            "Reasons": [],
        }

    # --------------------------------------------------------
    # Latest row
    # --------------------------------------------------------

    latest = data.iloc[-1]

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    (
        recommendation,
        confidence,
        reasons,
    ) = calculate_recommendation(
        data
    )

    # ========================================================
    # PRICE
    # ========================================================

    price = None

    if (
        "Close" in data.columns
        and pd.notna(
            latest["Close"]
        )
    ):

        try:

            price = float(
                latest["Close"]
            )

        except Exception:

            price = None

    # ========================================================
    # RSI
    # ========================================================

    rsi = None

    if (
        "RSI" in data.columns
        and pd.notna(
            latest["RSI"]
        )
    ):

        try:

            rsi = float(
                latest["RSI"]
            )

        except Exception:

            rsi = None

    # ========================================================
    # MOMENTUM
    # ========================================================

    momentum = None

    try:

        from analytics.momentum import (
            momentum_score,
        )

        momentum = momentum_score(
            data
        )

        if hasattr(
            momentum,
            "item",
        ):

            momentum = momentum.item()

        if isinstance(
            momentum,
            (int, float),
        ):

            momentum = round(
                float(momentum),
                2,
            )

    except Exception:

        momentum = None

    # ========================================================
    # VOLUME RATIO
    # ========================================================

    volume_ratio = None

    if (
        "Volume_Ratio" in data.columns
        and pd.notna(
            latest["Volume_Ratio"]
        )
    ):

        try:

            volume_ratio = float(
                latest["Volume_Ratio"]
            )

        except Exception:

            volume_ratio = None

    # ========================================================
    # VOLATILITY
    # ========================================================

    volatility = None

    try:

        from analytics.volatility import (
            calculate_volatility,
        )

        volatility = calculate_volatility(
            data
        )

        if hasattr(
            volatility,
            "item",
        ):

            volatility = volatility.item()

        if isinstance(
            volatility,
            (int, float),
        ):

            volatility = round(
                float(volatility),
                2,
            )

    except Exception:

        volatility = None

    # ========================================================
    # TREND
    # ========================================================

    trend = get_stock_trend(
        data
    )

    # ========================================================
    # CANDLESTICK
    # ========================================================

    candlestick = (
        get_latest_candlestick_text(
            data
        )
    )

    # ========================================================
    # RETURN SUMMARY
    # ========================================================

    return {
        "Symbol": symbol,

        "Price": (
            round(
                price,
                2,
            )
            if price is not None
            else None
        ),

        "Recommendation": (
            recommendation
        ),

        "Confidence": round(
            float(confidence),
            2,
        ),

        "Trend": trend,

        "RSI": (
            round(
                rsi,
                2,
            )
            if rsi is not None
            else None
        ),

        "MomentumScore": momentum,

        "VolumeRatio": (
            round(
                volume_ratio,
                2,
            )
            if volume_ratio is not None
            else None
        ),

        "Volatility": volatility,

        "Candlestick": (
            candlestick
        ),

        "Reasons": reasons,
    }