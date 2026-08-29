# analytics/candlestick_patterns.py

import numpy as np
import pandas as pd


# ============================================================
# PATTERN COLUMNS
# ============================================================

PATTERN_COLUMNS = [
    "Doji",
    "Hammer",
    "Inverted_Hammer",
    "Shooting_Star",
    "Bullish_Engulfing",
    "Bearish_Engulfing",
    "Bullish_Harami",
    "Bearish_Harami",
    "Bullish_Marubozu",
    "Bearish_Marubozu",
    "Morning_Star",
    "Evening_Star",
    "Piercing_Pattern",
    "Dark_Cloud_Cover",
    "Three_White_Soldiers",
    "Three_Black_Crows",
]


# ============================================================
# HELPERS
# ============================================================

def _prepare_data(data):
    """
    Validate and prepare OHLC data.
    """

    if data is None:
        return pd.DataFrame()

    if not isinstance(data, pd.DataFrame):
        return pd.DataFrame()

    if data.empty:
        return data.copy()

    df = data.copy()

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing required OHLC columns: "
            + ", ".join(missing)
        )

    for column in required_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    return df


# ============================================================
# CANDLESTICK DETECTION
# ============================================================

def detect_candlestick_patterns(data):
    """
    Detect candlestick patterns.

    Returns the original DataFrame with boolean
    columns for each detected pattern.
    """

    df = _prepare_data(data)

    if df.empty:
        return df

    # --------------------------------------------------------
    # BASIC CANDLE CALCULATIONS
    # --------------------------------------------------------

    candle_range = (
        df["High"] - df["Low"]
    )

    candle_range = candle_range.replace(
        0,
        np.nan,
    )

    body = (
        df["Close"] - df["Open"]
    )

    body_abs = body.abs()

    upper_wick = (
        df["High"]
        - df[["Open", "Close"]].max(axis=1)
    )

    lower_wick = (
        df[["Open", "Close"]].min(axis=1)
        - df["Low"]
    )

    bullish = (
        df["Close"] > df["Open"]
    )

    bearish = (
        df["Close"] < df["Open"]
    )

    # --------------------------------------------------------
    # DOJI
    # --------------------------------------------------------

    df["Doji"] = (
        body_abs <= candle_range * 0.10
    )

    # --------------------------------------------------------
    # HAMMER
    # --------------------------------------------------------

    df["Hammer"] = (
        (lower_wick >= body_abs * 2)
        & (upper_wick <= body_abs)
        & (
            body_abs
            <= candle_range * 0.40
        )
    )

    # --------------------------------------------------------
    # INVERTED HAMMER
    # --------------------------------------------------------

    df["Inverted_Hammer"] = (
        (upper_wick >= body_abs * 2)
        & (lower_wick <= body_abs)
        & (
            body_abs
            <= candle_range * 0.40
        )
    )

    # --------------------------------------------------------
    # SHOOTING STAR
    # --------------------------------------------------------

    df["Shooting_Star"] = (
        (upper_wick >= body_abs * 2)
        & (lower_wick <= body_abs)
        & (
            body_abs
            <= candle_range * 0.40
        )
    )

    # --------------------------------------------------------
    # PREVIOUS CANDLE VALUES
    # --------------------------------------------------------

    prev_open = df["Open"].shift(1)
    prev_close = df["Close"].shift(1)
    prev_high = df["High"].shift(1)
    prev_low = df["Low"].shift(1)

    prev_body = (
        prev_close - prev_open
    )

    prev_body_abs = (
        prev_body.abs()
    )

    # --------------------------------------------------------
    # BULLISH ENGULFING
    # --------------------------------------------------------

    df["Bullish_Engulfing"] = (
        bearish.shift(1)
        & bullish
        & (
            df["Open"] <= prev_close
        )
        & (
            df["Close"] >= prev_open
        )
        & (
            body_abs > prev_body_abs
        )
    ).fillna(False)

    # --------------------------------------------------------
    # BEARISH ENGULFING
    # --------------------------------------------------------

    df["Bearish_Engulfing"] = (
        bullish.shift(1)
        & bearish
        & (
            df["Open"] >= prev_close
        )
        & (
            df["Close"] <= prev_open
        )
        & (
            body_abs > prev_body_abs
        )
    ).fillna(False)

    # --------------------------------------------------------
    # BULLISH HARAMI
    # --------------------------------------------------------

    df["Bullish_Harami"] = (
        bearish.shift(1)
        & bullish
        & (
            df["Open"] > prev_close
        )
        & (
            df["Close"] < prev_open
        )
        & (
            body_abs < prev_body_abs
        )
    ).fillna(False)

    # --------------------------------------------------------
    # BEARISH HARAMI
    # --------------------------------------------------------

    df["Bearish_Harami"] = (
        bullish.shift(1)
        & bearish
        & (
            df["Open"] < prev_close
        )
        & (
            df["Close"] > prev_open
        )
        & (
            body_abs < prev_body_abs
        )
    ).fillna(False)

    # --------------------------------------------------------
    # MARUBOZU
    # --------------------------------------------------------

    df["Bullish_Marubozu"] = (
        bullish
        & (
            upper_wick
            <= candle_range * 0.05
        )
        & (
            lower_wick
            <= candle_range * 0.05
        )
    )

    df["Bearish_Marubozu"] = (
        bearish
        & (
            upper_wick
            <= candle_range * 0.05
        )
        & (
            lower_wick
            <= candle_range * 0.05
        )
    )

    # --------------------------------------------------------
    # THREE CANDLE PATTERNS
    # --------------------------------------------------------

    open_2 = df["Open"].shift(2)
    close_2 = df["Close"].shift(2)

    body_2 = (
        close_2 - open_2
    )

    body_2_abs = body_2.abs()

    bullish_2 = (
        close_2 > open_2
    )

    bearish_2 = (
        close_2 < open_2
    )

    # --------------------------------------------------------
    # MORNING STAR
    # --------------------------------------------------------

    small_middle = (
        body_abs.shift(1)
        <= (
            body_2_abs * 0.50
        )
    )

    df["Morning_Star"] = (
        bearish_2
        & small_middle
        & bullish
        & (
            df["Close"]
            >= (
                open_2
                + body_2_abs * 0.50
            )
        )
    ).fillna(False)

    # --------------------------------------------------------
    # EVENING STAR
    # --------------------------------------------------------

    df["Evening_Star"] = (
        bullish_2
        & small_middle
        & bearish
        & (
            df["Close"]
            <= (
                open_2
                - body_2_abs * 0.50
            )
        )
    ).fillna(False)

    # --------------------------------------------------------
    # PIERCING PATTERN
    # --------------------------------------------------------

    df["Piercing_Pattern"] = (
        bearish.shift(1)
        & bullish
        & (
            df["Open"] < prev_low
        )
        & (
            df["Close"]
            > (
                prev_open
                + prev_body_abs * 0.50
            )
        )
        & (
            df["Close"]
            < prev_open
        )
    ).fillna(False)

    # --------------------------------------------------------
    # DARK CLOUD COVER
    # --------------------------------------------------------

    df["Dark_Cloud_Cover"] = (
        bullish.shift(1)
        & bearish
        & (
            df["Open"] > prev_high
        )
        & (
            df["Close"]
            < (
                prev_open
                - prev_body_abs * 0.50
            )
        )
        & (
            df["Close"]
            > prev_open
        )
    ).fillna(False)

    # --------------------------------------------------------
    # THREE WHITE SOLDIERS
    # --------------------------------------------------------

    close_1 = df["Close"].shift(1)
    close_2 = df["Close"].shift(2)

    open_1 = df["Open"].shift(1)
    open_2 = df["Open"].shift(2)

    df["Three_White_Soldiers"] = (
        bullish
        & bullish.shift(1)
        & bullish.shift(2)
        & (
            df["Close"] > close_1
        )
        & (
            close_1 > close_2
        )
        & (
            df["Open"] > open_1
        )
        & (
            open_1 > open_2
        )
    ).fillna(False)

    # --------------------------------------------------------
    # THREE BLACK CROWS
    # --------------------------------------------------------

    df["Three_Black_Crows"] = (
        bearish
        & bearish.shift(1)
        & bearish.shift(2)
        & (
            df["Close"] < close_1
        )
        & (
            close_1 < close_2
        )
        & (
            df["Open"] < open_1
        )
        & (
            open_1 < open_2
        )
    ).fillna(False)

    # --------------------------------------------------------
    # CLEAN BOOLEAN COLUMNS
    # --------------------------------------------------------

    for column in PATTERN_COLUMNS:

        if column not in df.columns:

            df[column] = False

        df[column] = (
            df[column]
            .fillna(False)
            .astype(bool)
        )

    return df


# ============================================================
# LATEST PATTERNS
# ============================================================

def get_latest_patterns(data):
    """
    Return all candlestick patterns detected
    on the latest candle.
    """

    if data is None or data.empty:
        return []

    latest = data.iloc[-1]

    patterns = []

    for column in PATTERN_COLUMNS:

        if column not in data.columns:
            continue

        try:

            if bool(latest[column]):

                patterns.append(
                    column.replace(
                        "_",
                        " ",
                    )
                )

        except Exception:
            continue

    return patterns


def get_latest_pattern_text(data):
    """
    Return a user-friendly string containing
    latest detected candlestick patterns.
    """

    patterns = get_latest_patterns(
        data
    )

    if not patterns:
        return "None"

    return ", ".join(patterns)