# ============================================================
# pages/03_📉_Technical_Analysis.py
#
# Professional Technical Analysis Dashboard
#
# TAB BASED VERSION
#
# Tabs:
#   1. Overview
#   2. Moving Averages
#   3. Momentum
#   4. Volatility
#   5. Intraday
#   6. Candlestick
#   7. Trade Setup
#   8. Indicator Guide
#
# Features:
#   - Responsive device-friendly UI
#   - Heikin Ashi / Candlestick / OHLC / Line
#   - Multiple technical indicators
#   - Favorite 1 / 2 / 3
#   - Professional recommendation engine
#   - STRONG BUY / BUY / HOLD / SELL / STRONG SELL
#   - Confidence level
#   - Bullish / Bearish factor analysis
#   - Recommendation reasons
#   - Buy zone
#   - Entry trigger
#   - Stop loss
#   - Target 1 / Target 2
#   - Risk / Reward
#   - Intraday / Swing / Long Term
#   - Candlestick pattern detection
#   - Indicator explanations
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from services.stock_service import analyze_stock

from components.navigation import (
    get_selected_stock,
    page_header,
    show_page_navigation,
)

from utils.indicator_guide import (
    get_indicator_tooltip,
    show_indicator_guide,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Technical Analysis",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded",
)

CURRENT_PAGE = "pages/03_📉_Technical_Analysis.py"


# ============================================================
# CONSTANTS
# ============================================================

OVERLAY_INDICATORS = [
    "SMA 20",
    "SMA 50",
    "EMA 20",
    "EMA 50",
    "Bollinger Bands",
    "VWAP",
    "Supertrend",
]

PANEL_INDICATORS = [
    "RSI",
    "MACD",
    "ATR",
    "Momentum",
    "Volume",
    "Volume Ratio",
]

ALL_INDICATORS = (
    OVERLAY_INDICATORS
    + PANEL_INDICATORS
)

DEFAULT_INDICATORS = [
    "SMA 20",
    "SMA 50",
    "EMA 20",
    "EMA 50",
    "Bollinger Bands",
    "VWAP",
    "Supertrend",
]


# ============================================================
# SESSION STATE
# ============================================================

if "technical_favorite_1" not in st.session_state:
    st.session_state["technical_favorite_1"] = (
        DEFAULT_INDICATORS.copy()
    )

if "technical_favorite_2" not in st.session_state:
    st.session_state["technical_favorite_2"] = []

if "technical_favorite_3" not in st.session_state:
    st.session_state["technical_favorite_3"] = []

if "technical_selected_indicators" not in st.session_state:
    st.session_state["technical_selected_indicators"] = (
        DEFAULT_INDICATORS.copy()
    )

if "technical_strategy_mode" not in st.session_state:
    st.session_state["technical_strategy_mode"] = "Intraday"

if "technical_graph_type" not in st.session_state:
    st.session_state["technical_graph_type"] = "Heikin Ashi"

if "technical_period" not in st.session_state:
    st.session_state["technical_period"] = "90 Days"


# ============================================================
# PAGE HEADER
# ============================================================

page_header(
    "📉 Technical Analysis",
    CURRENT_PAGE,
)

show_page_navigation()


# ============================================================
# RESPONSIVE CSS
# ============================================================

st.markdown(
    """
    <style>

    button[data-baseweb="tab"] {
        font-size: 14px;
        font-weight: 600;
        padding-left: 12px;
        padding-right: 12px;
        white-space: nowrap;
    }

    div[data-baseweb="tab-list"] {
        gap: 4px;
        overflow-x: auto;
        scrollbar-width: thin;
    }

    div[data-baseweb="tab-list"]::-webkit-scrollbar {
        height: 4px;
    }

    div[data-testid="stMetric"] {
        min-width: 0;
    }

    div[data-testid="stMetricValue"] {
        font-size: clamp(18px, 2vw, 28px);
    }

    .recommendation-card {
        padding: 18px;
        border-radius: 14px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .recommendation-title {
        font-size: 28px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .recommendation-subtitle {
        font-size: 14px;
        opacity: 0.85;
    }

    .signal-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 13px;
        margin-right: 6px;
        margin-bottom: 5px;
    }

    .reason-box {
        padding: 10px 12px;
        border-radius: 9px;
        border: 1px solid rgba(128,128,128,0.18);
        margin-bottom: 6px;
    }

    @media (max-width: 768px) {

        button[data-baseweb="tab"] {
            font-size: 12px;
            padding-left: 8px;
            padding-right: 8px;
        }

        div[data-testid="stMetricValue"] {
            font-size: 18px;
        }

        .block-container {
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }

        .recommendation-title {
            font-size: 22px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize dataframe column names."""

    if df is None or df.empty:
        return pd.DataFrame()

    result = df.copy()

    result.columns = [
        str(col)
        .strip()
        .replace(" ", "_")
        for col in result.columns
    ]

    return result


def prepare_datetime_index(
    df: pd.DataFrame,
) -> pd.DataFrame:

    """Ensure dataframe has datetime index."""

    result = df.copy()

    date_columns = [
        "Date",
        "Datetime",
        "Timestamp",
        "date",
        "datetime",
        "timestamp",
    ]

    date_column = None

    for column in date_columns:
        if column in result.columns:
            date_column = column
            break

    if date_column:

        result[date_column] = pd.to_datetime(
            result[date_column],
            errors="coerce",
        )

        result = result.dropna(
            subset=[date_column]
        )

        result = result.set_index(
            date_column
        )

    else:

        try:

            result.index = pd.to_datetime(
                result.index,
                errors="coerce",
            )

            result = result[
                ~result.index.isna()
            ]

        except Exception:
            pass

    return result.sort_index()


def prepare_numeric_columns(
    df: pd.DataFrame,
) -> pd.DataFrame:

    """Convert market and indicator columns to numeric."""

    result = df.copy()

    columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "SMA_20",
        "SMA_50",
        "EMA_20",
        "EMA_50",
        "RSI",
        "MACD",
        "MACD_Signal",
        "MACD_Histogram",
        "VWAP",
        "Supertrend",
        "ATR",
        "BB_Upper",
        "BB_Middle",
        "BB_Lower",
        "Momentum",
        "Volume_Ratio",
    ]

    for column in columns:

        if column in result.columns:

            result[column] = pd.to_numeric(
                result[column],
                errors="coerce",
            )

    return result


def calculate_heikin_ashi(
    df: pd.DataFrame,
) -> pd.DataFrame:

    """Calculate Heikin Ashi candles."""

    result = df.copy()

    required = [
        "Open",
        "High",
        "Low",
        "Close",
    ]

    if not all(
        column in result.columns
        for column in required
    ):
        return result

    result["HA_Close"] = (
        result["Open"]
        + result["High"]
        + result["Low"]
        + result["Close"]
    ) / 4.0

    ha_open = np.zeros(len(result))

    if len(result) > 0:

        ha_open[0] = (
            result["Open"].iloc[0]
            + result["Close"].iloc[0]
        ) / 2.0

        for i in range(1, len(result)):

            ha_open[i] = (
                ha_open[i - 1]
                + result["HA_Close"].iloc[i - 1]
            ) / 2.0

    result["HA_Open"] = ha_open

    result["HA_High"] = result[
        [
            "High",
            "HA_Open",
            "HA_Close",
        ]
    ].max(axis=1)

    result["HA_Low"] = result[
        [
            "Low",
            "HA_Open",
            "HA_Close",
        ]
    ].min(axis=1)

    return result


def filter_period(
    df: pd.DataFrame,
    period: str,
) -> pd.DataFrame:

    if df.empty:
        return df

    if period == "All Data":
        return df

    days_map = {
        "30 Days": 30,
        "60 Days": 60,
        "90 Days": 90,
        "180 Days": 180,
        "1 Year": 365,
    }

    days = days_map.get(period)

    if days is None:
        return df

    latest = df.index.max()

    start = latest - pd.Timedelta(
        days=days
    )

    return df[
        df.index >= start
    ]


def latest_value(
    df: pd.DataFrame,
    column: str,
):

    if column not in df.columns:
        return None

    values = df[column].dropna()

    if values.empty:
        return None

    try:
        return float(values.iloc[-1])
    except Exception:
        return None


def previous_value(
    df: pd.DataFrame,
    column: str,
):

    if column not in df.columns:
        return None

    values = df[column].dropna()

    if len(values) < 2:
        return None

    try:
        return float(values.iloc[-2])
    except Exception:
        return None


def fmt(
    value,
    decimals=2,
):

    if value is None:
        return "N/A"

    try:

        if pd.isna(value):
            return "N/A"

        return f"{float(value):,.{decimals}f}"

    except Exception:
        return "N/A"


def pct(
    value,
):

    if value is None:
        return "N/A"

    try:
        return f"{float(value):.2f}%"
    except Exception:
        return "N/A"


# ============================================================
# CANDLESTICK PATTERN
# ============================================================

def detect_candlestick_pattern(
    df: pd.DataFrame,
):

    required = [
        "Open",
        "High",
        "Low",
        "Close",
    ]

    if df.empty:
        return {
            "pattern": "No Pattern",
            "bias": "Neutral",
            "description": "No market data available.",
        }

    if not all(
        column in df.columns
        for column in required
    ):
        return {
            "pattern": "Insufficient Data",
            "bias": "Neutral",
            "description": "OHLC data is required.",
        }

    if len(df) < 2:
        return {
            "pattern": "Insufficient Data",
            "bias": "Neutral",
            "description": "At least two candles are required.",
        }

    current = df.iloc[-1]
    previous = df.iloc[-2]

    o = float(current["Open"])
    h = float(current["High"])
    l = float(current["Low"])
    c = float(current["Close"])

    po = float(previous["Open"])
    pc = float(previous["Close"])

    body = abs(c - o)
    candle_range = max(h - l, 0.000001)

    upper_wick = h - max(o, c)
    lower_wick = min(o, c) - l

    bullish = c > o
    bearish = c < o

    if body <= candle_range * 0.10:

        return {
            "pattern": "Doji",
            "bias": "Neutral",
            "description": (
                "Open and close are very close, "
                "indicating market indecision."
            ),
        }

    if (
        bullish
        and pc < po
        and o <= pc
        and c >= po
    ):

        return {
            "pattern": "Bullish Engulfing",
            "bias": "Bullish",
            "description": (
                "The current bullish candle engulfs "
                "the previous bearish candle."
            ),
        }

    if (
        bearish
        and pc > po
        and o >= pc
        and c <= po
    ):

        return {
            "pattern": "Bearish Engulfing",
            "bias": "Bearish",
            "description": (
                "The current bearish candle engulfs "
                "the previous bullish candle."
            ),
        }

    if (
        lower_wick >= body * 2
        and upper_wick <= body
    ):

        return {
            "pattern": "Hammer",
            "bias": "Bullish",
            "description": (
                "Long lower wick suggests rejection "
                "of lower prices."
            ),
        }

    if (
        upper_wick >= body * 2
        and lower_wick <= body
    ):

        return {
            "pattern": "Shooting Star",
            "bias": "Bearish",
            "description": (
                "Long upper wick suggests rejection "
                "of higher prices."
            ),
        }

    if (
        bullish
        and body >= candle_range * 0.70
    ):

        return {
            "pattern": "Strong Bullish Candle",
            "bias": "Bullish",
            "description": (
                "Large bullish body indicates strong "
                "buying pressure."
            ),
        }

    if (
        bearish
        and body >= candle_range * 0.70
    ):

        return {
            "pattern": "Strong Bearish Candle",
            "bias": "Bearish",
            "description": (
                "Large bearish body indicates strong "
                "selling pressure."
            ),
        }

    return {
        "pattern": "Normal Candle",
        "bias": "Neutral",
        "description": (
            "No major classical candlestick pattern "
            "was detected."
        ),
    }


# ============================================================
# PROFESSIONAL TECHNICAL RECOMMENDATION ENGINE
# ============================================================

def calculate_technical_signal(
    df: pd.DataFrame,
    strategy_mode: str = "Intraday",
):

    if df.empty:

        return {
            "score": 50,
            "signal": "HOLD",
            "confidence": "Low",
            "reasons": [],
            "bullish_reasons": [],
            "bearish_reasons": [],
            "warnings": [],
            "bullish_count": 0,
            "bearish_count": 0,
            "candlestick": {},
        }

    # --------------------------------------------------------
    # Base score
    # --------------------------------------------------------

    score = 50.0

    bullish_count = 0
    bearish_count = 0

    bullish_reasons = []
    bearish_reasons = []
    warnings = []

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    def bullish(points, reason):
        nonlocal score
        score += points
        bullish_reasons.append(reason)

    def bearish(points, reason):
        nonlocal score
        score -= points
        bearish_reasons.append(reason)

    # --------------------------------------------------------
    # Values
    # --------------------------------------------------------

    close = latest_value(df, "Close")

    sma20 = latest_value(df, "SMA_20")
    sma50 = latest_value(df, "SMA_50")

    ema20 = latest_value(df, "EMA_20")
    ema50 = latest_value(df, "EMA_50")

    vwap = latest_value(df, "VWAP")
    supertrend = latest_value(df, "Supertrend")

    rsi = latest_value(df, "RSI")

    macd = latest_value(df, "MACD")
    macd_signal = latest_value(df, "MACD_Signal")
    macd_hist = latest_value(df, "MACD_Histogram")

    bb_middle = latest_value(df, "BB_Middle")
    bb_upper = latest_value(df, "BB_Upper")
    bb_lower = latest_value(df, "BB_Lower")

    momentum = latest_value(df, "Momentum")

    volume_ratio = latest_value(
        df,
        "Volume_Ratio",
    )

    # ========================================================
    # STRATEGY WEIGHTS
    # ========================================================

    if strategy_mode == "Intraday":

        weights = {
            "price_sma": 6,
            "ma_cross": 5,
            "ema_cross": 5,
            "vwap": 12,
            "supertrend": 12,
            "rsi": 7,
            "macd": 9,
            "bb": 3,
            "momentum": 5,
            "volume": 8,
            "candle": 4,
        }

    elif strategy_mode == "Swing":

        weights = {
            "price_sma": 8,
            "ma_cross": 10,
            "ema_cross": 8,
            "vwap": 4,
            "supertrend": 9,
            "rsi": 7,
            "macd": 9,
            "bb": 4,
            "momentum": 7,
            "volume": 5,
            "candle": 4,
        }

    else:

        weights = {
            "price_sma": 10,
            "ma_cross": 13,
            "ema_cross": 11,
            "vwap": 1,
            "supertrend": 8,
            "rsi": 5,
            "macd": 8,
            "bb": 3,
            "momentum": 8,
            "volume": 3,
            "candle": 2,
        }

    # ========================================================
    # PRICE VS SMA 20
    # ========================================================

    if close is not None and sma20 is not None:

        if close > sma20:

            bullish(
                weights["price_sma"],
                "Price is above SMA 20, supporting short-term strength.",
            )

            bullish_count += 1

        else:

            bearish(
                weights["price_sma"],
                "Price is below SMA 20, indicating short-term weakness.",
            )

            bearish_count += 1

    # ========================================================
    # SMA 20 / SMA 50
    # ========================================================

    if (
        sma20 is not None
        and sma50 is not None
    ):

        if sma20 > sma50:

            bullish(
                weights["ma_cross"],
                "SMA 20 is above SMA 50, supporting a bullish trend.",
            )

            bullish_count += 1

        else:

            bearish(
                weights["ma_cross"],
                "SMA 20 is below SMA 50, indicating a weaker trend.",
            )

            bearish_count += 1

    # ========================================================
    # EMA 20 / EMA 50
    # ========================================================

    if (
        ema20 is not None
        and ema50 is not None
    ):

        if ema20 > ema50:

            bullish(
                weights["ema_cross"],
                "EMA 20 is above EMA 50, supporting positive momentum.",
            )

            bullish_count += 1

        else:

            bearish(
                weights["ema_cross"],
                "EMA 20 is below EMA 50, indicating negative momentum.",
            )

            bearish_count += 1

    # ========================================================
    # VWAP
    # ========================================================

    if (
        close is not None
        and vwap is not None
    ):

        if close > vwap:

            bullish(
                weights["vwap"],
                "Price is above VWAP, indicating buyer control.",
            )

            bullish_count += 1

        else:

            bearish(
                weights["vwap"],
                "Price is below VWAP, indicating seller control.",
            )

            bearish_count += 1

    # ========================================================
    # SUPERTREND
    # ========================================================

    if (
        close is not None
        and supertrend is not None
    ):

        if close > supertrend:

            bullish(
                weights["supertrend"],
                "Price is above Supertrend, confirming an upward trend.",
            )

            bullish_count += 1

        else:

            bearish(
                weights["supertrend"],
                "Price is below Supertrend, confirming downward pressure.",
            )

            bearish_count += 1

    # ========================================================
    # RSI
    # ========================================================

    if rsi is not None:

        if 50 <= rsi < 65:

            bullish(
                weights["rsi"],
                f"RSI is {rsi:.1f}, showing healthy bullish momentum.",
            )

            bullish_count += 1

        elif 65 <= rsi < 70:

            bullish(
                weights["rsi"] * 0.5,
                f"RSI is {rsi:.1f}, showing strong momentum but approaching overbought.",
            )

            bullish_count += 1

            warnings.append(
                "RSI is approaching the overbought zone."
            )

        elif rsi >= 70:

            bearish(
                weights["rsi"] * 0.5,
                f"RSI is {rsi:.1f}, indicating an overbought condition.",
            )

            bearish_count += 1

            warnings.append(
                "Avoid chasing an already overbought move."
            )

        elif 30 < rsi < 50:

            bearish(
                weights["rsi"] * 0.6,
                f"RSI is {rsi:.1f}, indicating weaker momentum.",
            )

            bearish_count += 1

        else:

            bullish(
                weights["rsi"] * 0.5,
                f"RSI is {rsi:.1f}, indicating an oversold condition that may support a reversal.",
            )

            bullish_count += 1

            warnings.append(
                "RSI is oversold; wait for price confirmation before entering."
            )

    # ========================================================
    # MACD
    # ========================================================

    if (
        macd is not None
        and macd_signal is not None
    ):

        if macd > macd_signal:

            bullish(
                weights["macd"],
                "MACD is above its signal line, supporting bullish momentum.",
            )

            bullish_count += 1

        else:

            bearish(
                weights["macd"],
                "MACD is below its signal line, indicating bearish momentum.",
            )

            bearish_count += 1

    if macd_hist is not None:

        if macd_hist > 0:

            bullish(
                weights["macd"] * 0.35,
                "MACD histogram is positive.",
            )

        else:

            bearish(
                weights["macd"] * 0.35,
                "MACD histogram is negative.",
            )

    # ========================================================
    # BOLLINGER BANDS
    # ========================================================

    if (
        close is not None
        and bb_middle is not None
    ):

        if close > bb_middle:

            bullish(
                weights["bb"],
                "Price is above the Bollinger middle band.",
            )

            bullish_count += 1

        else:

            bearish(
                weights["bb"],
                "Price is below the Bollinger middle band.",
            )

            bearish_count += 1

    if (
        close is not None
        and bb_upper is not None
        and close >= bb_upper
    ):

        warnings.append(
            "Price is near/above the upper Bollinger Band; breakout confirmation is preferable to chasing."
        )

    if (
        close is not None
        and bb_lower is not None
        and close <= bb_lower
    ):

        warnings.append(
            "Price is near/below the lower Bollinger Band; reversal confirmation is required."
        )

    # ========================================================
    # MOMENTUM
    # ========================================================

    if momentum is not None:

        if momentum > 0:

            bullish(
                weights["momentum"],
                "Momentum is positive.",
            )

            bullish_count += 1

        else:

            bearish(
                weights["momentum"],
                "Momentum is negative.",
            )

            bearish_count += 1

    # ========================================================
    # VOLUME
    # ========================================================

    if volume_ratio is not None:

        if volume_ratio >= 1.5:

            if bullish_count > bearish_count:

                bullish(
                    weights["volume"],
                    f"Volume is elevated at {volume_ratio:.2f}x reference volume and supports the bullish move.",
                )

                bullish_count += 1

            elif bearish_count > bullish_count:

                bearish(
                    weights["volume"],
                    f"High volume at {volume_ratio:.2f}x is accompanying bearish pressure.",
                )

                bearish_count += 1

            else:

                warnings.append(
                    f"Volume is elevated at {volume_ratio:.2f}x, but directional confirmation is mixed."
                )

        elif volume_ratio < 0.75:

            warnings.append(
                "Volume is below normal; breakouts may require additional confirmation."
            )

    # ========================================================
    # CANDLESTICK
    # ========================================================

    candle = detect_candlestick_pattern(df)

    if candle["bias"] == "Bullish":

        bullish(
            weights["candle"],
            f"Candlestick pattern is bullish: {candle['pattern']}.",
        )

        bullish_count += 1

    elif candle["bias"] == "Bearish":

        bearish(
            weights["candle"],
            f"Candlestick pattern is bearish: {candle['pattern']}.",
        )

        bearish_count += 1

    # ========================================================
    # ALIGNMENT CHECK
    # ========================================================

    factor_difference = (
        bullish_count - bearish_count
    )

    if (
        bullish_count > 0
        and bearish_count > 0
        and abs(factor_difference) <= 1
    ):

        warnings.append(
            "Technical indicators are closely mixed. Wait for confirmation rather than entering aggressively."
        )

        # Make mixed setups more conservative.
        if score > 70:
            score -= 5

        elif score < 30:
            score += 5

    # ========================================================
    # SCORE NORMALIZATION
    # ========================================================

    score = max(
        0,
        min(
            100,
            score,
        ),
    )

    # ========================================================
    # SIGNAL
    # ========================================================

    if (
        score >= 78
        and bullish_count >= bearish_count + 2
    ):

        signal = "STRONG BUY"

    elif (
        score >= 60
        and bullish_count > bearish_count
    ):

        signal = "BUY"

    elif (
        score <= 22
        and bearish_count >= bullish_count + 2
    ):

        signal = "STRONG SELL"

    elif (
        score < 45
        and bearish_count > bullish_count
    ):

        signal = "SELL"

    else:

        signal = "HOLD"

    # ========================================================
    # CONFIDENCE
    # ========================================================

    factor_gap = abs(
        bullish_count - bearish_count
    )

    if (
        signal in ["STRONG BUY", "STRONG SELL"]
        and factor_gap >= 4
        and (score >= 80 or score <= 20)
    ):

        confidence = "Very High"

    elif (
        signal in ["STRONG BUY", "STRONG SELL", "BUY", "SELL"]
        and factor_gap >= 3
    ):

        confidence = "High"

    elif factor_gap >= 2:

        confidence = "Moderate"

    else:

        confidence = "Low"

    return {
        "score": round(score, 1),
        "signal": signal,
        "confidence": confidence,
        "reasons": (
            bullish_reasons
            + bearish_reasons
        ),
        "bullish_reasons": bullish_reasons,
        "bearish_reasons": bearish_reasons,
        "warnings": warnings,
        "bullish_count": bullish_count,
        "bearish_count": bearish_count,
        "candlestick": candle,
        "strategy_mode": strategy_mode,
    }


# ============================================================
# RECOMMENDATION ACTION
# ============================================================

def get_recommendation_action(
    signal_data: dict,
    strategy_mode: str,
):

    signal = signal_data.get(
        "signal",
        "HOLD",
    )

    if signal == "STRONG BUY":

        return (
            "Consider a long/buy setup only after the entry "
            "trigger is confirmed. Avoid chasing a large price "
            "extension."
        )

    if signal == "BUY":

        return (
            "Prefer buying near the calculated entry zone or "
            "after the trigger is confirmed with price and volume."
        )

    if signal == "SELL":

        if strategy_mode == "Intraday":

            return (
                "Avoid fresh long entries. Existing positions "
                "should be reviewed for risk. Short trades require "
                "confirmation below the trigger."
            )

        return (
            "Avoid fresh long entries until the technical structure "
            "improves. Existing positions should be reviewed for risk."
        )

    if signal == "STRONG SELL":

        return (
            "Avoid fresh long entries. Existing positions should "
            "consider risk-control/exit levels. Short setups require "
            "confirmation rather than chasing the fall."
        )

    return (
        "Wait for stronger confirmation. The current indicators "
        "do not provide a sufficiently clear directional edge."
    )


# ============================================================
# TRADE PLAN
# ============================================================

def calculate_trade_plan(
    df: pd.DataFrame,
    timeframe: str,
    signal_data: dict,
):

    close = latest_value(
        df,
        "Close",
    )

    atr = latest_value(
        df,
        "ATR",
    )

    if close is None:
        return None

    if (
        atr is None
        or atr <= 0
    ):

        fallback = {
            "Intraday": 0.01,
            "Swing": 0.03,
            "Long Term": 0.06,
        }

        atr = close * fallback.get(
            timeframe,
            0.03,
        )

    settings = {

        "Intraday": {
            "stop_atr": 1.0,
            "target1_rr": 1.5,
            "target2_rr": 2.0,
            "trigger_atr": 0.20,
        },

        "Swing": {
            "stop_atr": 1.5,
            "target1_rr": 2.0,
            "target2_rr": 3.0,
            "trigger_atr": 0.30,
        },

        "Long Term": {
            "stop_atr": 2.5,
            "target1_rr": 2.0,
            "target2_rr": 3.5,
            "trigger_atr": 0.50,
        },
    }

    cfg = settings.get(
        timeframe,
        settings["Swing"],
    )

    signal = signal_data.get(
        "signal",
        "HOLD",
    )

    # ========================================================
    # LONG
    # ========================================================

    if signal in [
        "STRONG BUY",
        "BUY",
    ]:

        entry = (
            close
            + atr * cfg["trigger_atr"]
        )

        buy_zone_low = max(
            0,
            close - atr * 0.25,
        )

        buy_zone_high = (
            close + atr * 0.10
        )

        risk = (
            atr * cfg["stop_atr"]
        )

        stop_loss = max(
            0,
            entry - risk,
        )

        target1 = (
            entry
            + risk * cfg["target1_rr"]
        )

        target2 = (
            entry
            + risk * cfg["target2_rr"]
        )

        return {
            "direction": "LONG",
            "entry": entry,
            "buy_zone_low": buy_zone_low,
            "buy_zone_high": buy_zone_high,
            "stop_loss": stop_loss,
            "target1": target1,
            "target2": target2,
            "risk": risk,
            "reward1": target1 - entry,
            "reward2": target2 - entry,
            "entry_condition": (
                f"Consider entry only if price sustains above "
                f"₹{entry:.2f} and bullish confirmation remains intact."
            ),
            "exit_condition": (
                f"Exit/review the position if price closes below "
                f"approximately ₹{stop_loss:.2f} or bullish structure breaks."
            ),
        }

    # ========================================================
    # SHORT
    # ========================================================

    if signal in [
        "STRONG SELL",
        "SELL",
    ]:

        entry = (
            close
            - atr * cfg["trigger_atr"]
        )

        sell_zone_low = max(
            0,
            close - atr * 0.10,
        )

        sell_zone_high = (
            close + atr * 0.25
        )

        risk = (
            atr * cfg["stop_atr"]
        )

        stop_loss = (
            entry + risk
        )

        target1 = (
            entry
            - risk * cfg["target1_rr"]
        )

        target2 = (
            entry
            - risk * cfg["target2_rr"]
        )

        return {
            "direction": "SHORT",
            "entry": entry,
            "buy_zone_low": sell_zone_low,
            "buy_zone_high": sell_zone_high,
            "stop_loss": stop_loss,
            "target1": target1,
            "target2": target2,
            "risk": risk,
            "reward1": entry - target1,
            "reward2": entry - target2,
            "entry_condition": (
                f"Consider short/exit confirmation only if price "
                f"sustains below ₹{entry:.2f} and bearish confirmation remains intact."
            ),
            "exit_condition": (
                f"Exit short if price moves above approximately "
                f"₹{stop_loss:.2f} or bearish structure breaks."
            ),
        }

    # ========================================================
    # HOLD
    # ========================================================

    return {
        "direction": "WAIT",
        "entry": close,
        "buy_zone_low": close * 0.99,
        "buy_zone_high": close * 1.01,
        "stop_loss": close,
        "target1": close,
        "target2": close,
        "risk": 0,
        "reward1": 0,
        "reward2": 0,
        "entry_condition": (
            "Wait for stronger confirmation before taking "
            "a directional position."
        ),
        "exit_condition": (
            "Avoid chasing price while indicators remain mixed."
        ),
    }


# ============================================================
# RECOMMENDATION CARD
# ============================================================

def show_recommendation_card(
    stock,
    strategy_mode,
    signal_data,
    trade_plan,
):

    signal = signal_data.get(
        "signal",
        "HOLD",
    )

    score = signal_data.get(
        "score",
        50,
    )

    confidence = signal_data.get(
        "confidence",
        "Low",
    )

    bullish_count = signal_data.get(
        "bullish_count",
        0,
    )

    bearish_count = signal_data.get(
        "bearish_count",
        0,
    )

    if signal == "STRONG BUY":

        st.success(
            f"🟢 **STRONG BUY** — Technical score {score:.0f}/100"
        )

    elif signal == "BUY":

        st.success(
            f"🟢 **BUY** — Technical score {score:.0f}/100"
        )

    elif signal == "SELL":

        st.warning(
            f"🟠 **SELL** — Technical score {score:.0f}/100"
        )

    elif signal == "STRONG SELL":

        st.error(
            f"🔴 **STRONG SELL** — Technical score {score:.0f}/100"
        )

    else:

        st.info(
            f"🟡 **HOLD** — Technical score {score:.0f}/100"
        )

    r1, r2, r3, r4 = st.columns(
        4,
        gap="small",
    )

    with r1:

        st.metric(
            "Recommendation",
            signal,
        )

    with r2:

        st.metric(
            "Confidence",
            confidence,
        )

    with r3:

        st.metric(
            "Bullish Factors",
            bullish_count,
        )

    with r4:

        st.metric(
            "Bearish Factors",
            bearish_count,
        )

    st.markdown(
        "### 🧠 Why this recommendation?"
    )

    bullish_reasons = signal_data.get(
        "bullish_reasons",
        [],
    )

    bearish_reasons = signal_data.get(
        "bearish_reasons",
        [],
    )

    if bullish_reasons:

        st.markdown(
            "#### 🟢 Bullish confirmations"
        )

        for reason in bullish_reasons[:6]:

            st.write(
                "✅ " + reason
            )

    if bearish_reasons:

        st.markdown(
            "#### 🔴 Bearish confirmations"
        )

        for reason in bearish_reasons[:6]:

            st.write(
                "⚠️ " + reason
            )

    warnings = signal_data.get(
        "warnings",
        [],
    )

    if warnings:

        st.markdown(
            "#### ⚠️ Risk / Confirmation Warnings"
        )

        for warning in warnings:

            st.warning(
                warning
            )

    st.markdown(
        "### 🎯 Recommended Action"
    )

    st.info(
        get_recommendation_action(
            signal_data,
            strategy_mode,
        )
    )

    if trade_plan:

        st.markdown(
            f"### 📌 {strategy_mode} Reference Levels"
        )

        p1, p2, p3, p4 = st.columns(
            4,
            gap="small",
        )

        with p1:

            st.metric(
                "Entry / Trigger",
                f"₹{fmt(trade_plan['entry'])}",
            )

        with p2:

            st.metric(
                "Stop Loss",
                f"₹{fmt(trade_plan['stop_loss'])}",
            )

        with p3:

            st.metric(
                "Target 1",
                f"₹{fmt(trade_plan['target1'])}",
            )

        with p4:

            st.metric(
                "Target 2",
                f"₹{fmt(trade_plan['target2'])}",
            )


# ============================================================
# INDICATOR CHIPS
# ============================================================

def show_indicator_chips(
    indicators,
):

    if not indicators:

        st.caption(
            "No indicators selected."
        )

        return

    chips = []

    for indicator in indicators:

        chips.append(
            f"""
            <span style="
                display:inline-block;
                padding:5px 10px;
                margin:3px 4px 3px 0;
                border-radius:14px;
                background:rgba(120,120,120,0.12);
                border:1px solid rgba(120,120,120,0.25);
                font-size:13px;
                white-space:nowrap;
            ">
                {indicator}
            </span>
            """
        )

    st.markdown(
        "".join(chips),
        unsafe_allow_html=True,
    )


# ============================================================
# LOAD STOCK
# ============================================================

stock = get_selected_stock()

if not stock:

    st.warning(
        "Please select a stock from the Stock Symbol selector."
    )

    st.stop()


with st.spinner(
    f"Loading technical analysis for {stock}..."
):

    try:

        data = analyze_stock(stock)

    except Exception as exc:

        st.error(
            f"Unable to analyze {stock}: {exc}"
        )

        st.stop()


if data is None:

    st.warning(
        "No data returned for the selected stock."
    )

    st.stop()


if not isinstance(
    data,
    pd.DataFrame,
):

    try:

        data = pd.DataFrame(data)

    except Exception as exc:

        st.error(
            f"Unable to convert stock data: {exc}"
        )

        st.stop()


if data.empty:

    st.warning(
        "No market data is available."
    )

    st.stop()


# ============================================================
# PREPARE DATA
# ============================================================

df = normalize_columns(data)

df = prepare_datetime_index(df)

df = prepare_numeric_columns(df)

df = calculate_heikin_ashi(df)


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

    st.error(
        "Missing required market columns: "
        + ", ".join(missing)
    )

    st.stop()


# ============================================================
# CURRENT PRICE
# ============================================================

current_price = latest_value(
    df,
    "Close",
)

previous_close = previous_value(
    df,
    "Close",
)

if (
    current_price is not None
    and previous_close is not None
    and previous_close != 0
):

    price_change_pct = (
        (
            current_price
            - previous_close
        )
        / previous_close
    ) * 100

else:

    price_change_pct = None


volume = latest_value(
    df,
    "Volume",
)


# ============================================================
# GLOBAL CONTROLS
# ============================================================

control1, control2, control3 = st.columns(
    3,
    gap="small",
)

with control1:

    strategy_mode = st.selectbox(
        "🎯 Strategy",
        [
            "Intraday",
            "Swing",
            "Long Term",
        ],
        key="technical_strategy_mode",
    )

with control2:

    graph_type = st.selectbox(
        "📈 Price Chart",
        [
            "Heikin Ashi",
            "Candlestick",
            "OHLC",
            "Line",
        ],
        key="technical_graph_type",
    )

with control3:

    period = st.selectbox(
        "📅 Period",
        [
            "30 Days",
            "60 Days",
            "90 Days",
            "180 Days",
            "1 Year",
            "All Data",
        ],
        key="technical_period",
    )


chart_df = filter_period(
    df,
    period,
)


# ============================================================
# GLOBAL SIGNAL
# ============================================================

signal_data = calculate_technical_signal(
    chart_df,
    strategy_mode,
)

trade_plan = calculate_trade_plan(
    chart_df,
    strategy_mode,
    signal_data,
)


# ============================================================
# FAVORITES
# ============================================================

with st.expander(
    "⭐ Indicator Favorites",
    expanded=False,
):

    f1, f2, f3 = st.columns(
        3,
        gap="small",
    )

    with f1:

        if st.button(
            "⭐ Load Favorite 1",
            width="stretch",
        ):

            st.session_state[
                "technical_selected_indicators"
            ] = st.session_state[
                "technical_favorite_1"
            ].copy()

            st.rerun()

    with f2:

        if st.button(
            "⭐ Load Favorite 2",
            width="stretch",
        ):

            st.session_state[
                "technical_selected_indicators"
            ] = st.session_state[
                "technical_favorite_2"
            ].copy()

            st.rerun()

    with f3:

        if st.button(
            "⭐ Load Favorite 3",
            width="stretch",
        ):

            st.session_state[
                "technical_selected_indicators"
            ] = st.session_state[
                "technical_favorite_3"
            ].copy()

            st.rerun()

    st.divider()

    selected_indicators = st.multiselect(
        "📌 Select indicators",
        options=ALL_INDICATORS,
        key="technical_selected_indicators",
        help=(
            "Select multiple indicators. Overlay indicators "
            "are drawn on the price chart."
        ),
    )

    save1, save2, save3 = st.columns(
        3,
        gap="small",
    )

    with save1:

        if st.button(
            "💾 Save Favorite 1",
            width="stretch",
        ):

            st.session_state[
                "technical_favorite_1"
            ] = selected_indicators.copy()

            st.success(
                "Favorite 1 saved."
            )

    with save2:

        if st.button(
            "💾 Save Favorite 2",
            width="stretch",
        ):

            st.session_state[
                "technical_favorite_2"
            ] = selected_indicators.copy()

            st.success(
                "Favorite 2 saved."
            )

    with save3:

        if st.button(
            "💾 Save Favorite 3",
            width="stretch",
        ):

            st.session_state[
                "technical_favorite_3"
            ] = selected_indicators.copy()

            st.success(
                "Favorite 3 saved."
            )

    st.markdown(
        "#### Selected Indicators"
    )

    show_indicator_chips(
        selected_indicators
    )


# ============================================================
# MAIN TABS
# ============================================================

tabs = st.tabs(
    [
        "📊 Overview",
        "📈 Moving Averages",
        "⚡ Momentum",
        "📊 Volatility",
        "💹 Intraday",
        "🕯️ Candlestick",
        "🎯 Trade Setup",
        "📚 Indicator Guide",
    ]
)


# ============================================================
# TAB 1 - OVERVIEW
# ============================================================

with tabs[0]:

    st.subheader(
        f"📊 {stock.replace('.NS', '')} Technical Overview"
    )

    # --------------------------------------------------------
    # Price summary
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(
        4,
        gap="small",
    )

    with c1:

        st.metric(
            "Current Price",
            (
                f"₹{fmt(current_price)}"
                if current_price is not None
                else "N/A"
            ),
            (
                pct(price_change_pct)
                if price_change_pct is not None
                else None
            ),
        )

    with c2:

        st.metric(
            "Technical Score",
            f"{signal_data['score']:.0f}/100",
        )

    with c3:

        st.metric(
            "Bullish Factors",
            signal_data["bullish_count"],
        )

    with c4:

        st.metric(
            "Bearish Factors",
            signal_data["bearish_count"],
        )

    st.divider()

    # --------------------------------------------------------
    # PROFESSIONAL RECOMMENDATION
    # --------------------------------------------------------

    st.markdown(
        "## 🧠 Professional Technical Recommendation"
    )

    st.caption(
        f"Strategy: **{strategy_mode}** | "
        f"Period: **{period}** | "
        f"Stock: **{stock.replace('.NS', '')}**"
    )

    show_recommendation_card(
        stock,
        strategy_mode,
        signal_data,
        trade_plan,
    )

    # --------------------------------------------------------
    # Quick setup
    # --------------------------------------------------------

    if trade_plan:

        st.divider()

        st.markdown(
            f"### 🎯 {strategy_mode} Quick Setup"
        )

        q1, q2, q3, q4 = st.columns(
            4,
            gap="small",
        )

        with q1:

            st.metric(
                "Entry",
                f"₹{fmt(trade_plan['entry'])}",
            )

        with q2:

            st.metric(
                "Stop Loss",
                f"₹{fmt(trade_plan['stop_loss'])}",
            )

        with q3:

            st.metric(
                "Target 1",
                f"₹{fmt(trade_plan['target1'])}",
            )

        with q4:

            st.metric(
                "Target 2",
                f"₹{fmt(trade_plan['target2'])}",
            )


# ============================================================
# TAB 2 - MOVING AVERAGES
# ============================================================

with tabs[1]:

    st.subheader(
        "📈 Moving Average Analysis"
    )

    ma_columns = [
        ("SMA 20", "SMA_20"),
        ("SMA 50", "SMA_50"),
        ("EMA 20", "EMA_20"),
        ("EMA 50", "EMA_50"),
    ]

    available = [
        item
        for item in ma_columns
        if item[1] in chart_df.columns
    ]

    if available:

        cols = st.columns(
            len(available),
            gap="small",
        )

        for col, (
            label,
            column,
        ) in zip(
            cols,
            available,
        ):

            with col:

                st.metric(
                    label,
                    fmt(
                        latest_value(
                            chart_df,
                            column,
                        )
                    ),
                    help=get_indicator_tooltip(
                        label
                    ),
                )

    st.divider()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["Close"],
            name="Close",
            mode="lines",
        )
    )

    for label, column in ma_columns:

        if column in chart_df.columns:

            fig.add_trace(
                go.Scatter(
                    x=chart_df.index,
                    y=chart_df[column],
                    name=label,
                    mode="lines",
                )
            )

    fig.update_layout(
        title="Price vs Moving Averages",
        height=550,
        autosize=True,
        hovermode="x unified",
        margin=dict(
            l=40,
            r=20,
            t=60,
            b=40,
        ),
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "responsive": True,
            "displaylogo": False,
            "scrollZoom": True,
        },
    )

    close = latest_value(
        chart_df,
        "Close",
    )

    sma20 = latest_value(
        chart_df,
        "SMA_20",
    )

    sma50 = latest_value(
        chart_df,
        "SMA_50",
    )

    ema20 = latest_value(
        chart_df,
        "EMA_20",
    )

    ema50 = latest_value(
        chart_df,
        "EMA_50",
    )

    st.markdown(
        "### 📌 Trend Interpretation"
    )

    if (
        close is not None
        and sma20 is not None
        and sma50 is not None
    ):

        if (
            close > sma20
            and sma20 > sma50
        ):

            st.success(
                "Bullish MA structure: Price > SMA 20 > SMA 50."
            )

        elif (
            close < sma20
            and sma20 < sma50
        ):

            st.error(
                "Bearish MA structure: Price < SMA 20 < SMA 50."
            )

        else:

            st.info(
                "Moving averages are mixed."
            )

    if (
        ema20 is not None
        and ema50 is not None
    ):

        if ema20 > ema50:

            st.success(
                "EMA 20 is above EMA 50 — positive short-term momentum."
            )

        else:

            st.warning(
                "EMA 20 is below EMA 50 — negative short-term momentum."
            )


# ============================================================
# TAB 3 - MOMENTUM
# ============================================================

with tabs[2]:

    st.subheader(
        "⚡ Momentum Analysis"
    )

    rsi = latest_value(
        chart_df,
        "RSI",
    )

    macd = latest_value(
        chart_df,
        "MACD",
    )

    macd_signal = latest_value(
        chart_df,
        "MACD_Signal",
    )

    macd_hist = latest_value(
        chart_df,
        "MACD_Histogram",
    )

    momentum = latest_value(
        chart_df,
        "Momentum",
    )

    m1, m2, m3, m4 = st.columns(
        4,
        gap="small",
    )

    with m1:

        st.metric(
            "RSI",
            fmt(rsi, 1),
            help=get_indicator_tooltip("RSI"),
        )

    with m2:

        st.metric(
            "MACD",
            fmt(macd),
            help=get_indicator_tooltip("MACD"),
        )

    with m3:

        st.metric(
            "MACD Signal",
            fmt(macd_signal),
        )

    with m4:

        st.metric(
            "Momentum",
            fmt(momentum),
            help=get_indicator_tooltip("Momentum"),
        )

    if "RSI" in chart_df.columns:

        st.markdown(
            "### RSI"
        )

        fig_rsi = go.Figure()

        fig_rsi.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["RSI"],
                mode="lines",
                name="RSI",
            )
        )

        fig_rsi.add_hline(
            y=70,
            line_dash="dash",
        )

        fig_rsi.add_hline(
            y=50,
            line_dash="dot",
        )

        fig_rsi.add_hline(
            y=30,
            line_dash="dash",
        )

        fig_rsi.update_yaxes(
            range=[0, 100]
        )

        fig_rsi.update_layout(
            height=350,
            hovermode="x unified",
        )

        st.plotly_chart(
            fig_rsi,
            width="stretch",
            config={
                "responsive": True,
                "displaylogo": False,
            },
        )

    if rsi is not None:

        if rsi >= 70:

            st.warning(
                f"RSI {rsi:.1f}: overbought zone. "
                "Avoid chasing unless price action confirms continuation."
            )

        elif rsi <= 30:

            st.info(
                f"RSI {rsi:.1f}: oversold zone. "
                "Look for reversal confirmation."
            )

        elif rsi >= 50:

            st.success(
                f"RSI {rsi:.1f}: bullish momentum zone."
            )

        else:

            st.warning(
                f"RSI {rsi:.1f}: weaker momentum."
            )

    if (
        "MACD" in chart_df.columns
        and "MACD_Signal" in chart_df.columns
    ):

        st.markdown(
            "### MACD"
        )

        fig_macd = go.Figure()

        fig_macd.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["MACD"],
                name="MACD",
                mode="lines",
            )
        )

        fig_macd.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["MACD_Signal"],
                name="Signal",
                mode="lines",
            )
        )

        if "MACD_Histogram" in chart_df.columns:

            fig_macd.add_trace(
                go.Bar(
                    x=chart_df.index,
                    y=chart_df["MACD_Histogram"],
                    name="Histogram",
                )
            )

        fig_macd.add_hline(
            y=0,
            line_dash="dot",
        )

        fig_macd.update_layout(
            height=400,
            hovermode="x unified",
        )

        st.plotly_chart(
            fig_macd,
            width="stretch",
            config={
                "responsive": True,
                "displaylogo": False,
            },
        )


# ============================================================
# TAB 4 - VOLATILITY
# ============================================================

with tabs[3]:

    st.subheader(
        "📊 Volatility Analysis"
    )

    atr = latest_value(
        chart_df,
        "ATR",
    )

    bb_upper = latest_value(
        chart_df,
        "BB_Upper",
    )

    bb_middle = latest_value(
        chart_df,
        "BB_Middle",
    )

    bb_lower = latest_value(
        chart_df,
        "BB_Lower",
    )

    v1, v2, v3, v4 = st.columns(
        4,
        gap="small",
    )

    with v1:

        st.metric(
            "ATR",
            fmt(atr),
            help=get_indicator_tooltip("ATR"),
        )

    with v2:

        st.metric(
            "BB Upper",
            fmt(bb_upper),
        )

    with v3:

        st.metric(
            "BB Middle",
            fmt(bb_middle),
        )

    with v4:

        st.metric(
            "BB Lower",
            fmt(bb_lower),
        )

    if all(
        column in chart_df.columns
        for column in [
            "BB_Upper",
            "BB_Middle",
            "BB_Lower",
        ]
    ):

        st.markdown(
            "### Bollinger Bands"
        )

        fig_bb = go.Figure()

        fig_bb.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["Close"],
                name="Close",
                mode="lines",
            )
        )

        fig_bb.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["BB_Upper"],
                name="Upper",
                mode="lines",
            )
        )

        fig_bb.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["BB_Middle"],
                name="Middle",
                mode="lines",
            )
        )

        fig_bb.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["BB_Lower"],
                name="Lower",
                mode="lines",
            )
        )

        fig_bb.update_layout(
            height=500,
            hovermode="x unified",
        )

        st.plotly_chart(
            fig_bb,
            width="stretch",
            config={
                "responsive": True,
                "displaylogo": False,
            },
        )

    if "ATR" in chart_df.columns:

        st.markdown(
            "### Average True Range"
        )

        fig_atr = go.Figure()

        fig_atr.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["ATR"],
                mode="lines",
                name="ATR",
            )
        )

        fig_atr.update_layout(
            height=350,
            hovermode="x unified",
        )

        st.plotly_chart(
            fig_atr,
            width="stretch",
            config={
                "responsive": True,
                "displaylogo": False,
            },
        )

    if (
        current_price is not None
        and atr is not None
        and current_price != 0
    ):

        atr_pct = (
            atr / current_price
        ) * 100

        st.info(
            f"ATR is approximately {atr_pct:.2f}% "
            "of the current price. Higher ATR generally "
            "means wider stop-loss requirements."
        )


# ============================================================
# TAB 5 - INTRADAY
# ============================================================

with tabs[4]:

    st.subheader(
        "💹 Intraday Analysis"
    )

    i1, i2, i3, i4 = st.columns(
        4,
        gap="small",
    )

    vwap = latest_value(
        chart_df,
        "VWAP",
    )

    supertrend = latest_value(
        chart_df,
        "Supertrend",
    )

    volume_ratio = latest_value(
        chart_df,
        "Volume_Ratio",
    )

    with i1:

        st.metric(
            "Price",
            f"₹{fmt(current_price)}",
        )

    with i2:

        st.metric(
            "VWAP",
            f"₹{fmt(vwap)}",
            help=get_indicator_tooltip("VWAP"),
        )

    with i3:

        st.metric(
            "Supertrend",
            f"₹{fmt(supertrend)}",
            help=get_indicator_tooltip("Supertrend"),
        )

    with i4:

        st.metric(
            "Volume Ratio",
            fmt(volume_ratio),
            help=get_indicator_tooltip("Volume Ratio"),
        )

    st.markdown(
        "### 📌 Intraday Bias"
    )

    bullish = 0
    bearish = 0

    if (
        current_price is not None
        and vwap is not None
    ):

        if current_price > vwap:
            bullish += 1
        else:
            bearish += 1

    if (
        current_price is not None
        and supertrend is not None
    ):

        if current_price > supertrend:
            bullish += 1
        else:
            bearish += 1

    if rsi is not None:

        if rsi >= 50:
            bullish += 1
        else:
            bearish += 1

    if (
        macd is not None
        and macd_signal is not None
    ):

        if macd > macd_signal:
            bullish += 1
        else:
            bearish += 1

    if bullish > bearish:

        st.success(
            f"🟢 Bullish intraday bias "
            f"({bullish} vs {bearish} factors)."
        )

    elif bearish > bullish:

        st.error(
            f"🔴 Bearish intraday bias "
            f"({bearish} vs {bullish} factors)."
        )

    else:

        st.info(
            "🟡 Neutral intraday bias."
        )

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=chart_df.index,
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            name="Price",
        )
    )

    if "VWAP" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["VWAP"],
                mode="lines",
                name="VWAP",
            )
        )

    if "Supertrend" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["Supertrend"],
                mode="lines",
                name="Supertrend",
            )
        )

    fig.update_layout(
        height=600,
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "responsive": True,
            "displaylogo": False,
            "scrollZoom": True,
        },
    )

    st.markdown(
        "### 🕐 Intraday Conditions"
    )

    if (
        current_price is not None
        and vwap is not None
    ):

        if current_price > vwap:

            st.success(
                "Price is above VWAP — buyers have the intraday advantage."
            )

        else:

            st.warning(
                "Price is below VWAP — sellers have the intraday advantage."
            )

    if (
        volume_ratio is not None
        and volume_ratio >= 1.5
    ):

        st.success(
            f"Volume spike detected: "
            f"{volume_ratio:.2f}x reference volume."
        )


# ============================================================
# TAB 6 - CANDLESTICK
# ============================================================

with tabs[5]:

    st.subheader(
        "🕯️ Candlestick Analysis"
    )

    candle = detect_candlestick_pattern(
        chart_df
    )

    p1, p2 = st.columns(
        2,
        gap="medium",
    )

    with p1:

        st.metric(
            "Detected Pattern",
            candle["pattern"],
        )

    with p2:

        st.metric(
            "Pattern Bias",
            candle["bias"],
        )

    if candle["bias"] == "Bullish":

        st.success(
            "🟢 Bullish pattern detected"
        )

    elif candle["bias"] == "Bearish":

        st.error(
            "🔴 Bearish pattern detected"
        )

    else:

        st.info(
            "🟡 Neutral / indecision pattern"
        )

    st.write(
        candle["description"]
    )

    st.markdown(
        "### Price Action"
    )

    candle_df = chart_df.tail(120)

    fig = go.Figure()

    if graph_type == "Heikin Ashi":

        fig.add_trace(
            go.Candlestick(
                x=candle_df.index,
                open=candle_df["HA_Open"],
                high=candle_df["HA_High"],
                low=candle_df["HA_Low"],
                close=candle_df["HA_Close"],
                name="Heikin Ashi",
            )
        )

    elif graph_type == "OHLC":

        fig.add_trace(
            go.Ohlc(
                x=candle_df.index,
                open=candle_df["Open"],
                high=candle_df["High"],
                low=candle_df["Low"],
                close=candle_df["Close"],
                name="OHLC",
            )
        )

    elif graph_type == "Line":

        fig.add_trace(
            go.Scatter(
                x=candle_df.index,
                y=candle_df["Close"],
                mode="lines",
                name="Close",
            )
        )

    else:

        fig.add_trace(
            go.Candlestick(
                x=candle_df.index,
                open=candle_df["Open"],
                high=candle_df["High"],
                low=candle_df["Low"],
                close=candle_df["Close"],
                name="Candlestick",
            )
        )

    fig.update_layout(
        height=600,
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "responsive": True,
            "displaylogo": False,
            "scrollZoom": True,
        },
    )

    with st.expander(
        "📚 Common Candlestick Patterns"
    ):

        pattern_table = pd.DataFrame(
            [
                [
                    "Bullish Engulfing",
                    "Bullish",
                    "Potential reversal / buying pressure",
                ],
                [
                    "Bearish Engulfing",
                    "Bearish",
                    "Potential reversal / selling pressure",
                ],
                [
                    "Hammer",
                    "Bullish",
                    "Lower-price rejection",
                ],
                [
                    "Shooting Star",
                    "Bearish",
                    "Higher-price rejection",
                ],
                [
                    "Doji",
                    "Neutral",
                    "Market indecision",
                ],
            ],
            columns=[
                "Pattern",
                "Bias",
                "Meaning",
            ],
        )

        st.dataframe(
            pattern_table,
            width="stretch",
            hide_index=True,
        )


# ============================================================
# TAB 7 - TRADE SETUP
# ============================================================

with tabs[6]:

    st.subheader(
        f"🎯 {strategy_mode} Trade Setup"
    )

    st.caption(
        "Levels are rule-based reference levels derived "
        "from technical indicators and ATR."
    )

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    st.markdown(
        "## 🧠 Trade Decision"
    )

    show_recommendation_card(
        stock,
        strategy_mode,
        signal_data,
        trade_plan,
    )

    if trade_plan:

        st.divider()

        t1, t2, t3, t4, t5 = st.columns(
            5,
            gap="small",
        )

        with t1:

            st.metric(
                "Entry / Trigger",
                f"₹{fmt(trade_plan['entry'])}",
            )

        with t2:

            st.metric(
                "Stop Loss",
                f"₹{fmt(trade_plan['stop_loss'])}",
            )

        with t3:

            st.metric(
                "Target 1",
                f"₹{fmt(trade_plan['target1'])}",
            )

        with t4:

            st.metric(
                "Target 2",
                f"₹{fmt(trade_plan['target2'])}",
            )

        with t5:

            if trade_plan["entry"]:

                risk_pct = (
                    trade_plan["risk"]
                    / trade_plan["entry"]
                ) * 100

            else:

                risk_pct = 0

            st.metric(
                "Risk",
                f"{risk_pct:.2f}%",
            )

        # ----------------------------------------------------
        # Entry zone
        # ----------------------------------------------------

        st.markdown(
            "### 🎯 Entry Zone"
        )

        z1, z2 = st.columns(
            2,
            gap="small",
        )

        with z1:

            st.metric(
                "Zone Low",
                f"₹{fmt(trade_plan['buy_zone_low'])}",
            )

        with z2:

            st.metric(
                "Zone High",
                f"₹{fmt(trade_plan['buy_zone_high'])}",
            )

        # ----------------------------------------------------
        # Risk reward
        # ----------------------------------------------------

        st.markdown(
            "### ⚖️ Risk / Reward"
        )

        if trade_plan["risk"] > 0:

            rr1 = (
                trade_plan["reward1"]
                / trade_plan["risk"]
            )

            rr2 = (
                trade_plan["reward2"]
                / trade_plan["risk"]
            )

            r1, r2 = st.columns(
                2,
                gap="small",
            )

            with r1:

                st.metric(
                    "Target 1 R:R",
                    f"1 : {rr1:.2f}",
                )

            with r2:

                st.metric(
                    "Target 2 R:R",
                    f"1 : {rr2:.2f}",
                )

        # ----------------------------------------------------
        # Buy / sell conditions
        # ----------------------------------------------------

        st.markdown(
            "### 🕐 When to Buy / Sell"
        )

        with st.container(
            border=True
        ):

            st.write(
                "🟢 **Entry condition:** "
                + trade_plan[
                    "entry_condition"
                ]
            )

            st.write(
                "🔴 **Exit condition:** "
                + trade_plan[
                    "exit_condition"
                ]
            )

        # ----------------------------------------------------
        # Strategy checklist
        # ----------------------------------------------------

        st.markdown(
            "### ✅ Confirmation Checklist"
        )

        if strategy_mode == "Intraday":

            checks = [
                (
                    "VWAP",
                    current_price is not None
                    and vwap is not None
                    and current_price > vwap,
                ),
                (
                    "Supertrend",
                    current_price is not None
                    and supertrend is not None
                    and current_price > supertrend,
                ),
                (
                    "RSI",
                    rsi is not None
                    and rsi >= 50,
                ),
                (
                    "MACD",
                    macd is not None
                    and macd_signal is not None
                    and macd > macd_signal,
                ),
                (
                    "Volume",
                    volume_ratio is not None
                    and volume_ratio >= 1.5,
                ),
            ]

        elif strategy_mode == "Swing":

            checks = [
                (
                    "SMA Trend",
                    sma20 is not None
                    and sma50 is not None
                    and sma20 > sma50,
                ),
                (
                    "EMA Trend",
                    ema20 is not None
                    and ema50 is not None
                    and ema20 > ema50,
                ),
                (
                    "MACD",
                    macd is not None
                    and macd_signal is not None
                    and macd > macd_signal,
                ),
                (
                    "RSI",
                    rsi is not None
                    and rsi >= 50,
                ),
                (
                    "Momentum",
                    momentum is not None
                    and momentum > 0,
                ),
            ]

        else:

            checks = [
                (
                    "SMA Trend",
                    sma20 is not None
                    and sma50 is not None
                    and sma20 > sma50,
                ),
                (
                    "EMA Trend",
                    ema20 is not None
                    and ema50 is not None
                    and ema20 > ema50,
                ),
                (
                    "Supertrend",
                    current_price is not None
                    and supertrend is not None
                    and current_price > supertrend,
                ),
                (
                    "MACD",
                    macd is not None
                    and macd_signal is not None
                    and macd > macd_signal,
                ),
                (
                    "Momentum",
                    momentum is not None
                    and momentum > 0,
                ),
            ]

        for label, passed in checks:

            if passed:

                st.success(
                    f"✓ {label}: Confirmed"
                )

            else:

                st.warning(
                    f"• {label}: Not confirmed"
                )

    with st.expander(
        "ℹ️ How this strategy mode works"
    ):

        if strategy_mode == "Intraday":

            st.write(
                """
                **Intraday**

                Designed for shorter-term setups.

                - VWAP receives higher importance.
                - Supertrend confirms direction.
                - RSI and MACD confirm momentum.
                - Volume confirmation is preferred.
                - ATR provides the stop-loss distance.
                - Avoid chasing large candles.
                """
            )

        elif strategy_mode == "Swing":

            st.write(
                """
                **Swing**

                Designed for multi-day positions.

                - Moving-average structure receives more importance.
                - EMA trend confirms momentum.
                - MACD and RSI provide momentum confirmation.
                - Wider ATR-based stop-loss is used.
                - Targets are larger than intraday setups.
                """
            )

        else:

            st.write(
                """
                **Long Term**

                Designed for broader trend positioning.

                - SMA/EMA trend structure receives highest importance.
                - Supertrend and momentum provide confirmation.
                - VWAP has very little influence.
                - Wider ATR-based risk allowance is used.
                - Short-term fluctuations should receive less importance.
                """
            )


# ============================================================
# TAB 8 - INDICATOR GUIDE
# ============================================================

with tabs[7]:

    st.subheader(
        "📚 Technical Indicator Guide"
    )

    st.caption(
        "Use this section to understand what each indicator "
        "does and how it can be interpreted."
    )

    guide_mapping = {

        "SMA 20": "SMA",
        "SMA 50": "SMA",

        "EMA 20": "EMA",
        "EMA 50": "EMA",

        "Bollinger Bands": "Bollinger Bands",

        "VWAP": "VWAP",

        "Supertrend": "Supertrend",

        "RSI": "RSI",

        "MACD": "MACD",

        "ATR": "ATR",

        "Momentum": "Momentum",

        "Volume": "Volume",

        "Volume Ratio": "Volume Ratio",
    }

    for indicator in ALL_INDICATORS:

        guide_key = guide_mapping.get(
            indicator,
            indicator,
        )

        with st.expander(
            f"ℹ️ {indicator}"
        ):

            try:

                show_indicator_guide(
                    st,
                    guide_key,
                )

            except Exception:

                st.write(
                    get_indicator_tooltip(
                        guide_key
                    )
                )


# ============================================================
# RECENT MARKET DATA
# ============================================================

st.divider()

with st.expander(
    "📋 Recent Market Data"
):

    display_columns = [
        column
        for column in [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",

            "SMA_20",
            "SMA_50",

            "EMA_20",
            "EMA_50",

            "RSI",

            "MACD",
            "MACD_Signal",
            "MACD_Histogram",

            "VWAP",
            "Supertrend",

            "ATR",

            "BB_Upper",
            "BB_Middle",
            "BB_Lower",

            "Momentum",
            "Volume_Ratio",
        ]
        if column in chart_df.columns
    ]

    if display_columns:

        recent = chart_df[
            display_columns
        ].tail(30)

        st.dataframe(
            recent,
            width="stretch",
            height=450,
        )

    else:

        st.info(
            "No indicator data available."
        )


# ============================================================
# FINAL DISCLAIMER
# ============================================================

st.divider()

st.warning(
    """
    ⚠️ **Technical-analysis disclaimer**

    Strong Buy / Buy / Hold / Sell / Strong Sell classifications
    are rule-based technical signals generated from available
    indicators. They are not guaranteed predictions of future
    returns.

    Entry zones, stop losses and targets are reference levels
    calculated from technical indicators and ATR. They should not
    be treated as guaranteed buy or sell prices.

    Always validate the setup against current price action,
    support/resistance, liquidity, broader market conditions,
    news/events and your own risk-management rules.

    A technical score or recommendation does not guarantee profit.
    """
)