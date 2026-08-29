# analytics/technical_indicators.py

import numpy as np
import pandas as pd


# ============================================================
# DATA NORMALIZATION
# ============================================================

def normalize_dataframe(data):

    if data is None:
        return pd.DataFrame()

    df = data.copy()

    # Fix Yahoo MultiIndex
    if isinstance(df.columns, pd.MultiIndex):

        new_columns = []

        for col in df.columns:

            if isinstance(col, tuple):

                new_columns.append(
                    str(col[0])
                )

            else:

                new_columns.append(
                    str(col)
                )

        df.columns = new_columns

    df.columns = [
        str(col).strip()
        for col in df.columns
    ]

    # Normalize OHLCV names
    rename_map = {}

    for column in df.columns:

        lower = column.lower()

        if lower == "open":
            rename_map[column] = "Open"

        elif lower == "high":
            rename_map[column] = "High"

        elif lower == "low":
            rename_map[column] = "Low"

        elif lower == "close":
            rename_map[column] = "Close"

        elif lower == "adj close":
            rename_map[column] = "Adj Close"

        elif lower == "volume":
            rename_map[column] = "Volume"

    df = df.rename(
        columns=rename_map
    )

    return df


def validate_ohlcv(data):

    required = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    missing = [
        column
        for column in required
        if column not in data.columns
    ]

    if missing:

        raise ValueError(
            "Missing OHLCV columns: "
            + ", ".join(missing)
        )


# ============================================================
# MOVING AVERAGES
# ============================================================

def calculate_sma(data, period=20):

    data = normalize_dataframe(data)

    return data["Close"].rolling(
        period
    ).mean()


def calculate_ema(data, period=20):

    data = normalize_dataframe(data)

    return data["Close"].ewm(
        span=period,
        adjust=False
    ).mean()


# ============================================================
# RSI
# ============================================================

def calculate_rsi(
    data,
    period=14
):

    data = normalize_dataframe(data)

    delta = data["Close"].diff()

    gain = delta.clip(
        lower=0
    )

    loss = -delta.clip(
        upper=0
    )

    avg_gain = gain.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    rs = avg_gain / avg_loss.replace(
        0,
        np.nan
    )

    rsi = 100 - (
        100 / (1 + rs)
    )

    return rsi


# ============================================================
# MACD
# ============================================================

def calculate_macd(data):

    data = normalize_dataframe(data)

    ema12 = data["Close"].ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = data["Close"].ewm(
        span=26,
        adjust=False
    ).mean()

    macd = ema12 - ema26

    signal = macd.ewm(
        span=9,
        adjust=False
    ).mean()

    histogram = macd - signal

    return (
        macd,
        signal,
        histogram
    )


# ============================================================
# BOLLINGER BANDS
# ============================================================

def calculate_bollinger_bands(
    data,
    period=20,
    std_dev=2
):

    data = normalize_dataframe(data)

    middle = data["Close"].rolling(
        period
    ).mean()

    std = data["Close"].rolling(
        period
    ).std()

    upper = middle + (
        std_dev * std
    )

    lower = middle - (
        std_dev * std
    )

    return (
        upper,
        middle,
        lower
    )


# ============================================================
# ATR
# ============================================================

def calculate_atr(
    data,
    period=14
):

    data = normalize_dataframe(data)

    high_low = (
        data["High"] -
        data["Low"]
    )

    high_close = (
        data["High"] -
        data["Close"].shift()
    ).abs()

    low_close = (
        data["Low"] -
        data["Close"].shift()
    ).abs()

    tr = pd.concat(
        [
            high_low,
            high_close,
            low_close,
        ],
        axis=1,
    ).max(
        axis=1
    )

    return tr.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()


# ============================================================
# VWAP
# ============================================================

def calculate_vwap(data):

    data = normalize_dataframe(data)

    typical_price = (
        data["High"]
        + data["Low"]
        + data["Close"]
    ) / 3

    volume = data["Volume"]

    cumulative_volume = (
        volume.cumsum()
    )

    cumulative_value = (
        typical_price * volume
    ).cumsum()

    return (
        cumulative_value /
        cumulative_volume.replace(
            0,
            np.nan
        )
    )


# ============================================================
# SUPERTREND
# ============================================================

def calculate_supertrend(
    data,
    period=10,
    multiplier=3
):

    data = normalize_dataframe(data)

    atr = calculate_atr(
        data,
        period
    )

    hl2 = (
        data["High"] +
        data["Low"]
    ) / 2

    upper_band = (
        hl2 +
        multiplier * atr
    )

    lower_band = (
        hl2 -
        multiplier * atr
    )

    final_upper = upper_band.copy()

    final_lower = lower_band.copy()

    direction = pd.Series(
        index=data.index,
        dtype=float
    )

    supertrend = pd.Series(
        index=data.index,
        dtype=float
    )

    direction.iloc[0] = 1

    supertrend.iloc[0] = (
        lower_band.iloc[0]
    )

    for i in range(
        1,
        len(data)
    ):

        if (
            upper_band.iloc[i]
            < final_upper.iloc[i - 1]
            or
            data["Close"].iloc[i - 1]
            > final_upper.iloc[i - 1]
        ):

            final_upper.iloc[i] = (
                upper_band.iloc[i]
            )

        else:

            final_upper.iloc[i] = (
                final_upper.iloc[i - 1]
            )

        if (
            lower_band.iloc[i]
            > final_lower.iloc[i - 1]
            or
            data["Close"].iloc[i - 1]
            < final_lower.iloc[i - 1]
        ):

            final_lower.iloc[i] = (
                lower_band.iloc[i]
            )

        else:

            final_lower.iloc[i] = (
                final_lower.iloc[i - 1]
            )

        if (
            direction.iloc[i - 1] == -1
            and
            data["Close"].iloc[i]
            > final_upper.iloc[i]
        ):

            direction.iloc[i] = 1

        elif (
            direction.iloc[i - 1] == 1
            and
            data["Close"].iloc[i]
            < final_lower.iloc[i]
        ):

            direction.iloc[i] = -1

        else:

            direction.iloc[i] = (
                direction.iloc[i - 1]
            )

        if direction.iloc[i] == 1:

            supertrend.iloc[i] = (
                final_lower.iloc[i]
            )

        else:

            supertrend.iloc[i] = (
                final_upper.iloc[i]
            )

    return (
        supertrend,
        direction
    )


# ============================================================
# CANDLESTICK PATTERNS
# ============================================================

def detect_candlestick_patterns(data):

    df = normalize_dataframe(data)

    patterns = []

    for i in range(len(df)):

        if i == 0:

            patterns.append("None")
            continue

        open_price = df["Open"].iloc[i]

        high = df["High"].iloc[i]

        low = df["Low"].iloc[i]

        close = df["Close"].iloc[i]

        previous_open = (
            df["Open"].iloc[i - 1]
        )

        previous_close = (
            df["Close"].iloc[i - 1]
        )

        body = abs(
            close - open_price
        )

        candle_range = (
            high - low
        )

        upper_shadow = (
            high -
            max(
                open_price,
                close
            )
        )

        lower_shadow = (
            min(
                open_price,
                close
            ) - low
        )

        pattern = "None"

        # Doji
        if (
            candle_range > 0
            and
            body <= candle_range * 0.10
        ):

            pattern = "Doji"

        # Bullish Engulfing
        elif (
            previous_close
            < previous_open
            and
            close > open_price
            and
            open_price <= previous_close
            and
            close >= previous_open
        ):

            pattern = "Bullish Engulfing"

        # Bearish Engulfing
        elif (
            previous_close
            > previous_open
            and
            close < open_price
            and
            open_price >= previous_close
            and
            close <= previous_open
        ):

            pattern = "Bearish Engulfing"

        # Hammer
        elif (
            lower_shadow >= body * 2
            and
            upper_shadow <= body
        ):

            pattern = "Hammer"

        # Shooting Star
        elif (
            upper_shadow >= body * 2
            and
            lower_shadow <= body
        ):

            pattern = "Shooting Star"

        patterns.append(
            pattern
        )

    return pd.Series(
        patterns,
        index=df.index
    )


# ============================================================
# HEIKIN ASHI
# ============================================================

def calculate_heikin_ashi(data):

    df = normalize_dataframe(data)

    ha = pd.DataFrame(
        index=df.index
    )

    ha["Close"] = (
        df["Open"]
        + df["High"]
        + df["Low"]
        + df["Close"]
    ) / 4

    ha_open = []

    for i in range(len(df)):

        if i == 0:

            value = (
                df["Open"].iloc[i]
                + df["Close"].iloc[i]
            ) / 2

        else:

            value = (
                ha_open[i - 1]
                + ha["Close"].iloc[i - 1]
            ) / 2

        ha_open.append(value)

    ha["Open"] = ha_open

    ha["High"] = pd.concat(
        [
            df["High"],
            ha["Open"],
            ha["Close"],
        ],
        axis=1
    ).max(
        axis=1
    )

    ha["Low"] = pd.concat(
        [
            df["Low"],
            ha["Open"],
            ha["Close"],
        ],
        axis=1
    ).min(
        axis=1
    )

    return ha


# ============================================================
# ALL INDICATORS
# ============================================================

def add_technical_indicators(data):

    df = normalize_dataframe(data)

    validate_ohlcv(df)

    df["SMA_20"] = calculate_sma(
        df,
        20
    )

    df["SMA_50"] = calculate_sma(
        df,
        50
    )

    df["SMA_200"] = calculate_sma(
        df,
        200
    )

    df["EMA_9"] = calculate_ema(
        df,
        9
    )

    df["EMA_20"] = calculate_ema(
        df,
        20
    )

    df["EMA_50"] = calculate_ema(
        df,
        50
    )

    df["RSI"] = calculate_rsi(
        df
    )

    (
        df["MACD"],
        df["MACD_Signal"],
        df["MACD_Histogram"],
    ) = calculate_macd(df)

    (
        df["BB_Upper"],
        df["BB_Middle"],
        df["BB_Lower"],
    ) = calculate_bollinger_bands(df)

    df["ATR"] = calculate_atr(
        df
    )

    df["VWAP"] = calculate_vwap(
        df
    )

    (
        df["Supertrend"],
        df["Supertrend_Direction"],
    ) = calculate_supertrend(df)

    df["Candlestick"] = (
        detect_candlestick_patterns(df)
    )

    return df