# pages/03_📉_Technical_Analysis.py

import streamlit as st
import inspect
import streamlit.components.v1 as components
from html import escape
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


# ============================================================
# CONSTANTS
# ============================================================

TREND_INDICATORS = [
    "SMA 20",
    "SMA 50",
    "EMA 20",
    "EMA 50",
    "VWAP",
    "Supertrend",
]

MOMENTUM_INDICATORS = [
    "RSI",
    "MACD",
    "Momentum",
]

VOLATILITY_INDICATORS = [
    "Bollinger Bands",
    "ATR",
]

VOLUME_INDICATORS = [
    "Volume",
    "Volume Ratio",
]

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
    TREND_INDICATORS
    + [
        x for x in MOMENTUM_INDICATORS
        if x not in TREND_INDICATORS
    ]
    + [
        x for x in VOLATILITY_INDICATORS
        if x not in TREND_INDICATORS
        and x not in MOMENTUM_INDICATORS
    ]
    + [
        x for x in VOLUME_INDICATORS
        if x not in TREND_INDICATORS
        and x not in MOMENTUM_INDICATORS
        and x not in VOLATILITY_INDICATORS
    ]
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

TIMEFRAMES = [
    "Intraday",
    "Swing",
    "Long Term",
]

# Candle intervals offered by the chart. Actual intraday data is only available
# when services.stock_service.analyze_stock supports an interval argument.
CANDLE_INTERVALS = [
    "1 minute",
    "2 minutes",
    "5 minutes",
    "15 minutes",
    "30 minutes",
    "60 minutes",
    "90 minutes",
    "1 day",
    "1 week",
    "1 month",
]
INTERVAL_TO_PROVIDER = {
    "1 minute": "1m",
    "2 minutes": "2m",
    "5 minutes": "5m",
    "15 minutes": "15m",
    "30 minutes": "30m",
    "60 minutes": "60m",
    "90 minutes": "90m",
    "1 day": "1d",
    "1 week": "1wk",
    "1 month": "1mo",
}

PERIODS = [
    "1 Day",
    "5 Days",
    "10 Days",
    "30 Days",
    "60 Days",
    "90 Days",
    "180 Days",
    "1 Year",
    "2 Years",
    "5 Years",
]

GRAPH_TYPES = [
    "Heikin Ashi",
    "Candlestick",
    "OHLC",
    "Line",
]


# ============================================================
# SESSION STATE
# ============================================================

SESSION_DEFAULTS = {
    "technical_favorite_1": "",
    "technical_favorite_2": "",
    "technical_favorite_3": "",
    "technical_selected_indicators": DEFAULT_INDICATORS.copy(),
    "technical_strategy_mode": "Intraday",
    "technical_graph_type": "Heikin Ashi",
    "technical_period": "90 Days",
    "technical_candle_interval": "1 day",
}

for key, value in SESSION_DEFAULTS.items():

    if key not in st.session_state:

        if isinstance(value, list):
            st.session_state[key] = value.copy()
        else:
            st.session_state[key] = value


# ============================================================
# RESPONSIVE CSS
# ============================================================

st.markdown(
    """
<style>

/* ==========================================================
   GLOBAL
   ========================================================== */

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}


/* ==========================================================
   TITLES
   ========================================================== */

.main-title {
    font-size: clamp(1.35rem, 2.5vw, 2rem);
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 0.25rem;
}

.sub-title {
    color: #6b7280;
    font-size: clamp(0.82rem, 1.5vw, 0.98rem);
    margin-bottom: 1rem;
}

.section-title {
    font-size: clamp(1.05rem, 2vw, 1.3rem);
    font-weight: 750;
    margin-top: 1rem;
    margin-bottom: 0.75rem;
}


/* ==========================================================
   CONTROL AREA
   ========================================================== */

.control-panel {
    border: 1px solid rgba(128,128,128,0.20);
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 14px;
    background: rgba(128,128,128,0.025);
}

.control-heading {
    font-size: 1.05rem;
    font-weight: 750;
    margin-bottom: 10px;
}


/* ==========================================================
   INDICATOR CHIP AREA
   ========================================================== */

.indicator-chip-wrapper {
    width: 100%;
    box-sizing: border-box;
    padding: 4px 0 2px 0;
}

.indicator-chip-container {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 7px;
    width: 100%;
    max-width: 100%;
}

.indicator-chip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    max-width: 210px;
    min-height: 30px;
    padding: 5px 11px;
    border-radius: 999px;
    border: 1px solid rgba(80,120,200,0.25);
    background: rgba(80,120,200,0.08);
    color: inherit;
    font-size: 0.82rem;
    line-height: 1.15;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    box-sizing: border-box;
}

.indicator-chip:hover {
    background: rgba(80,120,200,0.14);
}

.indicator-count {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 28px;
    padding: 4px 10px;
    border-radius: 999px;
    background: rgba(128,128,128,0.10);
    font-size: 0.78rem;
    font-weight: 650;
}


/* ==========================================================
   INDICATOR CATEGORY BOX
   ========================================================== */

.indicator-category {
    border: 1px solid rgba(128,128,128,0.16);
    border-radius: 12px;
    padding: 12px;
    min-height: 100%;
}

.indicator-category-title {
    font-size: 0.88rem;
    font-weight: 750;
    margin-bottom: 5px;
}

.indicator-category-help {
    font-size: 0.76rem;
    color: #6b7280;
    margin-bottom: 8px;
}


/* ==========================================================
   FAVORITES
   ========================================================== */

.favorite-container {
    border: 1px solid rgba(128,128,128,0.16);
    border-radius: 14px;
    padding: 14px;
    margin-top: 4px;
}

.favorite-title {
    font-size: 0.95rem;
    font-weight: 700;
    margin-bottom: 8px;
}


/* ==========================================================
   RECOMMENDATION
   ========================================================== */

.recommendation-card {
    border-radius: 16px;
    padding: 22px;
    margin: 12px 0 20px 0;
    border: 1px solid rgba(128,128,128,0.20);
    box-shadow: 0 3px 14px rgba(0,0,0,0.08);
}

.recommendation-title {
    font-size: 2rem;
    font-weight: 900;
}

.recommendation-subtitle {
    margin-top: 6px;
    font-size: 0.95rem;
    opacity: 0.85;
}


/* ==========================================================
   FACTORS
   ========================================================== */

.factor-card {
    border: 1px solid rgba(128,128,128,0.18);
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 8px;
}

.factor-positive {
    border-left: 4px solid #169c5a;
}

.factor-negative {
    border-left: 4px solid #d14343;
}


/* ==========================================================
   TRADE SETUP
   ========================================================== */

.trade-level {
    border: 1px solid rgba(128,128,128,0.20);
    border-radius: 12px;
    padding: 14px;
    min-height: 90px;
    background: rgba(128,128,128,0.035);
}

.setup-box {
    border: 1px solid rgba(128,128,128,0.2);
    border-radius: 14px;
    padding: 18px;
    margin-top: 12px;
}

.info-box {
    border-left: 5px solid #3685d1;
    background: rgba(54,133,209,0.08);
    padding: 12px 16px;
    border-radius: 8px;
}


/* ==========================================================
   MOBILE
   ========================================================== */

@media (max-width: 900px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .recommendation-card {
        padding: 16px;
    }

    .recommendation-title {
        font-size: 1.55rem;
    }

    .indicator-chip {
        max-width: 170px;
    }
}


@media (max-width: 600px) {

    .block-container {
        padding-left: 0.7rem;
        padding-right: 0.7rem;
    }

    .control-panel {
        padding: 12px;
        border-radius: 12px;
    }

    .indicator-chip {
        max-width: 145px;
        font-size: 0.76rem;
        padding: 5px 9px;
    }

    .section-title {
        margin-top: 0.8rem;
    }

    .recommendation-card {
        padding: 13px;
        border-radius: 12px;
    }
}


/* ==========================================================
   STREAMLIT MULTISELECT
   ========================================================== */

/*
   Give the indicator selector enough vertical room.
   This is intentionally NOT placed inside a narrow column.
*/

div[data-baseweb="select"] {
    min-height: 42px;
}

div[data-baseweb="select"] > div {
    min-height: 42px;
}


/* ==========================================================
   EXPANDER
   ========================================================== */

div[data-testid="stExpander"] {
    border-radius: 14px;
}


/* ==========================================================
   PLOTLY
   ========================================================== */

.js-plotly-plot,
.plot-container {
    width: 100% !important;
    max-width: 100% !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def normalize_columns(df):

    if df is None or df.empty:
        return pd.DataFrame()

    result = df.copy()

    rename_map = {}

    for col in result.columns:

        clean = str(col).strip()

        normalized = (
            clean
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

        mapping = {
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "adj_close": "Adj Close",
            "volume": "Volume",
            "date": "Date",
            "datetime": "Date",

            "sma_20": "SMA_20",
            "sma20": "SMA_20",
            "sma_50": "SMA_50",
            "sma50": "SMA_50",

            "ema_20": "EMA_20",
            "ema20": "EMA_20",
            "ema_50": "EMA_50",
            "ema50": "EMA_50",

            "rsi": "RSI",

            "macd": "MACD",
            "macd_signal": "MACD_Signal",
            "macd_hist": "MACD_Hist",

            "atr": "ATR",
            "momentum": "Momentum",

            "vwap": "VWAP",
            "supertrend": "Supertrend",

            "bb_upper": "BB_Upper",
            "bb_middle": "BB_Middle",
            "bb_lower": "BB_Lower",

            "volume_ratio": "Volume_Ratio",
        }

        if normalized in mapping:
            rename_map[col] = mapping[normalized]

    return result.rename(
        columns=rename_map
    )


def prepare_datetime_index(df):

    if df is None or df.empty:
        return df

    result = df.copy()

    if not isinstance(
        result.index,
        pd.DatetimeIndex,
    ):

        if "Date" in result.columns:

            result["Date"] = pd.to_datetime(
                result["Date"],
                errors="coerce",
            )

            result = result.dropna(
                subset=["Date"]
            )

            result = result.set_index(
                "Date"
            )

    try:
        result = result.sort_index()
    except Exception:
        pass

    return result


def prepare_numeric_columns(df):

    if df is None or df.empty:
        return df

    result = df.copy()

    numeric_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Adj Close",
        "Volume",

        "SMA_20",
        "SMA_50",
        "EMA_20",
        "EMA_50",

        "RSI",

        "MACD",
        "MACD_Signal",
        "MACD_Hist",

        "ATR",
        "Momentum",
        "VWAP",
        "Supertrend",

        "BB_Upper",
        "BB_Middle",
        "BB_Lower",

        "Volume_Ratio",
    ]

    for col in numeric_columns:

        if col in result.columns:

            result[col] = pd.to_numeric(
                result[col],
                errors="coerce",
            )

    return result


def latest_value(
    df,
    column,
    default=np.nan,
):

    if (
        df is None
        or df.empty
        or column not in df.columns
    ):
        return default

    series = pd.to_numeric(
        df[column],
        errors="coerce",
    ).dropna()

    if series.empty:
        return default

    return float(series.iloc[-1])


def previous_value(
    df,
    column,
    default=np.nan,
):

    if (
        df is None
        or df.empty
        or column not in df.columns
    ):
        return default

    series = pd.to_numeric(
        df[column],
        errors="coerce",
    ).dropna()

    if len(series) < 2:
        return default

    return float(series.iloc[-2])


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
    decimals=2,
):

    if value is None:
        return "N/A"

    try:

        if pd.isna(value):
            return "N/A"

        return f"{float(value):.{decimals}f}%"

    except Exception:

        return "N/A"


def safe_divide(
    a,
    b,
    default=0.0,
):

    try:

        if (
            b is None
            or pd.isna(b)
            or float(b) == 0
        ):
            return default

        return float(a) / float(b)

    except Exception:

        return default


# ============================================================
# HEIKIN ASHI
# ============================================================

def calculate_heikin_ashi(df):

    if df is None or df.empty:
        return pd.DataFrame()

    required = [
        "Open",
        "High",
        "Low",
        "Close",
    ]

    if not all(
        col in df.columns
        for col in required
    ):
        return df.copy()

    result = df.copy()

    ha = pd.DataFrame(
        index=result.index
    )

    ha["Close"] = (
        result["Open"]
        + result["High"]
        + result["Low"]
        + result["Close"]
    ) / 4

    ha_open = np.zeros(
        len(result)
    )

    if len(result) > 0:

        ha_open[0] = (
            result["Open"].iloc[0]
            + result["Close"].iloc[0]
        ) / 2

    for i in range(1, len(result)):

        ha_open[i] = (
            ha_open[i - 1]
            + ha["Close"].iloc[i - 1]
        ) / 2

    ha["Open"] = ha_open

    ha["High"] = pd.concat(
        [
            result["High"],
            ha["Open"],
            ha["Close"],
        ],
        axis=1,
    ).max(axis=1)

    ha["Low"] = pd.concat(
        [
            result["Low"],
            ha["Open"],
            ha["Close"],
        ],
        axis=1,
    ).min(axis=1)

    return ha


# ============================================================
# LOCAL INDICATOR CALCULATION
# ============================================================

def calculate_missing_indicators(df):
    """Calculate chart indicators locally so selector changes can render them.

    Existing service-calculated columns are preserved where present. The
    calculations use OHLCV columns and work with daily or intraday candles.
    """
    if df is None or df.empty or "Close" not in df.columns:
        return df

    result = df.copy()
    close = pd.to_numeric(result["Close"], errors="coerce")
    high = pd.to_numeric(result["High"], errors="coerce") if "High" in result else close
    low = pd.to_numeric(result["Low"], errors="coerce") if "Low" in result else close
    volume = pd.to_numeric(result["Volume"], errors="coerce") if "Volume" in result else pd.Series(0.0, index=result.index)

    for period in (20, 50):
        sma_col = f"SMA_{period}"
        ema_col = f"EMA_{period}"
        if sma_col not in result.columns:
            result[sma_col] = close.rolling(period, min_periods=1).mean()
        if ema_col not in result.columns:
            result[ema_col] = close.ewm(span=period, adjust=False, min_periods=1).mean()

    if "RSI" not in result.columns:
        delta = close.diff()
        gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False, min_periods=14).mean()
        loss = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False, min_periods=14).mean()
        rs = gain / loss.replace(0, np.nan)
        result["RSI"] = 100 - (100 / (1 + rs))
        result.loc[(loss == 0) & (gain > 0), "RSI"] = 100

    if not all(c in result.columns for c in ("MACD", "MACD_Signal", "MACD_Hist")):
        ema12 = close.ewm(span=12, adjust=False, min_periods=1).mean()
        ema26 = close.ewm(span=26, adjust=False, min_periods=1).mean()
        macd = ema12 - ema26
        if "MACD" not in result.columns:
            result["MACD"] = macd
        if "MACD_Signal" not in result.columns:
            result["MACD_Signal"] = macd.ewm(span=9, adjust=False, min_periods=1).mean()
        if "MACD_Hist" not in result.columns:
            result["MACD_Hist"] = result["MACD"] - result["MACD_Signal"]

    if "Momentum" not in result.columns:
        result["Momentum"] = close - close.shift(10)

    if "ATR" not in result.columns:
        previous_close = close.shift(1)
        true_range = pd.concat(
            [(high - low).abs(), (high - previous_close).abs(), (low - previous_close).abs()],
            axis=1,
        ).max(axis=1)
        result["ATR"] = true_range.rolling(14, min_periods=1).mean()

    if not all(c in result.columns for c in ("BB_Upper", "BB_Middle", "BB_Lower")):
        middle = close.rolling(20, min_periods=1).mean()
        std = close.rolling(20, min_periods=1).std(ddof=0).fillna(0)
        if "BB_Upper" not in result.columns:
            result["BB_Upper"] = middle + (2 * std)
        if "BB_Middle" not in result.columns:
            result["BB_Middle"] = middle
        if "BB_Lower" not in result.columns:
            result["BB_Lower"] = middle - (2 * std)

    if "Volume_Ratio" not in result.columns:
        average_volume = volume.rolling(20, min_periods=1).mean().replace(0, np.nan)
        result["Volume_Ratio"] = volume / average_volume

    # Session VWAP resets each trading date when a datetime index is available.
    if "VWAP" not in result.columns:
        typical = (high + low + close) / 3
        if isinstance(result.index, pd.DatetimeIndex):
            session = pd.Series(result.index.date, index=result.index)
            cumulative_pv = (typical * volume).groupby(session).cumsum()
            cumulative_volume = volume.groupby(session).cumsum().replace(0, np.nan)
            result["VWAP"] = cumulative_pv / cumulative_volume
        else:
            result["VWAP"] = (typical * volume).cumsum() / volume.cumsum().replace(0, np.nan)

    if "Supertrend" not in result.columns:
        atr = result["ATR"].fillna(0)
        hl2 = (high + low) / 2
        upper = hl2 + 3 * atr
        lower = hl2 - 3 * atr
        trend = pd.Series(index=result.index, dtype=float)
        direction = pd.Series(index=result.index, dtype=float)
        for i in range(len(result)):
            if i == 0:
                trend.iloc[i] = lower.iloc[i]
                direction.iloc[i] = 1
                continue
            prev_upper = upper.iloc[i - 1]
            prev_lower = lower.iloc[i - 1]
            if close.iloc[i] > prev_upper:
                direction.iloc[i] = 1
            elif close.iloc[i] < prev_lower:
                direction.iloc[i] = -1
            else:
                direction.iloc[i] = direction.iloc[i - 1]
            trend.iloc[i] = lower.iloc[i] if direction.iloc[i] >= 0 else upper.iloc[i]
        result["Supertrend"] = trend

    return result


def load_stock_data_for_interval(stock, interval_label, period_label):
    """Call analyze_stock with interval/period only if its signature supports them."""
    provider_interval = INTERVAL_TO_PROVIDER.get(interval_label, "1d")
    provider_period_map = {
        "1 Day": "1d", "5 Days": "5d", "10 Days": "10d",
        "30 Days": "1mo", "60 Days": "2mo", "90 Days": "3mo",
        "180 Days": "6mo", "1 Year": "1y", "2 Years": "2y", "5 Years": "5y",
    }
    provider_period = provider_period_map.get(period_label, "3mo")
    if provider_interval in {"1m", "2m", "5m", "15m", "30m", "60m", "90m"}:
        # Common free market-data providers restrict intraday history; 1-minute
        # candles are often limited to about 7 days, other intraday intervals to 60 days.
        intraday_period_map = {
            "1 Day": "1d", "5 Days": "5d", "10 Days": "7d",
            "30 Days": "1mo", "60 Days": "60d", "90 Days": "60d",
            "180 Days": "60d", "1 Year": "60d", "2 Years": "60d", "5 Years": "60d",
        }
        provider_period = intraday_period_map.get(period_label, "5d")
        if provider_interval == "1m" and period_label not in {"1 Day", "5 Days"}:
            provider_period = "7d"
    try:
        signature = inspect.signature(analyze_stock)
        parameters = signature.parameters
        accepts_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in parameters.values())
        kwargs = {}
        if "interval" in parameters or accepts_kwargs:
            kwargs["interval"] = provider_interval
        if "period" in parameters or accepts_kwargs:
            kwargs["period"] = provider_period
        return analyze_stock(stock, **kwargs), bool("interval" in kwargs)
    except (TypeError, ValueError):
        # Compatibility fallback for existing services that only accept symbol.
        return analyze_stock(stock), False


# ============================================================
# PERIOD FILTER
# ============================================================

def filter_period(
    df,
    period,
):

    if df is None or df.empty:
        return df

    result = df.copy()

    if not isinstance(
        result.index,
        pd.DatetimeIndex,
    ):
        return result

    days_map = {
        "1 Day": 1,
        "5 Days": 5,
        "10 Days": 10,
        "30 Days": 30,
        "60 Days": 60,
        "90 Days": 90,
        "180 Days": 180,
        "1 Year": 365,
        "2 Years": 730,
        "5 Years": 1825,
    }

    days = days_map.get(
        period
    )

    if days is None:
        return result

    end_date = result.index.max()

    start_date = (
        end_date
        - pd.Timedelta(
            days=days
        )
    )

    return result.loc[
        result.index >= start_date
    ]


# ============================================================
# CANDLESTICK PATTERN
# ============================================================

def detect_candlestick_pattern(df):

    if df is None or len(df) < 2:
        return "Neutral"

    required = [
        "Open",
        "High",
        "Low",
        "Close",
    ]

    if not all(
        col in df.columns
        for col in required
    ):
        return "Neutral"

    last = df.iloc[-1]

    o = float(last["Open"])
    h = float(last["High"])
    l = float(last["Low"])
    c = float(last["Close"])

    body = abs(c - o)

    candle_range = max(
        h - l,
        0.000001,
    )

    upper_wick = (
        h - max(o, c)
    )

    lower_wick = (
        min(o, c) - l
    )

    body_ratio = (
        body / candle_range
    )

    # --------------------------------------------------------
    # Previous candle
    # --------------------------------------------------------

    previous = df.iloc[-2]

    po = float(previous["Open"])
    pc = float(previous["Close"])

    # --------------------------------------------------------
    # Engulfing patterns first
    # --------------------------------------------------------

    if (
        pc < po
        and c > o
        and o <= pc
        and c >= po
    ):

        return "Bullish Engulfing"

    if (
        pc > po
        and c < o
        and o >= pc
        and c <= po
    ):

        return "Bearish Engulfing"

    # --------------------------------------------------------
    # Doji
    # --------------------------------------------------------

    if body_ratio <= 0.10:
        return "Doji"

    # --------------------------------------------------------
    # Hammer
    # --------------------------------------------------------

    if (
        lower_wick >= body * 2
        and upper_wick <= body
        and c >= o
    ):

        return "Hammer"

    # --------------------------------------------------------
    # Inverted Hammer
    # --------------------------------------------------------

    if (
        upper_wick >= body * 2
        and lower_wick <= body
        and c >= o
    ):

        return "Inverted Hammer"

    # --------------------------------------------------------
    # Shooting Star
    # --------------------------------------------------------

    if (
        upper_wick >= body * 2
        and lower_wick <= body
        and c < o
    ):

        return "Shooting Star"

    if c > o:
        return "Bullish Candle"

    if c < o:
        return "Bearish Candle"

    return "Neutral"


# ============================================================
# TECHNICAL SIGNAL ENGINE
# ============================================================

def calculate_technical_signal(
    df,
    timeframe,
):

    score = 50

    bullish_count = 0
    bearish_count = 0

    bullish_reasons = []
    bearish_reasons = []
    warnings = []

    if df is None or df.empty:

        return {
            "score": 50,
            "signal": "HOLD",
            "confidence": "Low",
            "bullish_count": 0,
            "bearish_count": 0,
            "factor_gap": 0,
            "reasons": [
                "Insufficient market data."
            ],
            "bullish_reasons": [],
            "bearish_reasons": [],
            "warnings": [
                "Unable to calculate complete technical analysis."
            ],
            "candlestick": "Neutral",
            "reason": "Insufficient data",
            "action": "Wait for reliable market data.",
            "confirmation": "Wait for additional confirmation.",
        }

    close = latest_value(
        df,
        "Close",
    )

    sma20 = latest_value(
        df,
        "SMA_20",
    )

    sma50 = latest_value(
        df,
        "SMA_50",
    )

    ema20 = latest_value(
        df,
        "EMA_20",
    )

    ema50 = latest_value(
        df,
        "EMA_50",
    )

    vwap = latest_value(
        df,
        "VWAP",
    )

    supertrend = latest_value(
        df,
        "Supertrend",
    )

    rsi = latest_value(
        df,
        "RSI",
    )

    macd = latest_value(
        df,
        "MACD",
    )

    macd_signal = latest_value(
        df,
        "MACD_Signal",
    )

    macd_hist = latest_value(
        df,
        "MACD_Hist",
    )

    bb_middle = latest_value(
        df,
        "BB_Middle",
    )

    momentum = latest_value(
        df,
        "Momentum",
    )

    volume_ratio = latest_value(
        df,
        "Volume_Ratio",
    )

    # ========================================================
    # SMA 20
    # ========================================================

    if not pd.isna(sma20):

        if close > sma20:

            score += 8
            bullish_count += 1

            bullish_reasons.append(
                "Price is above SMA 20, indicating short-term upward trend."
            )

        elif close < sma20:

            score -= 8
            bearish_count += 1

            bearish_reasons.append(
                "Price is below SMA 20, indicating short-term weakness."
            )

    # ========================================================
    # SMA 20 / SMA 50
    # ========================================================

    if (
        not pd.isna(sma20)
        and not pd.isna(sma50)
    ):

        if sma20 > sma50:

            score += 10
            bullish_count += 1

            bullish_reasons.append(
                "SMA 20 is above SMA 50, supporting a bullish trend."
            )

        elif sma20 < sma50:

            score -= 10
            bearish_count += 1

            bearish_reasons.append(
                "SMA 20 is below SMA 50, indicating bearish trend structure."
            )

    # ========================================================
    # EMA 20 / EMA 50
    # ========================================================

    if (
        not pd.isna(ema20)
        and not pd.isna(ema50)
    ):

        if ema20 > ema50:

            score += 8
            bullish_count += 1

            bullish_reasons.append(
                "EMA 20 is above EMA 50, supporting positive momentum."
            )

        elif ema20 < ema50:

            score -= 8
            bearish_count += 1

            bearish_reasons.append(
                "EMA 20 is below EMA 50, indicating negative momentum."
            )

    # ========================================================
    # VWAP
    # ========================================================

    if not pd.isna(vwap):

        if close > vwap:

            score += 8
            bullish_count += 1

            bullish_reasons.append(
                "Price is above VWAP, indicating bullish positioning."
            )

        elif close < vwap:

            score -= 8
            bearish_count += 1

            bearish_reasons.append(
                "Price is below VWAP, indicating bearish positioning."
            )

    elif timeframe == "Intraday":

        warnings.append(
            "VWAP data is unavailable for intraday confirmation."
        )

    # ========================================================
    # SUPERTREND
    # ========================================================

    if not pd.isna(supertrend):

        if close > supertrend:

            score += 10
            bullish_count += 1

            bullish_reasons.append(
                "Price is above Supertrend, indicating bullish trend direction."
            )

        elif close < supertrend:

            score -= 10
            bearish_count += 1

            bearish_reasons.append(
                "Price is below Supertrend, indicating bearish trend direction."
            )

    # ========================================================
    # RSI
    # ========================================================

    if not pd.isna(rsi):

        if 50 <= rsi < 70:

            score += 7
            bullish_count += 1

            bullish_reasons.append(
                f"RSI at {rsi:.1f} supports positive momentum without being overbought."
            )

        elif rsi >= 70:

            score -= 4

            warnings.append(
                f"RSI at {rsi:.1f} is overbought. Avoid chasing extended price."
            )

        elif rsi < 30:

            score += 4

            warnings.append(
                f"RSI at {rsi:.1f} is oversold. Reversal confirmation is required."
            )

        elif 30 <= rsi < 50:

            score -= 4
            bearish_count += 1

            bearish_reasons.append(
                f"RSI at {rsi:.1f} is below 50, showing weak momentum."
            )

    # ========================================================
    # MACD
    # ========================================================

    if (
        not pd.isna(macd)
        and not pd.isna(macd_signal)
    ):

        if macd > macd_signal:

            score += 8
            bullish_count += 1

            bullish_reasons.append(
                "MACD is above its signal line, supporting bullish momentum."
            )

        elif macd < macd_signal:

            score -= 8
            bearish_count += 1

            bearish_reasons.append(
                "MACD is below its signal line, indicating weakening momentum."
            )

    if not pd.isna(macd_hist):

        if macd_hist > 0:

            score += 4
            bullish_count += 1

            bullish_reasons.append(
                "MACD histogram is positive."
            )

        elif macd_hist < 0:

            score -= 4
            bearish_count += 1

            bearish_reasons.append(
                "MACD histogram is negative."
            )

    # ========================================================
    # BOLLINGER
    # ========================================================

    if not pd.isna(bb_middle):

        if close > bb_middle:

            score += 5
            bullish_count += 1

            bullish_reasons.append(
                "Price is above Bollinger middle band."
            )

        elif close < bb_middle:

            score -= 5
            bearish_count += 1

            bearish_reasons.append(
                "Price is below Bollinger middle band."
            )

    # ========================================================
    # MOMENTUM
    # ========================================================

    if not pd.isna(momentum):

        if momentum > 0:

            score += 5
            bullish_count += 1

            bullish_reasons.append(
                "Momentum is positive."
            )

        elif momentum < 0:

            score -= 5
            bearish_count += 1

            bearish_reasons.append(
                "Momentum is negative."
            )

    # ========================================================
    # VOLUME
    # ========================================================

    if not pd.isna(volume_ratio):

        if volume_ratio >= 1.5:

            previous_close = previous_value(
                df,
                "Close",
                close,
            )

            if close >= previous_close:

                score += 5
                bullish_count += 1

                bullish_reasons.append(
                    f"Volume is {volume_ratio:.2f}x average with positive price action."
                )

            else:

                score -= 5
                bearish_count += 1

                bearish_reasons.append(
                    f"High volume of {volume_ratio:.2f}x average accompanies price weakness."
                )

        elif volume_ratio < 1:

            warnings.append(
                f"Volume is only {volume_ratio:.2f}x average; confirmation is weak."
            )

    # ========================================================
    # CANDLESTICK
    # ========================================================

    candlestick = detect_candlestick_pattern(
        df
    )

    bullish_patterns = [
        "Bullish Engulfing",
        "Hammer",
        "Inverted Hammer",
        "Bullish Candle",
    ]

    bearish_patterns = [
        "Bearish Engulfing",
        "Shooting Star",
        "Bearish Candle",
    ]

    if candlestick in bullish_patterns:

        score += 3
        bullish_count += 1

        bullish_reasons.append(
            f"Latest candlestick pattern is {candlestick}."
        )

    elif candlestick in bearish_patterns:

        score -= 3
        bearish_count += 1

        bearish_reasons.append(
            f"Latest candlestick pattern is {candlestick}."
        )

    elif candlestick == "Doji":

        warnings.append(
            "Latest candle is a Doji, indicating indecision."
        )

    # ========================================================
    # TIMEFRAME CONFIRMATION
    # ========================================================

    if timeframe == "Intraday":

        if pd.isna(vwap):

            warnings.append(
                "Intraday VWAP confirmation is unavailable."
            )

        if pd.isna(volume_ratio):

            warnings.append(
                "Intraday volume confirmation is unavailable."
            )

    elif timeframe == "Swing":

        if pd.isna(sma50):

            warnings.append(
                "SMA 50 is unavailable for swing confirmation."
            )

    elif timeframe == "Long Term":

        if not pd.isna(sma50):

            if close > sma50:

                bullish_reasons.append(
                    "Price is above SMA 50, supporting the longer-term trend."
                )

            elif close < sma50:

                bearish_reasons.append(
                    "Price is below SMA 50, indicating longer-term weakness."
                )

    # ========================================================
    # SCORE
    # ========================================================

    score = int(
        np.clip(
            score,
            0,
            100,
        )
    )

    factor_gap = (
        bullish_count
        - bearish_count
    )

    # ========================================================
    # SIGNAL
    # ========================================================

    if (
        score >= 75
        and factor_gap >= 2
    ):

        signal = "STRONG BUY"

    elif (
        score >= 60
        and factor_gap >= 1
    ):

        signal = "BUY"

    elif (
        score <= 25
        and factor_gap <= -2
    ):

        signal = "STRONG SELL"

    elif (
        score < 45
        and factor_gap <= -1
    ):

        signal = "SELL"

    else:

        signal = "HOLD"

    # ========================================================
    # CONFIDENCE
    # ========================================================

    if (
        score >= 80
        and abs(factor_gap) >= 3
    ):

        confidence = "High"

    elif (
        score >= 70
        and abs(factor_gap) >= 2
    ):

        confidence = "Moderate-High"

    elif (
        score >= 55
        and abs(factor_gap) >= 1
    ):

        confidence = "Moderate"

    else:

        confidence = "Low"

    # ========================================================
    # REASON / ACTION
    # ========================================================

    if signal == "STRONG BUY":

        reason = (
            "Multiple technical indicators are aligned bullishly "
            "with strong confirmation."
        )

        action = (
            "Wait for the entry trigger and confirmation before buying. "
            "Avoid chasing a large breakout candle."
        )

        confirmation = (
            "Prefer price above VWAP/Supertrend with positive momentum "
            "and volume confirmation."
        )

    elif signal == "BUY":

        reason = (
            "The majority of technical factors support a bullish setup."
        )

        action = (
            "Consider buying after the entry trigger is confirmed."
        )

        confirmation = (
            "Confirm trend, momentum and volume before entry."
        )

    elif signal == "STRONG SELL":

        reason = (
            "Multiple technical indicators are aligned bearishly "
            "with strong downside confirmation."
        )

        action = (
            "Avoid fresh long positions and consider selling/shorting "
            "only after the sell trigger confirms."
        )

        confirmation = (
            "Prefer price below VWAP/Supertrend with negative momentum "
            "and volume confirmation."
        )

    elif signal == "SELL":

        reason = (
            "The majority of technical factors indicate weakness."
        )

        action = (
            "Avoid fresh buying and consider reducing exposure "
            "after confirmation."
        )

        confirmation = (
            "Confirm bearish trend and momentum before selling."
        )

    else:

        reason = (
            "Bullish and bearish technical factors are not sufficiently aligned."
        )

        action = (
            "Wait for stronger confirmation rather than forcing a trade."
        )

        confirmation = (
            "Wait for trend, momentum and volume to align."
        )

    return {
        "score": score,
        "signal": signal,
        "confidence": confidence,
        "bullish_count": bullish_count,
        "bearish_count": bearish_count,
        "factor_gap": factor_gap,
        "reasons": (
            bullish_reasons
            + bearish_reasons
        ),
        "bullish_reasons": bullish_reasons,
        "bearish_reasons": bearish_reasons,
        "warnings": warnings,
        "candlestick": candlestick,
        "reason": reason,
        "action": action,
        "confirmation": confirmation,
    }


# ============================================================
# TRADE PLAN
# ============================================================

def calculate_trade_plan(
    df,
    timeframe,
    signal_data,
):

    close = latest_value(
        df,
        "Close",
    )

    atr = latest_value(
        df,
        "ATR",
    )

    if pd.isna(close):

        return {
            "direction": "WAIT",
            "entry": np.nan,
            "zone_low": np.nan,
            "zone_high": np.nan,
            "stop_loss": np.nan,
            "target1": np.nan,
            "target2": np.nan,
            "risk": np.nan,
            "rr": 0,
            "atr": np.nan,
            "timeframe": timeframe,
            "signal": signal_data.get(
                "signal",
                "HOLD",
            ),
        }

    if pd.isna(atr) or atr <= 0:

        fallback_map = {
            "Intraday": 0.01,
            "Swing": 0.03,
            "Long Term": 0.06,
        }

        atr = (
            close
            * fallback_map.get(
                timeframe,
                0.02,
            )
        )

    signal = signal_data.get(
        "signal",
        "HOLD",
    )

    if timeframe == "Intraday":

        stop_atr = 1.0
        target1_rr = 1.5
        target2_rr = 2.0
        trigger_atr = 0.20

    elif timeframe == "Swing":

        stop_atr = 1.5
        target1_rr = 2.0
        target2_rr = 3.0
        trigger_atr = 0.30

    else:

        stop_atr = 2.5
        target1_rr = 2.0
        target2_rr = 3.5
        trigger_atr = 0.50

    if signal in [
        "BUY",
        "STRONG BUY",
    ]:

        entry = (
            close
            + atr * trigger_atr
        )

        zone_low = (
            close
            - atr * 0.25
        )

        zone_high = (
            close
            + atr * 0.10
        )

        risk = (
            atr * stop_atr
        )

        stop_loss = (
            entry - risk
        )

        target1 = (
            entry
            + risk * target1_rr
        )

        target2 = (
            entry
            + risk * target2_rr
        )

        rr = target2_rr

        direction = "BUY"

    elif signal in [
        "SELL",
        "STRONG SELL",
    ]:

        entry = (
            close
            - atr * trigger_atr
        )

        zone_low = (
            close
            - atr * 0.10
        )

        zone_high = (
            close
            + atr * 0.25
        )

        risk = (
            atr * stop_atr
        )

        stop_loss = (
            entry + risk
        )

        target1 = (
            entry
            - risk * target1_rr
        )

        target2 = (
            entry
            - risk * target2_rr
        )

        rr = target2_rr

        direction = "SELL"

    else:

        entry = close
        zone_low = close * 0.99
        zone_high = close * 1.01
        stop_loss = close
        target1 = close
        target2 = close
        risk = 0
        rr = 0
        direction = "WAIT"

    return {
        "direction": direction,
        "entry": entry,
        "zone_low": zone_low,
        "zone_high": zone_high,
        "stop_loss": stop_loss,
        "target1": target1,
        "target2": target2,
        "risk": risk,
        "rr": rr,
        "atr": atr,
        "timeframe": timeframe,
        "signal": signal,
    }


# ============================================================
# RESPONSIVE INDICATOR CHIPS
# ============================================================

def show_indicator_chips(selected):
    """Render selected indicators as responsive HTML chips.

    components.html isolates the chip markup and its CSS from Streamlit's
    Markdown renderer, preventing the HTML source from appearing as plain text.
    """
    indicators = list(selected or [])

    if not indicators:
        st.info(
            "No indicators selected. "
            "Choose indicators above to display them on the chart."
        )
        return

    chips = "".join(
        f'<span class="indicator-chip" title="{escape(str(indicator), quote=True)}">'
        f'{escape(str(indicator))}</span>'
        for indicator in indicators
    )

    html_content = f"""
    <!doctype html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            padding: 2px 0 6px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                         sans-serif;
            color: var(--text-color, #31333F);
        }}
        .indicator-chip-wrapper {{
            width: 100%;
            padding: 4px 0 2px;
        }}
        .indicator-chip-container {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 7px;
            width: 100%;
            max-width: 100%;
        }}
        .indicator-chip {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            max-width: 100%;
            min-height: 30px;
            padding: 5px 11px;
            border-radius: 999px;
            border: 1px solid rgba(80, 120, 200, 0.35);
            background: rgba(80, 120, 200, 0.12);
            color: inherit;
            font-size: 13px;
            line-height: 1.2;
            white-space: normal;
            overflow-wrap: anywhere;
        }}
        .indicator-chip:hover {{
            background: rgba(80, 120, 200, 0.20);
        }}
        .indicator-count {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 28px;
            padding: 4px 10px;
            border-radius: 999px;
            background: rgba(128, 128, 128, 0.14);
            font-size: 12px;
            font-weight: 650;
            white-space: nowrap;
            margin-left: auto;
        }}
        @media (max-width: 600px) {{
            .indicator-chip {{ font-size: 12px; padding: 5px 9px; }}
            .indicator-count {{ margin-left: 0; }}
        }}
    </style>
    </head>
    <body>
      <div class="indicator-chip-wrapper">
        <div class="indicator-chip-container">
          {chips}
          <span class="indicator-count">{len(indicators)} selected</span>
        </div>
      </div>
    </body>
    </html>
    """

    # Height adapts to wrapping so chips do not get clipped on narrow screens.
    rows = (len(indicators) + 2) // 3
    frame_height = min(180, max(58, rows * 42 + 16))
    components.html(
        html_content,
        height=frame_height,
        scrolling=False,
    )


# ============================================================
# PROFESSIONAL INDICATOR SELECTOR
# ============================================================

def _set_indicator_preset(indicators):
    """Callback keeps the multiselect widget and canonical state synchronized."""
    chosen = [item for item in indicators if item in ALL_INDICATORS]
    st.session_state.technical_selected_indicators = chosen.copy()
    st.session_state.technical_indicator_select = chosen.copy()


def show_indicator_selector():
    current = st.session_state.get(
        "technical_selected_indicators",
        DEFAULT_INDICATORS.copy(),
    )

    st.markdown("### 📌 Technical Indicators")
    st.caption(
        "Select one or more indicators. Price overlays are drawn on the main "
        "chart; RSI, MACD, ATR, Momentum and volume indicators are drawn in panels."
    )

    # Keep a separate widget key; callbacks update both keys before rerun.
    if "technical_indicator_select" not in st.session_state:
        st.session_state.technical_indicator_select = current.copy()

    selected = st.multiselect(
        "Select indicators",
        options=ALL_INDICATORS,
        placeholder="Search and select indicators...",
        help=(
            "Select multiple indicators. The main chart and indicator panels "
            "refresh automatically when this selection changes."
        ),
        key="technical_indicator_select",
        label_visibility="collapsed",
    )
    st.session_state.technical_selected_indicators = list(selected)

    q1, q2, q3, q4 = st.columns(4)
    with q1:
        st.button(
            "📈 Trend", width="stretch", key="select_trend_indicators",
            on_click=_set_indicator_preset, args=(TREND_INDICATORS,),
        )
    with q2:
        st.button(
            "🚀 Momentum", width="stretch", key="select_momentum_indicators",
            on_click=_set_indicator_preset, args=(MOMENTUM_INDICATORS,),
        )
    with q3:
        st.button(
            "⚡ Volatility", width="stretch", key="select_volatility_indicators",
            on_click=_set_indicator_preset, args=(VOLATILITY_INDICATORS,),
        )
    with q4:
        st.button(
            "⭐ Recommended", width="stretch", key="select_recommended_indicators",
            on_click=_set_indicator_preset, args=(DEFAULT_INDICATORS,),
        )

    st.markdown("#### Selected")
    show_indicator_chips(st.session_state.technical_selected_indicators)
    return list(st.session_state.technical_selected_indicators)


# ============================================================
# OVERLAY INDICATORS
# ============================================================

def add_selected_overlays(
    fig,
    df,
    selected_indicators,
):

    if df is None or df.empty:
        return fig

    if (
        "SMA 20" in selected_indicators
        and "SMA_20" in df.columns
    ):

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["SMA_20"],
                mode="lines",
                name="SMA 20",
            )
        )

    if (
        "SMA 50" in selected_indicators
        and "SMA_50" in df.columns
    ):

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["SMA_50"],
                mode="lines",
                name="SMA 50",
            )
        )

    if (
        "EMA 20" in selected_indicators
        and "EMA_20" in df.columns
    ):

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["EMA_20"],
                mode="lines",
                name="EMA 20",
            )
        )

    if (
        "EMA 50" in selected_indicators
        and "EMA_50" in df.columns
    ):

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["EMA_50"],
                mode="lines",
                name="EMA 50",
            )
        )

    if "Bollinger Bands" in selected_indicators:

        if all(
            col in df.columns
            for col in [
                "BB_Upper",
                "BB_Middle",
                "BB_Lower",
            ]
        ):

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["BB_Upper"],
                    mode="lines",
                    name="BB Upper",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["BB_Middle"],
                    mode="lines",
                    name="BB Middle",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["BB_Lower"],
                    mode="lines",
                    name="BB Lower",
                )
            )

    if (
        "VWAP" in selected_indicators
        and "VWAP" in df.columns
    ):

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["VWAP"],
                mode="lines",
                name="VWAP",
            )
        )

    if (
        "Supertrend" in selected_indicators
        and "Supertrend" in df.columns
    ):

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Supertrend"],
                mode="lines",
                name="Supertrend",
            )
        )

    return fig


# ============================================================
# PRICE CHART
# ============================================================

def create_price_chart(
    df,
    graph_type,
    selected_indicators,
):

    if df is None or df.empty:
        return None

    chart_df = df.copy()

    fig = go.Figure()

    if graph_type == "Candlestick":

        if all(
            col in chart_df.columns
            for col in [
                "Open",
                "High",
                "Low",
                "Close",
            ]
        ):

            fig.add_trace(
                go.Candlestick(
                    x=chart_df.index,
                    open=chart_df["Open"],
                    high=chart_df["High"],
                    low=chart_df["Low"],
                    close=chart_df["Close"],
                    name="Candlestick",
                )
            )

    elif graph_type == "Heikin Ashi":

        ha = calculate_heikin_ashi(
            chart_df
        )

        if not ha.empty:

            fig.add_trace(
                go.Candlestick(
                    x=ha.index,
                    open=ha["Open"],
                    high=ha["High"],
                    low=ha["Low"],
                    close=ha["Close"],
                    name="Heikin Ashi",
                )
            )

    elif graph_type == "OHLC":

        if all(
            col in chart_df.columns
            for col in [
                "Open",
                "High",
                "Low",
                "Close",
            ]
        ):

            fig.add_trace(
                go.Ohlc(
                    x=chart_df.index,
                    open=chart_df["Open"],
                    high=chart_df["High"],
                    low=chart_df["Low"],
                    close=chart_df["Close"],
                    name="OHLC",
                )
            )

    else:

        if "Close" in chart_df.columns:

            fig.add_trace(
                go.Scatter(
                    x=chart_df.index,
                    y=chart_df["Close"],
                    mode="lines",
                    name="Close",
                )
            )

    fig = add_selected_overlays(
        fig,
        chart_df,
        selected_indicators,
    )

    fig.update_layout(
        height=560,
        margin=dict(
            l=10,
            r=10,
            t=30,
            b=10,
        ),
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
    )

    fig.update_xaxes(
        showgrid=False,
        fixedrange=False,
    )

    fig.update_yaxes(
        showgrid=True,
        fixedrange=False,
    )

    return fig


# ============================================================
# INDICATOR PANEL CHART
# ============================================================

def create_indicator_chart(
    df,
    indicator,
):

    if df is None or df.empty:
        return None

    fig = go.Figure()

    column_map = {
        "RSI": "RSI",
        "ATR": "ATR",
        "Momentum": "Momentum",
        "Volume": "Volume",
        "Volume Ratio": "Volume_Ratio",
    }

    if indicator == "MACD":

        if "MACD" in df.columns:

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["MACD"],
                    mode="lines",
                    name="MACD",
                )
            )

        if "MACD_Signal" in df.columns:

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["MACD_Signal"],
                    mode="lines",
                    name="Signal",
                )
            )

        if "MACD_Hist" in df.columns:

            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df["MACD_Hist"],
                    name="Histogram",
                )
            )

    else:

        column = column_map.get(
            indicator
        )

        if (
            not column
            or column not in df.columns
        ):
            return None

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[column],
                mode="lines",
                name=indicator,
            )
        )

        if indicator == "RSI":

            fig.add_hline(
                y=70,
                line_dash="dash",
            )

            fig.add_hline(
                y=30,
                line_dash="dash",
            )

            fig.add_hline(
                y=50,
                line_dash="dot",
            )

    fig.update_layout(
        height=360,
        margin=dict(
            l=10,
            r=10,
            t=25,
            b=10,
        ),
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
    )

    return fig


# ============================================================
# RECOMMENDATION CARD
# ============================================================

def show_recommendation_card(
    signal_data,
    trade_plan,
    timeframe,
    compact=False,
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

    reason = signal_data.get(
        "reason",
        "Insufficient technical confirmation.",
    )

    action = signal_data.get(
        "action",
        "Wait for stronger confirmation.",
    )

    if signal == "STRONG BUY":

        st.success(
            f"## 🟢 STRONG BUY\n\n"
            f"**{timeframe} Technical Recommendation**  \n"
            f"Technical Score: **{score}/100**  \n"
            f"Confidence: **{confidence}**"
        )

    elif signal == "BUY":

        st.success(
            f"## 🟢 BUY\n\n"
            f"**{timeframe} Technical Recommendation**  \n"
            f"Technical Score: **{score}/100**  \n"
            f"Confidence: **{confidence}**"
        )

    elif signal == "STRONG SELL":

        st.error(
            f"## 🔴 STRONG SELL\n\n"
            f"**{timeframe} Technical Recommendation**  \n"
            f"Technical Score: **{score}/100**  \n"
            f"Confidence: **{confidence}**"
        )

    elif signal == "SELL":

        st.error(
            f"## 🔴 SELL\n\n"
            f"**{timeframe} Technical Recommendation**  \n"
            f"Technical Score: **{score}/100**  \n"
            f"Confidence: **{confidence}**"
        )

    else:

        st.warning(
            f"## 🟡 HOLD\n\n"
            f"**{timeframe} Technical Recommendation**  \n"
            f"Technical Score: **{score}/100**  \n"
            f"Confidence: **{confidence}**"
        )

    st.info(
        f"**What to do now:** {action}"
    )

    st.markdown(
        "### 🧠 Why this recommendation?"
    )

    st.write(
        reason
    )

    if compact:
        return

    if signal in [
        "STRONG BUY",
        "BUY",
        "STRONG SELL",
        "SELL",
    ]:

        st.markdown(
            "### 🎯 Trade Levels"
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Entry / Trigger",
                fmt(
                    trade_plan.get(
                        "entry",
                        np.nan,
                    )
                ),
            )

        with c2:
            st.metric(
                "Stop Loss",
                fmt(
                    trade_plan.get(
                        "stop_loss",
                        np.nan,
                    )
                ),
            )

        with c3:
            st.metric(
                "Target 1",
                fmt(
                    trade_plan.get(
                        "target1",
                        np.nan,
                    )
                ),
            )

        with c4:
            st.metric(
                "Target 2",
                fmt(
                    trade_plan.get(
                        "target2",
                        np.nan,
                    )
                ),
            )

    else:

        st.warning(
            "No high-confidence trade setup currently. "
            "Wait for stronger confirmation before entering."
        )

    warnings = signal_data.get(
        "warnings",
        [],
    )

    if warnings:

        with st.expander(
            "⚠️ Important Warnings",
            expanded=False,
        ):

            for warning in warnings:

                st.warning(
                    warning
                )


# ============================================================
# INTRADAY SETUP
# ============================================================

def show_intraday_trade_setup(
    df,
    signal_data,
    trade_plan,
):

    signal = signal_data["signal"]

    st.markdown(
        "### 🎯 Intraday Trade Setup"
    )

    if signal == "HOLD":

        st.warning(
            "No high-confidence intraday setup currently. "
            "Wait for VWAP, Supertrend, momentum and volume confirmation."
        )

        return

    direction = trade_plan["direction"]

    if direction == "BUY":

        st.success(
            "🟢 Bullish intraday setup — buy only after the entry trigger confirms."
        )

    elif direction == "SELL":

        st.error(
            "🔴 Bearish intraday setup — sell/short only after the sell trigger confirms."
        )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "Current Price",
            fmt(
                latest_value(
                    df,
                    "Close",
                )
            ),
        )

    with c2:
        st.metric(
            "Entry Trigger",
            fmt(
                trade_plan["entry"]
            ),
        )

    with c3:
        st.metric(
            "Stop Loss",
            fmt(
                trade_plan["stop_loss"]
            ),
        )

    with c4:
        st.metric(
            "Target 1",
            fmt(
                trade_plan["target1"]
            ),
        )

    with c5:
        st.metric(
            "Target 2",
            fmt(
                trade_plan["target2"]
            ),
        )

    st.markdown(
        "### Entry Zone"
    )

    z1, z2, z3 = st.columns(3)

    with z1:
        st.metric(
            "Zone Low",
            fmt(
                trade_plan["zone_low"]
            ),
        )

    with z2:
        st.metric(
            "Preferred Trigger",
            fmt(
                trade_plan["entry"]
            ),
        )

    with z3:
        st.metric(
            "Zone High",
            fmt(
                trade_plan["zone_high"]
            ),
        )

    r1, r2, r3 = st.columns(3)

    with r1:
        st.metric(
            "ATR",
            fmt(
                trade_plan["atr"]
            ),
        )

    with r2:
        st.metric(
            "Risk",
            fmt(
                trade_plan["risk"]
            ),
        )

    with r3:
        st.metric(
            "Target R:R",
            f"1:{fmt(trade_plan['rr'], 1)}",
        )

    st.markdown(
        "### How to Execute"
    )

    if direction == "BUY":

        st.markdown(
            """
            <div class="info-box">
            <b>Buy only when:</b>
            <ul>
                <li>Price breaks and sustains above the entry trigger.</li>
                <li>Price remains above VWAP where available.</li>
                <li>Price remains above Supertrend where available.</li>
                <li>RSI preferably remains above 50.</li>
                <li>MACD supports bullish momentum.</li>
                <li>Volume preferably confirms the breakout.</li>
            </ul>
            <b>Risk management:</b> Keep the predefined stop loss.
            Do not chase an unusually large candle.
            </div>
            """,
            unsafe_allow_html=True,
        )

    elif direction == "SELL":

        st.markdown(
            """
            <div class="info-box">
            <b>Sell/Short only when:</b>
            <ul>
                <li>Price breaks and sustains below the sell trigger.</li>
                <li>Price remains below VWAP where available.</li>
                <li>Price remains below Supertrend where available.</li>
                <li>RSI preferably remains below 50.</li>
                <li>MACD supports bearish momentum.</li>
                <li>Volume confirms the downside move.</li>
            </ul>
            <b>Risk management:</b> Keep the predefined stop loss.
            Avoid shorting after an already extended fall.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        "### Intraday Confirmation Checklist"
    )

    current_price = latest_value(
        df,
        "Close",
    )

    vwap = latest_value(
        df,
        "VWAP",
    )

    supertrend = latest_value(
        df,
        "Supertrend",
    )

    rsi = latest_value(
        df,
        "RSI",
    )

    macd = latest_value(
        df,
        "MACD",
    )

    macd_signal = latest_value(
        df,
        "MACD_Signal",
    )

    volume_ratio = latest_value(
        df,
        "Volume_Ratio",
    )

    checks = []

    if direction == "BUY":

        checks.extend(
            [
                (
                    "Price above VWAP",
                    not pd.isna(vwap)
                    and current_price > vwap,
                ),
                (
                    "Price above Supertrend",
                    not pd.isna(supertrend)
                    and current_price > supertrend,
                ),
                (
                    "RSI above 50",
                    not pd.isna(rsi)
                    and rsi > 50,
                ),
                (
                    "MACD above Signal",
                    not pd.isna(macd)
                    and not pd.isna(macd_signal)
                    and macd > macd_signal,
                ),
                (
                    "Volume confirmation",
                    not pd.isna(volume_ratio)
                    and volume_ratio >= 1.2,
                ),
            ]
        )

    else:

        checks.extend(
            [
                (
                    "Price below VWAP",
                    not pd.isna(vwap)
                    and current_price < vwap,
                ),
                (
                    "Price below Supertrend",
                    not pd.isna(supertrend)
                    and current_price < supertrend,
                ),
                (
                    "RSI below 50",
                    not pd.isna(rsi)
                    and rsi < 50,
                ),
                (
                    "MACD below Signal",
                    not pd.isna(macd)
                    and not pd.isna(macd_signal)
                    and macd < macd_signal,
                ),
                (
                    "Volume confirmation",
                    not pd.isna(volume_ratio)
                    and volume_ratio >= 1.2,
                ),
            ]
        )

    for label, passed in checks:

        if passed:
            st.success(
                f"✓ {label}"
            )
        else:
            st.warning(
                f"⚠ {label}"
            )


# ============================================================
# STRATEGY-SPECIFIC CHARTS
# ============================================================

STRATEGY_CHART_SETTINGS = {
    # Each strategy chooses its own candle interval and lookback period.
    # Free market-data providers commonly limit intraday history to 5–60 days.
    "Intraday": {"interval": "5 minutes", "period": "5 Days", "panels": ["RSI", "MACD", "Volume Ratio"]},
    "Swing": {"interval": "1 day", "period": "180 Days", "panels": ["RSI", "MACD", "ATR", "Volume Ratio"]},
    "Long Term": {"interval": "1 week", "period": "5 Years", "panels": ["RSI", "MACD", "ATR", "Volume"]},
}


@st.cache_data(ttl=300, show_spinner=False)
def load_strategy_chart_data(stock_symbol, strategy_name):
    """Fetch and prepare data using the strategy's own interval and period."""
    settings = STRATEGY_CHART_SETTINGS[strategy_name]
    raw, interval_supported = load_stock_data_for_interval(
        stock_symbol, settings["interval"], settings["period"]
    )
    frame = normalize_columns(raw)
    frame = prepare_datetime_index(frame)
    frame = prepare_numeric_columns(frame)
    frame = calculate_missing_indicators(frame)
    frame = filter_period(frame, settings["period"])
    return frame, interval_supported, settings


def show_strategy_chart(stock_symbol, strategy_name, graph_type, selected_indicators):
    """Render a strategy chart using its own market-data interval and period."""
    settings = STRATEGY_CHART_SETTINGS[strategy_name]
    interval = settings["interval"]
    period_name = settings["period"]

    st.markdown(f"### {strategy_name} price chart")
    st.caption(
        f"Automatic settings: **{interval} candles · {period_name} history**. "
        "These settings are chosen independently for this strategy."
    )

    try:
        df, interval_supported, loaded_settings = load_strategy_chart_data(
            stock_symbol, strategy_name
        )
    except Exception as exc:
        st.error(f"Could not load {strategy_name} market data: {exc}")
        return

    if df is None or df.empty:
        st.warning(f"No data returned for {strategy_name} ({interval}, {period_name}).")
        return

    if not interval_supported and interval != "1 day":
        st.warning(
            f"Your current analyze_stock() service does not accept an interval argument. "
            f"This view requested {interval} candles, but the service may have returned "
            "its default interval. Update services/stock_service.py and "
            "services/market_data.py to enable genuine interval-specific charts."
        )

    presets = {
        "Intraday": ["VWAP", "Supertrend", "EMA 20", "EMA 50"],
        "Swing": ["SMA 20", "SMA 50", "EMA 20", "EMA 50", "Bollinger Bands", "Supertrend"],
        "Long Term": ["SMA 50", "EMA 50", "Bollinger Bands", "Supertrend"],
    }
    selected = list(selected_indicators or [])
    overlays = list(dict.fromkeys(
        [x for x in selected if x in OVERLAY_INDICATORS] + presets[strategy_name]
    ))
    panels = list(dict.fromkeys(
        [x for x in selected if x in PANEL_INDICATORS] + settings["panels"]
    ))

    fig = create_price_chart(df, graph_type, overlays)
    strategy_key = strategy_name.lower().replace(" ", "_")
    if fig is not None:
        st.plotly_chart(
            fig, width="stretch", key=f"strategy_price_chart_{strategy_key}_{interval.replace(' ', '')}_{period_name.replace(' ', '')}"
        )
    else:
        st.warning("Unable to create a price chart from the available OHLC data.")

    # Show a strategy-specific actionable plan directly under its chart.
    signal = calculate_technical_signal(df, strategy_name)
    plan = calculate_trade_plan(df, strategy_name, signal)
    st.markdown("#### Strategy trade recommendation")
    st.write(f"**Signal:** {signal.get('signal', 'HOLD')} · **Action:** {plan.get('direction', 'WAIT')}")
    p1, p2, p3, p4, p5 = st.columns(5)
    with p1:
        st.metric("Entry / Trigger", fmt(plan.get("entry")))
    with p2:
        st.metric("Stop Loss", fmt(plan.get("stop_loss")))
    with p3:
        st.metric("Target 1", fmt(plan.get("target1")))
    with p4:
        st.metric("Target 2", fmt(plan.get("target2")))
    with p5:
        st.metric("Risk : Reward", f"1 : {plan.get('rr', 0):.1f}" if plan.get("rr") else "—")
    if plan.get("direction") == "WAIT":
        st.info("No directional entry is confirmed. Wait for a breakout/breakdown and indicator confirmation.")
    elif plan.get("direction") == "BUY":
        st.success(f"Buy only after confirmation above {fmt(plan.get('entry'))}; consider partial exits at Target 1 and Target 2. Exit if stop loss {fmt(plan.get('stop_loss'))} is hit or the setup invalidates.")
    else:
        st.warning(f"Sell/short only where permitted and after breakdown confirmation below {fmt(plan.get('entry'))}; targets {fmt(plan.get('target1'))} and {fmt(plan.get('target2'))}. Exit if stop loss {fmt(plan.get('stop_loss'))} is hit.")

    st.markdown("#### Indicator panels")
    for indicator in panels:
        panel = create_indicator_chart(df, indicator)
        if panel is not None:
            st.plotly_chart(
                panel,
                width="stretch",
                key=f"strategy_indicator_{strategy_key}_{indicator.lower().replace(' ', '_').replace('/', '_')}",
            )
        else:
            st.caption(f"{indicator}: unavailable for the current data returned by the service.")


# ============================================================
# HEADER
# ============================================================

try:

    page_header(
        "Technical Analysis",
        "Professional multi-indicator technical analysis and trade planning",
    )

except Exception:

    st.markdown(
        '<div class="main-title">📉 Technical Analysis</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sub-title">'
        'Professional multi-indicator technical analysis and trade planning'
        '</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# NAVIGATION
# ============================================================

try:
    show_page_navigation()
except Exception as exc:
    st.warning(f"Page navigation could not be rendered: {exc}")


# ============================================================
# STOCK
# ============================================================

try:

    stock = get_selected_stock()

except Exception:

    stock = None


if not stock:

    st.warning(
        "Please select a stock from the Dashboard first."
    )

    st.stop()


# ============================================================
# ANALYSIS CONTROLS
# ============================================================

st.markdown(
    "### ⚙️ Analysis Controls"
)

st.markdown(
    '<div class="control-panel">',
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Row 1
# ------------------------------------------------------------

control1, control2, control3, control4 = st.columns(4)

with control1:

    strategy_mode = st.selectbox(
        "Strategy",
        TIMEFRAMES,
        index=TIMEFRAMES.index(
            st.session_state.technical_strategy_mode
        ),
        key="technical_strategy_select",
    )

    st.session_state.technical_strategy_mode = (
        strategy_mode
    )

with control2:

    period = st.selectbox(
        "Analysis Period",
        PERIODS,
        index=PERIODS.index(
            st.session_state.technical_period
        ),
        key="technical_period_select",
    )

    st.session_state.technical_period = (
        period
    )

with control3:

    graph_type = st.selectbox(
        "Chart Type",
        GRAPH_TYPES,
        index=GRAPH_TYPES.index(
            st.session_state.technical_graph_type
        ),
        key="technical_graph_select",
    )

    st.session_state.technical_graph_type = graph_type

with control4:
    candle_interval = st.selectbox(
        "Candle Interval",
        CANDLE_INTERVALS,
        index=CANDLE_INTERVALS.index(
            st.session_state.technical_candle_interval
        ),
        key="technical_candle_interval_select",
        help="Requires the stock service to support interval-based market data.",
    )
    st.session_state.technical_candle_interval = candle_interval

st.markdown(
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# INDICATOR SELECTOR
# ============================================================

with st.container():

    selected_indicators = (
        show_indicator_selector()
    )


# ============================================================
# FAVORITES
# ============================================================

with st.expander(
    "⭐ Favorite Stocks",
    expanded=False,
):

    st.caption(
        "Save frequently analyzed symbols for quick reference."
    )

    fav1, fav2, fav3 = st.columns(3)

    with fav1:

        st.session_state.technical_favorite_1 = (
            st.text_input(
                "Favorite 1",
                value=st.session_state.technical_favorite_1,
                placeholder="e.g. RELIANCE",
            )
        )

    with fav2:

        st.session_state.technical_favorite_2 = (
            st.text_input(
                "Favorite 2",
                value=st.session_state.technical_favorite_2,
                placeholder="e.g. TCS",
            )
        )

    with fav3:

        st.session_state.technical_favorite_3 = (
            st.text_input(
                "Favorite 3",
                value=st.session_state.technical_favorite_3,
                placeholder="e.g. INFY",
            )
        )


# ============================================================
# LOAD DATA
# ============================================================

with st.spinner(
    f"Loading technical analysis for {stock}..."
):

    try:

        raw_data, interval_supported = load_stock_data_for_interval(
            stock,
            candle_interval,
            period,
        )

    except Exception as exc:

        st.error(
            f"Unable to load technical analysis for {stock}: {exc}"
        )

        st.stop()


# ============================================================
# NORMALIZE
# ============================================================

data = normalize_columns(
    raw_data
)

data = prepare_datetime_index(
    data
)

data = prepare_numeric_columns(data)
data = calculate_missing_indicators(data)

# Apply the requested display period after calculating rolling indicators, so
# moving averages and oscillators have enough warm-up history.
data = filter_period(data, period)

if not interval_supported and candle_interval != "1 day":
    st.warning(
        f"Your current services.stock_service.analyze_stock() does not expose an "
        f"'interval' parameter. Showing the service's default candle interval, "
        f"not true {candle_interval} candles. To enable genuine intraday/weekly/monthly "
        f"candles, update services/stock_service.py and services/market_data.py."
    )

if data is None or data.empty:

    st.warning(
        "No market data is available for the selected stock and period."
    )

    st.stop()


if "Close" not in data.columns:

    st.error(
        "The market-data service did not return a Close price column."
    )

    st.stop()


# ============================================================
# COMMON METRICS
# ============================================================

current_price = latest_value(
    data,
    "Close",
)

previous_close = previous_value(
    data,
    "Close",
    current_price,
)

daily_change = (
    safe_divide(
        current_price - previous_close,
        previous_close,
    )
    * 100
)

rsi = latest_value(
    data,
    "RSI",
)

macd = latest_value(
    data,
    "MACD",
)

macd_signal = latest_value(
    data,
    "MACD_Signal",
)

macd_hist = latest_value(
    data,
    "MACD_Hist",
)

momentum = latest_value(
    data,
    "Momentum",
)

vwap = latest_value(
    data,
    "VWAP",
)

supertrend = latest_value(
    data,
    "Supertrend",
)

volume_ratio = latest_value(
    data,
    "Volume_Ratio",
)

atr = latest_value(
    data,
    "ATR",
)

sma20 = latest_value(
    data,
    "SMA_20",
)

sma50 = latest_value(
    data,
    "SMA_50",
)

ema20 = latest_value(
    data,
    "EMA_20",
)

ema50 = latest_value(
    data,
    "EMA_50",
)

bb_upper = latest_value(
    data,
    "BB_Upper",
)

bb_middle = latest_value(
    data,
    "BB_Middle",
)

bb_lower = latest_value(
    data,
    "BB_Lower",
)


# ============================================================
# SIGNAL
# ============================================================

signal_data = calculate_technical_signal(
    data,
    strategy_mode,
)

trade_plan = calculate_trade_plan(
    data,
    strategy_mode,
    signal_data,
)


# ============================================================
# TABS
# ============================================================

tabs = st.tabs(
    [
        "📊 Overview",
        "📈 Moving Averages",
        "🚀 Momentum",
        "⚡ Volatility",
        "🎯 Intraday",
        "🕯️ Candlestick",
        "💰 Trade Setup",
        "📘 Indicator Guide",
    ]
)


# ============================================================
# TAB 1 — OVERVIEW
# ============================================================

with tabs[0]:

    st.markdown(
        f"""
        <div class="main-title">
            {stock} Technical Overview
        </div>

        <div class="sub-title">
            {strategy_mode} strategy • {period}
        </div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)

    with m1:

        st.metric(
            "Current Price",
            fmt(current_price),
            f"{daily_change:+.2f}%",
        )

    with m2:

        st.metric(
            "Technical Score",
            f"{signal_data['score']}/100",
        )

    with m3:

        st.metric(
            "Bullish Factors",
            signal_data["bullish_count"],
        )

    with m4:

        st.metric(
            "Bearish Factors",
            signal_data["bearish_count"],
        )

    st.markdown(
        "### ⭐ Main Recommendation"
    )

    show_recommendation_card(
        signal_data,
        trade_plan,
        strategy_mode,
    )

    st.markdown("### 🎯 Entry, Exit, Stop Loss & Targets")
    st.caption(
        "Levels are technical estimates derived from the latest close and ATR, not guaranteed prices. "
        "Use a confirmed trigger and your own risk limits before placing any order."
    )
    level1, level2, level3, level4, level5 = st.columns(5)
    with level1:
        st.metric("Action", trade_plan.get("direction", "WAIT"))
    with level2:
        st.metric("Entry / Trigger", fmt(trade_plan.get("entry")))
    with level3:
        st.metric("Stop Loss", fmt(trade_plan.get("stop_loss")))
    with level4:
        st.metric("Target 1", fmt(trade_plan.get("target1")))
    with level5:
        st.metric("Target 2 / Final Exit", fmt(trade_plan.get("target2")))
    if trade_plan.get("direction") == "WAIT":
        st.info("Current signal is HOLD. Wait for a confirmed buy breakout or sell breakdown; avoid treating the reference levels as an active order.")
    elif trade_plan.get("direction") == "BUY":
        st.success(f"Buy setup: wait for price confirmation at/above {fmt(trade_plan.get('entry'))}. Consider booking partial profit at {fmt(trade_plan.get('target1'))} and exiting the remainder near {fmt(trade_plan.get('target2'))}; exit earlier if stop loss {fmt(trade_plan.get('stop_loss'))} is hit or the setup fails.")
    else:
        st.warning(f"Sell setup: confirm breakdown at/below {fmt(trade_plan.get('entry'))}. Potential downside targets are {fmt(trade_plan.get('target1'))} and {fmt(trade_plan.get('target2'))}; risk invalidation is {fmt(trade_plan.get('stop_loss'))}. Short selling is subject to market and broker rules.")

    st.markdown(
        "### 📌 What Should You Do Now?"
    )

    if signal_data["signal"] == "STRONG BUY":

        st.success(
            f"STRONG BUY: Monitor the stock for a sustained move above "
            f"{fmt(trade_plan['entry'])}. Stop loss: "
            f"{fmt(trade_plan['stop_loss'])}. "
            f"Targets: {fmt(trade_plan['target1'])} and "
            f"{fmt(trade_plan['target2'])}."
        )

    elif signal_data["signal"] == "BUY":

        st.success(
            f"BUY: Consider entry after price confirms "
            f"{fmt(trade_plan['entry'])}. "
            f"Stop loss: {fmt(trade_plan['stop_loss'])}. "
            f"Targets: {fmt(trade_plan['target1'])} / "
            f"{fmt(trade_plan['target2'])}."
        )

    elif signal_data["signal"] == "STRONG SELL":

        st.error(
            f"STRONG SELL: Avoid fresh long positions. "
            f"Consider sell/short confirmation below "
            f"{fmt(trade_plan['entry'])}. "
            f"Stop loss: {fmt(trade_plan['stop_loss'])}."
        )

    elif signal_data["signal"] == "SELL":

        st.error(
            f"SELL: Technical structure is weak. "
            f"Wait for confirmation below "
            f"{fmt(trade_plan['entry'])} before selling."
        )

    else:

        st.warning(
            "HOLD: Do not force a trade. "
            "Wait for stronger technical alignment."
        )

    left, right = st.columns(2)

    with left:

        st.markdown(
            "### 🟢 Bullish Factors"
        )

        if signal_data["bullish_reasons"]:

            for reason in signal_data["bullish_reasons"]:

                st.markdown(
                    f"""
                    <div class="factor-card factor-positive">
                        ✓ {reason}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        else:

            st.info(
                "No strong bullish factors detected."
            )

    with right:

        st.markdown(
            "### 🔴 Bearish Factors"
        )

        if signal_data["bearish_reasons"]:

            for reason in signal_data["bearish_reasons"]:

                st.markdown(
                    f"""
                    <div class="factor-card factor-negative">
                        ⚠ {reason}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        else:

            st.info(
                "No strong bearish factors detected."
            )

    st.markdown(
        "### 📈 Price & Selected Indicators"
    )

    fig = create_price_chart(
        data,
        graph_type,
        selected_indicators,
    )

    if fig is not None:

        indicator_key = "_".join(
            item.lower().replace(" ", "_")
            for item in selected_indicators
        ) or "no_indicators"
        st.plotly_chart(
            fig,
            width="stretch",
            key=f"technical_overview_price_chart_{graph_type.lower().replace(' ', '_')}_{indicator_key}",
        )

    st.markdown("---")
    st.markdown("### Strategy-specific chart views")
    st.caption(
        "Each strategy automatically loads its own candle interval and history, "
        "independent of the global chart controls above."
    )
    strategy_tab_intraday, strategy_tab_swing, strategy_tab_longterm = st.tabs(
        ["⚡ Intraday · 5m / 5D", "📈 Swing · 1D / 180D", "🏦 Long Term · 1W / 5Y"]
    )
    with strategy_tab_intraday:
        show_strategy_chart(stock, "Intraday", graph_type, selected_indicators)
    with strategy_tab_swing:
        show_strategy_chart(stock, "Swing", graph_type, selected_indicators)
    with strategy_tab_longterm:
        show_strategy_chart(stock, "Long Term", graph_type, selected_indicators)


# ============================================================
# TAB 2 — MOVING AVERAGES
# ============================================================

with tabs[1]:

    st.markdown(
        "## 📈 Moving Average Analysis"
    )

    ma1, ma2, ma3, ma4 = st.columns(4)

    with ma1:
        st.metric(
            "SMA 20",
            fmt(sma20),
        )

    with ma2:
        st.metric(
            "SMA 50",
            fmt(sma50),
        )

    with ma3:
        st.metric(
            "EMA 20",
            fmt(ema20),
        )

    with ma4:
        st.metric(
            "EMA 50",
            fmt(ema50),
        )

    if (
        not pd.isna(sma20)
        and not pd.isna(sma50)
    ):

        if sma20 > sma50:

            st.success(
                "Bullish moving-average structure: SMA 20 is above SMA 50."
            )

        else:

            st.error(
                "Bearish moving-average structure: SMA 20 is below SMA 50."
            )

    if (
        not pd.isna(ema20)
        and not pd.isna(ema50)
    ):

        if ema20 > ema50:

            st.success(
                "EMA trend is bullish: EMA 20 is above EMA 50."
            )

        else:

            st.error(
                "EMA trend is bearish: EMA 20 is below EMA 50."
            )

    fig = create_price_chart(
        data,
        graph_type,
        [
            "SMA 20",
            "SMA 50",
            "EMA 20",
            "EMA 50",
        ],
    )

    if fig is not None:

        st.plotly_chart(
            fig,
            width="stretch",
        )

    st.markdown(
        "### 📘 Interpretation"
    )

    st.info(
        "SMA 20 and EMA 20 are primarily used for short-term trend direction. "
        "SMA 50 and EMA 50 provide broader trend confirmation. "
        "A faster average above a slower average generally supports bullish structure."
    )


# ============================================================
# TAB 3 — MOMENTUM
# ============================================================

with tabs[2]:

    st.markdown(
        "## 🚀 Momentum Analysis"
    )

    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.metric(
            "RSI",
            fmt(rsi, 1),
        )

    with p2:
        st.metric(
            "MACD",
            fmt(macd, 3),
        )

    with p3:
        st.metric(
            "MACD Signal",
            fmt(macd_signal, 3),
        )

    with p4:
        st.metric(
            "Momentum",
            fmt(momentum, 2),
        )

    if not pd.isna(rsi):

        if rsi >= 70:

            st.warning(
                f"RSI {rsi:.1f}: Overbought zone. Avoid chasing extended moves."
            )

        elif rsi <= 30:

            st.warning(
                f"RSI {rsi:.1f}: Oversold zone. Wait for reversal confirmation."
            )

        elif rsi >= 50:

            st.success(
                f"RSI {rsi:.1f}: Momentum is bullish."
            )

        else:

            st.error(
                f"RSI {rsi:.1f}: Momentum is weak."
            )

    if (
        not pd.isna(macd)
        and not pd.isna(macd_signal)
    ):

        if macd > macd_signal:

            st.success(
                "MACD is above Signal — bullish momentum confirmation."
            )

        else:

            st.error(
                "MACD is below Signal — bearish momentum confirmation."
            )

    for indicator in [
        "RSI",
        "MACD",
        "Momentum",
    ]:

        fig = create_indicator_chart(
            data,
            indicator,
        )

        if fig is not None:

            st.markdown(
                f"### {indicator}"
            )

            st.plotly_chart(
                fig,
                width="stretch",
            )


# ============================================================
# TAB 4 — VOLATILITY
# ============================================================

with tabs[3]:

    st.markdown(
        "## ⚡ Volatility Analysis"
    )

    v1, v2, v3, v4 = st.columns(4)

    with v1:
        st.metric(
            "ATR",
            fmt(atr),
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

    if (
        not pd.isna(bb_upper)
        and not pd.isna(bb_lower)
        and not pd.isna(current_price)
    ):

        if current_price >= bb_upper:

            st.warning(
                "Price is near/above the upper Bollinger Band. "
                "The stock may be extended."
            )

        elif current_price <= bb_lower:

            st.warning(
                "Price is near/below the lower Bollinger Band. "
                "Watch for reversal or continuation confirmation."
            )

        elif (
            not pd.isna(bb_middle)
            and current_price > bb_middle
        ):

            st.success(
                "Price is above the Bollinger middle band."
            )

        else:

            st.info(
                "Price is below the Bollinger middle band."
            )

    fig = create_price_chart(
        data,
        graph_type,
        [
            "Bollinger Bands",
        ],
    )

    if fig is not None:

        st.plotly_chart(
            fig,
            width="stretch",
        )

    atr_fig = create_indicator_chart(
        data,
        "ATR",
    )

    if atr_fig is not None:

        st.markdown(
            "### ATR"
        )

        st.plotly_chart(
            atr_fig,
            width="stretch",
        )


# ============================================================
# TAB 5 — INTRADAY
# ============================================================

with tabs[4]:

    st.markdown(
        "## 🎯 Intraday Analysis"
    )

    i1, i2, i3, i4 = st.columns(4)

    with i1:
        st.metric(
            "Price",
            fmt(current_price),
        )

    with i2:
        st.metric(
            "VWAP",
            fmt(vwap),
        )

    with i3:
        st.metric(
            "Supertrend",
            fmt(supertrend),
        )

    with i4:
        st.metric(
            "Volume Ratio",
            fmt(volume_ratio, 2),
        )

    bullish_intraday = 0
    bearish_intraday = 0

    if not pd.isna(vwap):

        if current_price > vwap:
            bullish_intraday += 1
        else:
            bearish_intraday += 1

    if not pd.isna(supertrend):

        if current_price > supertrend:
            bullish_intraday += 1
        else:
            bearish_intraday += 1

    if not pd.isna(rsi):

        if rsi > 50:
            bullish_intraday += 1
        else:
            bearish_intraday += 1

    if (
        not pd.isna(macd)
        and not pd.isna(macd_signal)
    ):

        if macd > macd_signal:
            bullish_intraday += 1
        else:
            bearish_intraday += 1

    if bullish_intraday >= 3:

        st.success(
            "🟢 Intraday Bias: BULLISH"
        )

    elif bearish_intraday >= 3:

        st.error(
            "🔴 Intraday Bias: BEARISH"
        )

    else:

        st.warning(
            "🟡 Intraday Bias: MIXED"
        )

    intraday_signal = calculate_technical_signal(
        data,
        "Intraday",
    )

    intraday_plan = calculate_trade_plan(
        data,
        "Intraday",
        intraday_signal,
    )

    show_intraday_trade_setup(
        data,
        intraday_signal,
        intraday_plan,
    )

    st.markdown(
        "### 📈 Intraday Price Structure"
    )

    intraday_fig = create_price_chart(
        data,
        graph_type,
        [
            "VWAP",
            "Supertrend",
        ],
    )

    if intraday_fig is not None:

        st.plotly_chart(
            intraday_fig,
            width="stretch",
        )


# ============================================================
# TAB 6 — CANDLESTICK
# ============================================================

with tabs[5]:

    st.markdown(
        "## 🕯️ Candlestick Analysis"
    )

    pattern = detect_candlestick_pattern(
        data
    )

    st.metric(
        "Latest Pattern",
        pattern,
    )

    if pattern in [
        "Bullish Engulfing",
        "Hammer",
        "Inverted Hammer",
        "Bullish Candle",
    ]:

        st.success(
            f"🟢 Bullish candlestick pattern detected: {pattern}"
        )

    elif pattern in [
        "Bearish Engulfing",
        "Shooting Star",
        "Bearish Candle",
    ]:

        st.error(
            f"🔴 Bearish candlestick pattern detected: {pattern}"
        )

    elif pattern == "Doji":

        st.warning(
            "🟡 Doji detected — market indecision. "
            "Wait for confirmation."
        )

    else:

        st.info(
            "No strong directional candlestick pattern detected."
        )

    candle_fig = create_price_chart(
        data,
        "Candlestick",
        selected_indicators,
    )

    if candle_fig is not None:

        st.plotly_chart(
            candle_fig,
            width="stretch",
        )

    st.markdown(
        "### 📘 Pattern Guide"
    )

    st.info(
        "Bullish Engulfing and Hammer can indicate potential bullish reversal. "
        "Bearish Engulfing and Shooting Star can indicate potential bearish reversal. "
        "Doji indicates indecision and should be confirmed using trend, momentum and volume."
    )


# ============================================================
# TAB 7 — TRADE SETUP
# ============================================================

with tabs[6]:

    st.markdown(
        f"## 💰 {strategy_mode} Trade Setup"
    )

    show_recommendation_card(
        signal_data,
        trade_plan,
        strategy_mode,
    )

    st.markdown(
        "### 📊 Detailed Trade Levels"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Current Price",
            fmt(current_price),
        )

    with c2:
        st.metric(
            "Zone Low",
            fmt(
                trade_plan["zone_low"]
            ),
        )

    with c3:
        st.metric(
            "Zone High",
            fmt(
                trade_plan["zone_high"]
            ),
        )

    with c4:
        st.metric(
            "Entry Trigger",
            fmt(
                trade_plan["entry"]
            ),
        )

    c5, c6, c7 = st.columns(3)

    with c5:
        st.metric(
            "Stop Loss",
            fmt(
                trade_plan["stop_loss"]
            ),
        )

    with c6:
        st.metric(
            "Target 1",
            fmt(
                trade_plan["target1"]
            ),
        )

    with c7:
        st.metric(
            "Target 2",
            fmt(
                trade_plan["target2"]
            ),
        )

    st.markdown(
        "### 📐 Risk Management"
    )

    r1, r2, r3 = st.columns(3)

    with r1:
        st.metric(
            "Direction",
            trade_plan["direction"],
        )

    with r2:
        st.metric(
            "ATR",
            fmt(
                trade_plan["atr"]
            ),
        )

    with r3:
        st.metric(
            "Target R:R",
            f"1:{fmt(trade_plan['rr'], 1)}",
        )

    st.markdown(
        "### 📝 How to Execute"
    )

    if signal_data["signal"] in [
        "STRONG BUY",
        "BUY",
    ]:

        st.markdown(
            f"""
            <div class="setup-box">

            <b>🟢 BUY PLAN</b><br><br>

            Current Price:
            <b>{fmt(current_price)}</b><br>

            Buy Zone:
            <b>
            {fmt(trade_plan["zone_low"])}
            – {fmt(trade_plan["zone_high"])}
            </b><br>

            Entry Trigger:
            <b>{fmt(trade_plan["entry"])}</b><br>

            Stop Loss:
            <b>{fmt(trade_plan["stop_loss"])}</b><br>

            Target 1:
            <b>{fmt(trade_plan["target1"])}</b><br>

            Target 2:
            <b>{fmt(trade_plan["target2"])}</b>

            <br><br>

            Enter only after price confirms the trigger.
            Use the stop loss without widening it emotionally.
            Consider booking partial profit at Target 1.

            </div>
            """,
            unsafe_allow_html=True,
        )

    elif signal_data["signal"] in [
        "STRONG SELL",
        "SELL",
    ]:

        st.markdown(
            f"""
            <div class="setup-box">

            <b>🔴 SELL / SHORT PLAN</b><br><br>

            Current Price:
            <b>{fmt(current_price)}</b><br>

            Sell Zone:
            <b>
            {fmt(trade_plan["zone_low"])}
            – {fmt(trade_plan["zone_high"])}
            </b><br>

            Sell Trigger:
            <b>{fmt(trade_plan["entry"])}</b><br>

            Stop Loss:
            <b>{fmt(trade_plan["stop_loss"])}</b><br>

            Target 1:
            <b>{fmt(trade_plan["target1"])}</b><br>

            Target 2:
            <b>{fmt(trade_plan["target2"])}</b>

            <br><br>

            Enter only after downside confirmation.
            Avoid shorting an already extended fall.
            Use the stop loss without widening it.

            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            """
            <div class="setup-box">

            <b>🟡 WAIT / HOLD PLAN</b><br><br>

            No high-confidence trade is currently detected.
            Wait for stronger alignment between trend, momentum,
            price action and volume before entering.

            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        "### 🔍 Confirmation"
    )

    st.info(
        signal_data["confirmation"]
    )

    st.markdown(
        "### 🧠 Recommendation Reasons"
    )

    for reason in signal_data["reasons"]:

        st.markdown(
            f"- {reason}"
        )

    if signal_data["warnings"]:

        st.markdown(
            "### ⚠️ Risk Warnings"
        )

        for warning in signal_data["warnings"]:

            st.warning(
                warning
            )


# ============================================================
# TAB 8 — INDICATOR GUIDE
# ============================================================

with tabs[7]:

    st.markdown(
        "## 📘 Technical Indicator Guide"
    )

    st.markdown(
        """
        Understand what each indicator means, how it is used,
        and how it contributes to the technical recommendation.
        """
    )

    guide_text = {

        "SMA 20":
            "20-period Simple Moving Average. Useful for short-term trend direction.",

        "SMA 50":
            "50-period Simple Moving Average. Useful for medium-term trend confirmation.",

        "EMA 20":
            "20-period Exponential Moving Average. Reacts faster to recent price changes.",

        "EMA 50":
            "50-period Exponential Moving Average. Useful for broader trend confirmation.",

        "Bollinger Bands":
            "Measures price volatility and identifies potentially extended price conditions.",

        "VWAP":
            "Volume Weighted Average Price. Especially useful for intraday price positioning.",

        "Supertrend":
            "Trend-following indicator used to identify bullish or bearish direction.",

        "RSI":
            "Relative Strength Index. Above 70 can indicate overbought conditions; below 30 can indicate oversold conditions.",

        "MACD":
            "Momentum and trend indicator. MACD above Signal generally supports bullish momentum.",

        "ATR":
            "Average True Range. Measures volatility and can help estimate stop-loss distance.",

        "Momentum":
            "Measures the rate of price movement. Positive momentum supports bullish conditions.",

        "Volume":
            "Shows trading activity. Higher-than-normal volume can strengthen price-move confirmation.",

        "Volume Ratio":
            "Compares current volume with average volume. Values above 1.5x indicate strong volume activity.",
    }

    for indicator in ALL_INDICATORS:

        with st.expander(
            f"📌 {indicator}",
            expanded=False,
        ):

            try:

                tooltip = get_indicator_tooltip(
                    indicator
                )

                if tooltip:

                    st.markdown(
                        tooltip
                    )

                else:

                    st.info(
                        guide_text.get(
                            indicator,
                            "Technical indicator used for market analysis.",
                        )
                    )

            except Exception:

                st.info(
                    guide_text.get(
                        indicator,
                        "Technical indicator used for market analysis.",
                    )
                )

    try:

        st.markdown(
            "### 📚 Complete Indicator Guide"
        )

        show_indicator_guide()

    except Exception:

        pass


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "⚠️ Technical analysis is probabilistic and is not a guarantee "
    "of future returns. Use appropriate position sizing, risk management "
    "and independent judgment. Entry, stop-loss and target levels are "
    "algorithmic estimates based on technical indicators and ATR."
)