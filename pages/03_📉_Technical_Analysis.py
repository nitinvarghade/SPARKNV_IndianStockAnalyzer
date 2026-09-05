# ============================================================
# pages/03_📉_Technical_Analysis.py
#
# Professional Technical Analysis Dashboard
#
# Features:
#   - Responsive device-friendly layout
#   - Heikin Ashi default
#   - Candlestick / OHLC / Line options
#   - Multiple indicators on same chart
#   - Favorite 1 / Favorite 2 / Favorite 3
#   - Intraday / Swing / Long Term strategy modes
#   - Technical score
#   - Strong Buy / Buy / Hold / Sell / Strong Sell
#   - Buy zone
#   - Buy trigger
#   - Stop loss
#   - Target 1 / Target 2
#   - Sell / exit conditions
#   - Indicator explanations
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from plotly.subplots import make_subplots

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

DEFAULT_INDICATORS = [
    "SMA 20",
    "SMA 50",
    "EMA 20",
    "EMA 50",
    "Bollinger Bands",
    "VWAP",
    "Supertrend",
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
    OVERLAY_INDICATORS
    + PANEL_INDICATORS
)


# ============================================================
# SESSION STATE
# ============================================================

if "technical_favorite_1" not in st.session_state:
    st.session_state["technical_favorite_1"] = DEFAULT_INDICATORS.copy()

if "technical_favorite_2" not in st.session_state:
    st.session_state["technical_favorite_2"] = []

if "technical_favorite_3" not in st.session_state:
    st.session_state["technical_favorite_3"] = []

if "technical_selected_indicators" not in st.session_state:
    st.session_state[
        "technical_selected_indicators"
    ] = DEFAULT_INDICATORS.copy()


# ============================================================
# PAGE HEADER
# ============================================================

page_header(
    "📉 Technical Analysis",
    CURRENT_PAGE,
)

show_page_navigation()


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
    """Convert indicator columns to numeric."""

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
    """Return latest non-null value."""

    if column not in df.columns:
        return None

    values = df[column].dropna()

    if values.empty:
        return None

    return float(values.iloc[-1])


def fmt(
    value,
    decimals=2,
):
    """Format numeric value."""

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
    """Format percentage."""

    if value is None:
        return "N/A"

    try:
        return f"{float(value):.2f}%"
    except Exception:
        return "N/A"


# ============================================================
# RESPONSIVE INDICATOR SUMMARY
# ============================================================

def show_indicator_chips(
    indicators,
):
    """
    Responsive indicator list.

    We intentionally don't use Plotly's large legend.
    This prevents indicator names from overlapping the
    chart title on smaller screens.
    """

    if not indicators:
        st.caption("No overlay indicators selected.")
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
# TECHNICAL SCORING
# ============================================================

def calculate_technical_signal(
    df: pd.DataFrame,
):
    """
    Calculate a technical-analysis score.

    This is a rule-based analytical score, not a
    guaranteed probability of future returns.
    """

    if df.empty:
        return {
            "score": 50,
            "signal": "HOLD",
            "reasons": [],
            "bullish_count": 0,
            "bearish_count": 0,
        }

    score = 50.0

    reasons = []

    bullish_count = 0
    bearish_count = 0

    close = latest_value(df, "Close")

    # --------------------------------------------------------
    # SMA
    # --------------------------------------------------------

    sma20 = latest_value(df, "SMA_20")
    sma50 = latest_value(df, "SMA_50")

    if close is not None and sma20 is not None:

        if close > sma20:

            score += 8
            bullish_count += 1

            reasons.append(
                "Price is above SMA 20, "
                "supporting short-term strength."
            )

        else:

            score -= 8
            bearish_count += 1

            reasons.append(
                "Price is below SMA 20, "
                "indicating short-term weakness."
            )

    if (
        sma20 is not None
        and sma50 is not None
    ):

        if sma20 > sma50:

            score += 10
            bullish_count += 1

            reasons.append(
                "SMA 20 is above SMA 50, "
                "supporting a bullish trend structure."
            )

        else:

            score -= 10
            bearish_count += 1

            reasons.append(
                "SMA 20 is below SMA 50, "
                "indicating a weaker trend structure."
            )

    # --------------------------------------------------------
    # EMA
    # --------------------------------------------------------

    ema20 = latest_value(df, "EMA_20")
    ema50 = latest_value(df, "EMA_50")

    if (
        ema20 is not None
        and ema50 is not None
    ):

        if ema20 > ema50:

            score += 8
            bullish_count += 1

            reasons.append(
                "EMA 20 is above EMA 50, "
                "supporting positive momentum."
            )

        else:

            score -= 8
            bearish_count += 1

            reasons.append(
                "EMA 20 is below EMA 50, "
                "indicating negative momentum."
            )

    # --------------------------------------------------------
    # VWAP
    # --------------------------------------------------------

    vwap = latest_value(
        df,
        "VWAP",
    )

    if (
        close is not None
        and vwap is not None
    ):

        if close > vwap:

            score += 8
            bullish_count += 1

            reasons.append(
                "Price is above VWAP."
            )

        else:

            score -= 8
            bearish_count += 1

            reasons.append(
                "Price is below VWAP."
            )

    # --------------------------------------------------------
    # SUPERTREND
    # --------------------------------------------------------

    supertrend = latest_value(
        df,
        "Supertrend",
    )

    if (
        close is not None
        and supertrend is not None
    ):

        if close > supertrend:

            score += 10
            bullish_count += 1

            reasons.append(
                "Price is above Supertrend, "
                "supporting a bullish trend."
            )

        else:

            score -= 10
            bearish_count += 1

            reasons.append(
                "Price is below Supertrend, "
                "supporting a bearish trend."
            )

    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------

    rsi = latest_value(
        df,
        "RSI",
    )

    if rsi is not None:

        if 50 <= rsi < 70:

            score += 7
            bullish_count += 1

            reasons.append(
                f"RSI is {rsi:.1f}, "
                "showing positive momentum without "
                "being extremely overbought."
            )

        elif rsi < 30:

            score += 4
            bullish_count += 1

            reasons.append(
                f"RSI is {rsi:.1f}, "
                "indicating an oversold condition."
            )

        elif rsi >= 70:

            score -= 4
            bearish_count += 1

            reasons.append(
                f"RSI is {rsi:.1f}, "
                "indicating an overbought condition."
            )

        else:

            score -= 2

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

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
        "MACD_Histogram",
    )

    if (
        macd is not None
        and macd_signal is not None
    ):

        if macd > macd_signal:

            score += 8
            bullish_count += 1

            reasons.append(
                "MACD is above its signal line."
            )

        else:

            score -= 8
            bearish_count += 1

            reasons.append(
                "MACD is below its signal line."
            )

    if macd_hist is not None:

        if macd_hist > 0:

            score += 4

        else:

            score -= 4

    # --------------------------------------------------------
    # BOLLINGER BANDS
    # --------------------------------------------------------

    bb_middle = latest_value(
        df,
        "BB_Middle",
    )

    bb_upper = latest_value(
        df,
        "BB_Upper",
    )

    bb_lower = latest_value(
        df,
        "BB_Lower",
    )

    if (
        close is not None
        and bb_middle is not None
    ):

        if close > bb_middle:

            score += 5
            bullish_count += 1

            reasons.append(
                "Price is above the Bollinger middle band."
            )

        else:

            score -= 5
            bearish_count += 1

            reasons.append(
                "Price is below the Bollinger middle band."
            )

    # --------------------------------------------------------
    # MOMENTUM
    # --------------------------------------------------------

    momentum = latest_value(
        df,
        "Momentum",
    )

    if momentum is not None:

        if momentum > 0:

            score += 5
            bullish_count += 1

            reasons.append(
                "Momentum is positive."
            )

        else:

            score -= 5
            bearish_count += 1

            reasons.append(
                "Momentum is negative."
            )

    # --------------------------------------------------------
    # VOLUME
    # --------------------------------------------------------

    volume_ratio = latest_value(
        df,
        "Volume_Ratio",
    )

    if volume_ratio is not None:

        if volume_ratio >= 1.5:

            if bullish_count >= bearish_count:

                score += 5

                reasons.append(
                    f"Volume is elevated at "
                    f"{volume_ratio:.2f}x the reference average."
                )

            else:

                score -= 5

                reasons.append(
                    f"High volume at "
                    f"{volume_ratio:.2f}x the reference average "
                    "is accompanying bearish pressure."
                )

    # --------------------------------------------------------
    # LIMIT SCORE
    # --------------------------------------------------------

    score = max(
        0,
        min(
            100,
            score,
        ),
    )

    # --------------------------------------------------------
    # SIGNAL
    # --------------------------------------------------------

    if score >= 75:

        signal = "STRONG BUY"

    elif score >= 60:

        signal = "BUY"

    elif score >= 45:

        signal = "HOLD"

    elif score >= 30:

        signal = "SELL"

    else:

        signal = "STRONG SELL"

    return {
        "score": round(score, 1),
        "signal": signal,
        "reasons": reasons,
        "bullish_count": bullish_count,
        "bearish_count": bearish_count,
    }


# ============================================================
# TRADE PLAN
# ============================================================

def calculate_trade_plan(
    df: pd.DataFrame,
    timeframe: str,
    signal_data: dict,
):
    """
    Calculate a rule-based trade plan.

    Intraday:
        tighter ATR stop and targets

    Swing:
        wider volatility allowance

    Long Term:
        wider risk allowance
    """

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

    # --------------------------------------------------------
    # ATR FALLBACK
    # --------------------------------------------------------

    if (
        atr is None
        or atr <= 0
    ):

        fallback = {
            "Intraday": 0.01,
            "Swing": 0.03,
            "Long Term": 0.06,
        }

        atr = close * fallback[
            timeframe
        ]

    # --------------------------------------------------------
    # TIMEFRAME PARAMETERS
    # --------------------------------------------------------

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

    cfg = settings[
        timeframe
    ]

    signal = signal_data[
        "signal"
    ]

    # --------------------------------------------------------
    # BULLISH PLAN
    # --------------------------------------------------------

    if signal in [
        "STRONG BUY",
        "BUY",
    ]:

        buy_trigger = (
            close
            + (
                atr
                * cfg["trigger_atr"]
            )
        )

        buy_zone_low = max(
            0,
            close - (
                atr
                * 0.25
            ),
        )

        buy_zone_high = (
            close
            + (
                atr
                * 0.10
            )
        )

        risk = (
            atr
            * cfg["stop_atr"]
        )

        stop_loss = (
            buy_trigger
            - risk
        )

        target1 = (
            buy_trigger
            + (
                risk
                * cfg["target1_rr"]
            )
        )

        target2 = (
            buy_trigger
            + (
                risk
                * cfg["target2_rr"]
            )
        )

        return {
            "direction": "LONG",
            "entry": buy_trigger,
            "buy_zone_low": buy_zone_low,
            "buy_zone_high": buy_zone_high,
            "stop_loss": stop_loss,
            "target1": target1,
            "target2": target2,
            "risk": risk,
            "reward1": target1 - buy_trigger,
            "reward2": target2 - buy_trigger,
            "entry_condition": (
                f"Consider entry only if price sustains "
                f"above ₹{buy_trigger:.2f} and bullish "
                "confirmation remains intact."
            ),
            "exit_condition": (
                f"Exit if price closes below the technical "
                f"stop around ₹{stop_loss:.2f}, or if the "
                f"bullish setup breaks."
            ),
        }

    # --------------------------------------------------------
    # BEARISH PLAN
    # --------------------------------------------------------

    if signal in [
        "STRONG SELL",
        "SELL",
    ]:

        sell_trigger = (
            close
            - (
                atr
                * cfg["trigger_atr"]
            )
        )

        sell_zone_low = (
            close
            - (
                atr
                * 0.10
            )
        )

        sell_zone_high = (
            close
            + (
                atr
                * 0.25
            )
        )

        risk = (
            atr
            * cfg["stop_atr"]
        )

        stop_loss = (
            sell_trigger
            + risk
        )

        target1 = (
            sell_trigger
            - (
                risk
                * cfg["target1_rr"]
            )
        )

        target2 = (
            sell_trigger
            - (
                risk
                * cfg["target2_rr"]
            )
        )

        return {
            "direction": "SHORT / EXIT",
            "entry": sell_trigger,
            "buy_zone_low": sell_zone_low,
            "buy_zone_high": sell_zone_high,
            "stop_loss": stop_loss,
            "target1": target1,
            "target2": target2,
            "risk": risk,
            "reward1": sell_trigger - target1,
            "reward2": sell_trigger - target2,
            "entry_condition": (
                f"Bearish setup confirmation is required "
                f"below ₹{sell_trigger:.2f}. "
                "For delivery investors this is primarily "
                "an exit/avoid-new-entry signal rather than "
                "a short-selling instruction."
            ),
            "exit_condition": (
                f"Exit/avoid the bearish trade if price "
                f"moves above approximately ₹{stop_loss:.2f} "
                "or the bearish structure reverses."
            ),
        }

    # --------------------------------------------------------
    # HOLD
    # --------------------------------------------------------

    return {
        "direction": "WAIT",
        "entry": close,
        "buy_zone_low": close - atr * 0.50,
        "buy_zone_high": close + atr * 0.50,
        "stop_loss": close - atr,
        "target1": close + atr * 1.5,
        "target2": close + atr * 2.5,
        "risk": atr,
        "reward1": atr * 1.5,
        "reward2": atr * 2.5,
        "entry_condition": (
            "Wait for a clearer bullish or bearish "
            "confirmation before taking a fresh position."
        ),
        "exit_condition": (
            "If already invested, review the position if "
            "trend indicators weaken or the defined risk "
            "level is breached."
        ),
    }


# ============================================================
# SIGNAL CARD
# ============================================================

def show_signal_card(
    signal_data,
    trade_plan,
    timeframe,
):
    """Render professional signal summary."""

    signal = signal_data["signal"]
    score = signal_data["score"]

    if signal == "STRONG BUY":

        st.success(
            f"🟢 STRONG BUY — Technical Score: {score:.0f}/100"
        )

    elif signal == "BUY":

        st.success(
            f"🟢 BUY — Technical Score: {score:.0f}/100"
        )

    elif signal == "HOLD":

        st.warning(
            f"🟡 HOLD — Technical Score: {score:.0f}/100"
        )

    elif signal == "SELL":

        st.warning(
            f"🟠 SELL — Technical Score: {score:.0f}/100"
        )

    else:

        st.error(
            f"🔴 STRONG SELL — Technical Score: {score:.0f}/100"
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    st.caption(
        f"Strategy timeframe: **{timeframe}**"
    )

    if trade_plan is None:
        return

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    c1, c2, c3, c4, c5 = st.columns(
        5,
        gap="small",
    )

    with c1:

        st.metric(
            "Buy / Trigger",
            f"₹{fmt(trade_plan['entry'])}",
        )

    with c2:

        st.metric(
            "Stop Loss",
            f"₹{fmt(trade_plan['stop_loss'])}",
        )

    with c3:

        st.metric(
            "Target 1",
            f"₹{fmt(trade_plan['target1'])}",
        )

    with c4:

        st.metric(
            "Target 2",
            f"₹{fmt(trade_plan['target2'])}",
        )

    with c5:

        risk_pct = (
            trade_plan["risk"]
            / trade_plan["entry"]
            * 100
        )

        st.metric(
            "Risk",
            f"{risk_pct:.2f}%",
        )

    # --------------------------------------------------------
    # Buy Zone
    # --------------------------------------------------------

    st.markdown(
        "### 🎯 Entry Zone"
    )

    z1, z2 = st.columns(
        2,
        gap="small",
    )

    with z1:

        st.metric(
            "Suggested Zone - Low",
            f"₹{fmt(trade_plan['buy_zone_low'])}",
        )

    with z2:

        st.metric(
            "Suggested Zone - High",
            f"₹{fmt(trade_plan['buy_zone_high'])}",
        )

    # --------------------------------------------------------
    # When to buy / sell
    # --------------------------------------------------------

    with st.container(border=True):

        st.markdown(
            "### 🕐 When to Buy / Exit"
        )

        st.write(
            "🟢 **Entry condition:** "
            + trade_plan["entry_condition"]
        )

        st.write(
            "🔴 **Exit / Sell condition:** "
            + trade_plan["exit_condition"]
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


if not isinstance(data, pd.DataFrame):

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

volume = latest_value(
    df,
    "Volume",
)


# ============================================================
# STRATEGY MODE
# ============================================================

st.subheader(
    "🎯 Trading / Investment Mode"
)


strategy_mode = st.radio(
    "Select analysis timeframe",
    [
        "Intraday",
        "Swing",
        "Long Term",
    ],
    horizontal=True,
    index=0,
    key="technical_strategy_mode",
    help=(
        "Intraday focuses on shorter-term setups, "
        "Swing focuses on multi-day setups, and "
        "Long Term focuses on broader trend positioning."
    ),
)


# ============================================================
# CHART SETTINGS
# ============================================================

st.subheader(
    "⚙️ Chart Settings"
)


settings1, settings2 = st.columns(
    2,
    gap="medium",
)


with settings1:

    graph_type = st.radio(
        "Price Pattern",
        [
            "Heikin Ashi",
            "Candlestick",
            "OHLC",
            "Line",
        ],
        horizontal=True,
        index=0,
        key="technical_graph_type",
        help=(
            "Heikin Ashi is the default. "
            "Candlestick and OHLC show actual market "
            "OHLC prices."
        ),
    )


with settings2:

    period = st.selectbox(
        "Chart Period",
        [
            "30 Days",
            "60 Days",
            "90 Days",
            "180 Days",
            "1 Year",
            "All Data",
        ],
        index=2,
        key="technical_period",
    )


chart_df = filter_period(
    df,
    period,
)


# ============================================================
# FAVORITES
# ============================================================

st.subheader(
    "⭐ Favorite Indicator Combinations"
)


fav1, fav2, fav3 = st.columns(
    3,
    gap="small",
)


with fav1:

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


with fav2:

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


with fav3:

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


# ============================================================
# MULTI INDICATOR SELECTION
# ============================================================

st.subheader(
    "📌 Multiple Technical Indicators"
)


selected_indicators = st.multiselect(
    "Select indicators",
    options=ALL_INDICATORS,
    key="technical_selected_indicators",
    help=(
        "Select multiple indicators. "
        "Overlay indicators appear on the price chart. "
        "Oscillators and volume indicators appear in "
        "their own panels."
    ),
)


# ============================================================
# SAVE FAVORITES
# ============================================================

save1, save2, save3 = st.columns(
    3,
    gap="small",
)


with save1:

    if st.button(
        "💾 Save as Favorite 1",
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
        "💾 Save as Favorite 2",
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
        "💾 Save as Favorite 3",
        width="stretch",
    ):

        st.session_state[
            "technical_favorite_3"
        ] = selected_indicators.copy()

        st.success(
            "Favorite 3 saved."
        )


# ============================================================
# RESPONSIVE SELECTED INDICATORS
# ============================================================

st.markdown(
    "#### Selected Indicators"
)

show_indicator_chips(
    selected_indicators
)


# ============================================================
# TECHNICAL SIGNAL
# ============================================================

signal_data = calculate_technical_signal(
    chart_df
)

trade_plan = calculate_trade_plan(
    chart_df,
    strategy_mode,
    signal_data,
)


st.subheader(
    "🤖 Technical Trading Signal"
)


show_signal_card(
    signal_data,
    trade_plan,
    strategy_mode,
)


# ============================================================
# REASONS
# ============================================================

st.markdown(
    "### 🔎 Why this signal?"
)


reasons = signal_data.get(
    "reasons",
    [],
)


if reasons:

    reason_container = st.container(
        border=True
    )

    with reason_container:

        for reason in reasons:

            st.write(
                "• " + reason
            )

else:

    st.info(
        "Not enough indicator information "
        "to explain the signal."
    )


# ============================================================
# BULLISH / BEARISH COUNT
# ============================================================

b1, b2, b3 = st.columns(
    3,
    gap="small",
)


with b1:

    st.metric(
        "Technical Score",
        f"{signal_data['score']:.0f}/100",
    )


with b2:

    st.metric(
        "Bullish Factors",
        signal_data[
            "bullish_count"
        ],
    )


with b3:

    st.metric(
        "Bearish Factors",
        signal_data[
            "bearish_count"
        ],
    )


# ============================================================
# ADDITIONAL PANEL OPTIONS
# ============================================================

st.subheader(
    "📊 Chart Panels"
)


panel1, panel2, panel3 = st.columns(
    3,
    gap="small",
)


with panel1:

    show_rsi = st.checkbox(
        "RSI",
        value=("RSI" in selected_indicators),
        key="show_rsi_panel",
        help=get_indicator_tooltip("RSI"),
    )


with panel2:

    show_macd = st.checkbox(
        "MACD",
        value=("MACD" in selected_indicators),
        key="show_macd_panel",
        help=get_indicator_tooltip("MACD"),
    )


with panel3:

    show_volume = st.checkbox(
        "Volume",
        value=("Volume" in selected_indicators),
        key="show_volume_panel",
        help=get_indicator_tooltip("Volume"),
    )


show_atr = (
    "ATR" in selected_indicators
)

show_momentum = (
    "Momentum" in selected_indicators
)

show_volume_ratio = (
    "Volume Ratio"
    in selected_indicators
)


# ============================================================
# PANEL LIST
# ============================================================

panel_names = [
    "Price"
]


if show_rsi:
    panel_names.append("RSI")


if show_macd:
    panel_names.append("MACD")


if show_atr:
    panel_names.append("ATR")


if show_momentum:
    panel_names.append("Momentum")


if show_volume:
    panel_names.append("Volume")


if show_volume_ratio:
    panel_names.append("Volume Ratio")


row_count = len(panel_names)


# ============================================================
# ROW HEIGHTS
# ============================================================

if row_count == 1:

    row_heights = [1.0]

else:

    row_heights = [
        0.50
    ]

    remaining = 0.50 / (
        row_count - 1
    )

    row_heights += [
        remaining
    ] * (
        row_count - 1
    )


# ============================================================
# SUBPLOTS
# ============================================================

fig = make_subplots(
    rows=row_count,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.025,
    row_heights=row_heights,
    subplot_titles=panel_names,
)


# ============================================================
# PRICE CHART
# ============================================================

if graph_type == "Heikin Ashi":

    fig.add_trace(
        go.Candlestick(
            x=chart_df.index,
            open=chart_df["HA_Open"],
            high=chart_df["HA_High"],
            low=chart_df["HA_Low"],
            close=chart_df["HA_Close"],
            name="Heikin Ashi",
            showlegend=False,
        ),
        row=1,
        col=1,
    )


elif graph_type == "Candlestick":

    fig.add_trace(
        go.Candlestick(
            x=chart_df.index,
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            name="Candlestick",
            showlegend=False,
        ),
        row=1,
        col=1,
    )


elif graph_type == "OHLC":

    fig.add_trace(
        go.Ohlc(
            x=chart_df.index,
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            name="OHLC",
            showlegend=False,
        ),
        row=1,
        col=1,
    )


else:

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["Close"],
            mode="lines",
            name="Close",
            showlegend=False,
        ),
        row=1,
        col=1,
    )


# ============================================================
# OVERLAY INDICATORS
# ============================================================

def add_line(
    column,
    name,
    row=1,
):

    if column not in chart_df.columns:
        return

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df[column],
            mode="lines",
            name=name,
            showlegend=False,
        ),
        row=row,
        col=1,
    )


for indicator in selected_indicators:

    if indicator == "SMA 20":

        add_line(
            "SMA_20",
            "SMA 20",
        )


    elif indicator == "SMA 50":

        add_line(
            "SMA_50",
            "SMA 50",
        )


    elif indicator == "EMA 20":

        add_line(
            "EMA_20",
            "EMA 20",
        )


    elif indicator == "EMA 50":

        add_line(
            "EMA_50",
            "EMA 50",
        )


    elif indicator == "VWAP":

        add_line(
            "VWAP",
            "VWAP",
        )


    elif indicator == "Supertrend":

        add_line(
            "Supertrend",
            "Supertrend",
        )


    elif indicator == "Bollinger Bands":

        add_line(
            "BB_Upper",
            "BB Upper",
        )

        add_line(
            "BB_Middle",
            "BB Middle",
        )

        add_line(
            "BB_Lower",
            "BB Lower",
        )


# ============================================================
# SECONDARY PANELS
# ============================================================

row = 1


# ------------------------------------------------------------
# RSI
# ------------------------------------------------------------

if show_rsi:

    row += 1

    if "RSI" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["RSI"],
                mode="lines",
                name="RSI",
                showlegend=False,
            ),
            row=row,
            col=1,
        )

        fig.add_hline(
            y=70,
            line_dash="dash",
            row=row,
            col=1,
        )

        fig.add_hline(
            y=50,
            line_dash="dot",
            row=row,
            col=1,
        )

        fig.add_hline(
            y=30,
            line_dash="dash",
            row=row,
            col=1,
        )

        fig.update_yaxes(
            range=[0, 100],
            title_text="RSI",
            automargin=True,
            row=row,
            col=1,
        )


# ------------------------------------------------------------
# MACD
# ------------------------------------------------------------

if show_macd:

    row += 1

    if "MACD" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["MACD"],
                mode="lines",
                name="MACD",
                showlegend=False,
            ),
            row=row,
            col=1,
        )


    if "MACD_Signal" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["MACD_Signal"],
                mode="lines",
                name="Signal",
                showlegend=False,
            ),
            row=row,
            col=1,
        )


    if "MACD_Histogram" in chart_df.columns:

        fig.add_trace(
            go.Bar(
                x=chart_df.index,
                y=chart_df["MACD_Histogram"],
                name="Histogram",
                showlegend=False,
            ),
            row=row,
            col=1,
        )


    fig.add_hline(
        y=0,
        line_dash="dot",
        row=row,
        col=1,
    )


    fig.update_yaxes(
        title_text="MACD",
        automargin=True,
        row=row,
        col=1,
    )


# ------------------------------------------------------------
# ATR
# ------------------------------------------------------------

if show_atr:

    row += 1

    if "ATR" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["ATR"],
                mode="lines",
                name="ATR",
                showlegend=False,
            ),
            row=row,
            col=1,
        )

    fig.update_yaxes(
        title_text="ATR",
        automargin=True,
        row=row,
        col=1,
    )


# ------------------------------------------------------------
# MOMENTUM
# ------------------------------------------------------------

if show_momentum:

    row += 1

    if "Momentum" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["Momentum"],
                mode="lines",
                name="Momentum",
                showlegend=False,
            ),
            row=row,
            col=1,
        )

    fig.add_hline(
        y=0,
        line_dash="dot",
        row=row,
        col=1,
    )

    fig.update_yaxes(
        title_text="Momentum",
        automargin=True,
        row=row,
        col=1,
    )


# ------------------------------------------------------------
# VOLUME
# ------------------------------------------------------------

if show_volume:

    row += 1

    if "Volume" in chart_df.columns:

        fig.add_trace(
            go.Bar(
                x=chart_df.index,
                y=chart_df["Volume"],
                name="Volume",
                showlegend=False,
            ),
            row=row,
            col=1,
        )

    fig.update_yaxes(
        title_text="Volume",
        automargin=True,
        row=row,
        col=1,
    )


# ------------------------------------------------------------
# VOLUME RATIO
# ------------------------------------------------------------

if show_volume_ratio:

    row += 1

    if "Volume_Ratio" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["Volume_Ratio"],
                mode="lines",
                name="Volume Ratio",
                showlegend=False,
            ),
            row=row,
            col=1,
        )

    fig.add_hline(
        y=1,
        line_dash="dot",
        row=row,
        col=1,
    )

    fig.update_yaxes(
        title_text="Volume Ratio",
        automargin=True,
        row=row,
        col=1,
    )


# ============================================================
# PROFESSIONAL RESPONSIVE CHART LAYOUT
# ============================================================

# Important:
# We intentionally hide Plotly's large legend.
# The responsive indicator chips above the chart replace it.

chart_height = max(
    650,
    460 + (
        row_count - 1
    ) * 190,
)


fig.update_layout(
    autosize=True,

    height=chart_height,

    showlegend=False,

    hovermode="x unified",

    margin=dict(
        l=55,
        r=25,
        t=55,
        b=45,
        pad=5,
        autoexpand=True,
    ),

    title=dict(
        text=(
            f"{stock.replace('.NS', '')} • "
            f"{strategy_mode} • "
            f"{graph_type}"
        ),
        x=0.01,
        xanchor="left",
        y=0.99,
        yanchor="top",
        automargin=True,
    ),

    font=dict(
        size=12,
    ),
)


# ------------------------------------------------------------
# Responsive axis margins
# ------------------------------------------------------------

fig.update_xaxes(
    automargin=True,
    showgrid=True,
)


fig.update_yaxes(
    automargin=True,
    showgrid=True,
)


# ============================================================
# MAIN CHART
# ============================================================

st.subheader(
    "📈 Price + Multiple Technical Indicators"
)


st.caption(
    "Hover over the chart for synchronized indicator values. "
    "Use the Plotly toolbar to zoom, pan and reset the chart."
)


st.plotly_chart(
    fig,
    width="stretch",
    config={
        "responsive": True,
        "displayModeBar": True,
        "displaylogo": False,
        "scrollZoom": True,
        "doubleClick": "reset",
        "showTips": True,
    },
)


# ============================================================
# CURRENT VALUES
# ============================================================

st.subheader(
    "📌 Current Indicator Values"
)


metric_items = [
    ("Close", "Close"),
    ("SMA 20", "SMA_20"),
    ("SMA 50", "SMA_50"),
    ("EMA 20", "EMA_20"),
    ("EMA 50", "EMA_50"),
    ("RSI", "RSI"),
    ("MACD", "MACD"),
    ("MACD Signal", "MACD_Signal"),
    ("VWAP", "VWAP"),
    ("Supertrend", "Supertrend"),
    ("ATR", "ATR"),
    ("Momentum", "Momentum"),
    ("Volume Ratio", "Volume_Ratio"),
]


available_metrics = [
    item
    for item in metric_items
    if item[1] in chart_df.columns
]


# Responsive metric rows:
# 4 on desktop-ish widths, naturally stacks on smaller screens.

for start in range(
    0,
    len(available_metrics),
    4,
):

    items = available_metrics[
        start:start + 4
    ]

    metric_cols = st.columns(
        len(items),
        gap="small",
    )

    for col, (
        label,
        column,
    ) in zip(
        metric_cols,
        items,
    ):

        value = latest_value(
            chart_df,
            column,
        )

        with col:

            st.metric(
                label,
                fmt(value),
                help=get_indicator_tooltip(
                    label
                ),
            )


# ============================================================
# FAVORITE SUMMARY
# ============================================================

with st.expander(
    "⭐ Saved Favorite Combinations"
):

    favorite1 = st.session_state.get(
        "technical_favorite_1",
        [],
    )

    favorite2 = st.session_state.get(
        "technical_favorite_2",
        [],
    )

    favorite3 = st.session_state.get(
        "technical_favorite_3",
        [],
    )

    st.markdown(
        "**Favorite 1:** "
        + (
            " • ".join(favorite1)
            if favorite1
            else "Empty"
        )
    )

    st.markdown(
        "**Favorite 2:** "
        + (
            " • ".join(favorite2)
            if favorite2
            else "Empty"
        )
    )

    st.markdown(
        "**Favorite 3:** "
        + (
            " • ".join(favorite3)
            if favorite3
            else "Empty"
        )
    )


# ============================================================
# INDICATOR GUIDE
# ============================================================

st.subheader(
    "📚 Technical Indicator Guide"
)


guide_keys = []


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


for indicator in selected_indicators:

    key = guide_mapping.get(
        indicator,
        indicator,
    )

    if key not in guide_keys:

        guide_keys.append(
            key
        )


for indicator in guide_keys:

    try:

        show_indicator_guide(
            st,
            indicator,
        )

    except Exception:

        with st.expander(
            f"ℹ️ {indicator}"
        ):

            st.write(
                get_indicator_tooltip(
                    indicator
                )
            )


# ============================================================
# RECENT MARKET DATA
# ============================================================

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
        )

    else:

        st.info(
            "No indicator data available."
        )


# ============================================================
# RISK / DISCLAIMER
# ============================================================

st.divider()


st.warning(
    "⚠️ **Technical-analysis disclaimer:** "
    "The Strong Buy / Buy / Hold / Sell / Strong Sell "
    "classification is a rule-based technical signal generated "
    "from the available indicators. It is not a guarantee of "
    "future returns. Buy zones, stop losses and targets are "
    "calculated reference levels and should be validated against "
    "current price action, liquidity, news, support/resistance "
    "and your own risk management."
)


st.caption(
    "Investment in securities market are subject to market risks. "
    "Read all the related documents carefully before investing."
)