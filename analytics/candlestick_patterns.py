import pandas as pd
import numpy as np


def detect_candlestick_patterns(data):

    df = data.copy()

    body = (
        df["Close"] -
        df["Open"]
    )

    body_abs = body.abs()

    candle_range = (
        df["High"] -
        df["Low"]
    ).replace(0, np.nan)

    upper_wick = (
        df["High"] -
        df[["Open", "Close"]].max(axis=1)
    )

    lower_wick = (
        df[["Open", "Close"]].min(axis=1) -
        df["Low"]
    )

    # --------------------------------------------------------
    # Doji
    # --------------------------------------------------------

    df["Doji"] = (
        body_abs <= candle_range * 0.10
    )

    # --------------------------------------------------------
    # Hammer
    # --------------------------------------------------------

    df["Hammer"] = (
        (lower_wick >= body_abs * 2) &
        (upper_wick <= body_abs) &
        (body_abs > 0)
    )

    # --------------------------------------------------------
    # Inverted Hammer
    # --------------------------------------------------------

    df["Inverted_Hammer"] = (
        (upper_wick >= body_abs * 2) &
        (lower_wick <= body_abs) &
        (body_abs > 0)
    )

    # --------------------------------------------------------
    # Shooting Star
    # --------------------------------------------------------

    df["Shooting_Star"] = (
        (upper_wick >= body_abs * 2) &
        (lower_wick <= body_abs) &
        (body_abs > 0) &
        (
            df["Close"] <
            df["Open"]
        )
    )

    # --------------------------------------------------------
    # Bullish / Bearish
    # --------------------------------------------------------

    previous_open = df["Open"].shift(1)
    previous_close = df["Close"].shift(1)

    previous_bearish = (
        previous_close < previous_open
    )

    previous_bullish = (
        previous_close > previous_open
    )

    current_bullish = (
        df["Close"] > df["Open"]
    )

    current_bearish = (
        df["Close"] < df["Open"]
    )

    # --------------------------------------------------------
    # Bullish Engulfing
    # --------------------------------------------------------

    df["Bullish_Engulfing"] = (
        previous_bearish &
        current_bullish &
        (
            df["Open"] <= previous_close
        ) &
        (
            df["Close"] >= previous_open
        )
    )

    # --------------------------------------------------------
    # Bearish Engulfing
    # --------------------------------------------------------

    df["Bearish_Engulfing"] = (
        previous_bullish &
        current_bearish &
        (
            df["Open"] >= previous_close
        ) &
        (
            df["Close"] <= previous_open
        )
    )

    # --------------------------------------------------------
    # Harami
    # --------------------------------------------------------

    df["Bullish_Harami"] = (
        previous_bearish &
        current_bullish &
        (
            df["Open"] > previous_close
        ) &
        (
            df["Close"] < previous_open
        )
    )

    df["Bearish_Harami"] = (
        previous_bullish &
        current_bearish &
        (
            df["Open"] < previous_close
        ) &
        (
            df["Close"] > previous_open
        )
    )

    # --------------------------------------------------------
    # Marubozu
    # --------------------------------------------------------

    df["Bullish_Marubozu"] = (
        current_bullish &
        (
            upper_wick <= candle_range * 0.05
        ) &
        (
            lower_wick <= candle_range * 0.05
        )
    )

    df["Bearish_Marubozu"] = (
        current_bearish &
        (
            upper_wick <= candle_range * 0.05
        ) &
        (
            lower_wick <= candle_range * 0.05
        )
    )

    # --------------------------------------------------------
    # Morning / Evening Star
    # --------------------------------------------------------

    first_open = df["Open"].shift(2)
    first_close = df["Close"].shift(2)

    second_body = (
        df["Close"].shift(1) -
        df["Open"].shift(1)
    ).abs()

    first_body = (
        first_close -
        first_open
    ).abs()

    third_body = body_abs

    df["Morning_Star"] = (
        (first_close < first_open) &
        (second_body < first_body * 0.5) &
        current_bullish &
        (
            df["Close"] >
            (
                first_open +
                first_close
            ) / 2
        ) &
        (third_body > 0)
    )

    df["Evening_Star"] = (
        (first_close > first_open) &
        (second_body < first_body * 0.5) &
        current_bearish &
        (
            df["Close"] <
            (
                first_open +
                first_close
            ) / 2
        ) &
        (third_body > 0)
    )

    # --------------------------------------------------------
    # Piercing
    # --------------------------------------------------------

    df["Piercing_Pattern"] = (
        previous_bearish &
        current_bullish &
        (
            df["Close"] >
            (
                previous_open +
                previous_close
            ) / 2
        ) &
        (
            df["Close"] < previous_open
        )
    )

    # --------------------------------------------------------
    # Dark Cloud Cover
    # --------------------------------------------------------

    df["Dark_Cloud_Cover"] = (
        previous_bullish &
        current_bearish &
        (
            df["Close"] <
            (
                previous_open +
                previous_close
            ) / 2
        ) &
        (
            df["Close"] > previous_open
        )
    )

    # --------------------------------------------------------
    # Three White Soldiers
    # --------------------------------------------------------

    b1 = df["Close"] > df["Open"]
    b2 = b1.shift(1)
    b3 = b1.shift(2)

    df["Three_White_Soldiers"] = (
        b1 &
        b2 &
        b3 &
        (
            df["Close"] >
            df["Close"].shift(1)
        ) &
        (
            df["Close"].shift(1) >
            df["Close"].shift(2)
        )
    )

    # --------------------------------------------------------
    # Three Black Crows
    # --------------------------------------------------------

    s1 = df["Close"] < df["Open"]
    s2 = s1.shift(1)
    s3 = s1.shift(2)

    df["Three_Black_Crows"] = (
        s1 &
        s2 &
        s3 &
        (
            df["Close"] <
            df["Close"].shift(1)
        ) &
        (
            df["Close"].shift(1) <
            df["Close"].shift(2)
        )
    )

    return df


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
    "Three_Black_Crows"
]